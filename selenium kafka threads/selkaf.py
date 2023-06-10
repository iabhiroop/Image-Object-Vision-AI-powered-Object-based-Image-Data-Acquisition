import threading
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic
import json
from fastapi import FastAPI,Response, Request, Form , BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import json
import shutil
import requests
import torch
import os, time, io
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import cairosvg
from pymongo import MongoClient
from ultralytics import YOLO

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

client = MongoClient("mongodb://abhi:abhi@localhost:27017")
database = client["imagedatabase"]
collection = database["imagelist"]
if collection.drop():
    collection = database["imagelist"]

zip_file_ready = False
path = '.\\images\\'
if not os.path.exists(path):
    os.makedirs(path)
path_all = '.\\images\\remaining'
if not os.path.exists(path_all):
    os.makedirs(path_all)
sr_path = '.\\images\\source'
if not os.path.exists(sr_path):
    os.makedirs(sr_path)

c = 0
cc = 0
start = 0

# Kafka configuration
bootstrap_servers = 'localhost:9092'
input_topic = 'images'
output_topic = 'yolov8'
sort_topic = "sorting"
topic_list = [input_topic,output_topic,sort_topic]
image_detection_threads = 2
image_result_threads = 3

count = 0
check = 0
# Lock object
lock = threading.Lock()

# Function to increment the count
def increment_count():
    global count
    with lock:
        count += 1
admin_conf = {'bootstrap.servers': 'localhost:9092'}
admin_client = AdminClient(admin_conf)
topics = {
    'yolov8': image_detection_threads,  # Number of partitions for topic 'yolo'
    'sorting': image_result_threads   # Number of partitions for topic 'sort'
}
topic_list = []
for topic,num_partitions in topics.items():
    topic_list.append(NewTopic(topic, num_partitions, 1))
# Create the topics
admin_client.create_topics(topic_list)
topic_metadata = admin_client.list_topics(timeout=10)
print([topic for topic in topic_metadata.topics])
    # Filter out internal topics (e.g., __consumer_offsets)
topics_to_delete = [topic for topic in topic_metadata.topics if not topic.startswith('__')]




def clear_topic():
    admin_conf = {'bootstrap.servers': 'localhost:9092'}
    admin_client = AdminClient(admin_conf)

    # Retrieve the list of topics
    topic_metadata = admin_client.list_topics(timeout=10)

    # Filter out internal topics (e.g., __consumer_offsets)
    topics_to_delete = [topic for topic in topic_metadata.topics if not topic.startswith('__')]
    if len(topics_to_delete) == 0:
        return
    # Delete each topic
    delete_results = admin_client.delete_topics(topics_to_delete)

    # Wait for the delete operation to complete for each topic
    for topic, result in delete_results.items():
        try:
            result.result()  # Wait for the deletion to complete
            print(f"Topic '{topic}' deleted successfully")
        except Exception as e:
            print(f"Failed to delete topic '{topic}': {e}")

def create_topic():
    admin_conf = {'bootstrap.servers': 'localhost:9092'}
    admin_client = AdminClient(admin_conf)

    # Define the topics and their corresponding number of partitions
    topics = {
        'yolov8': image_detection_threads,  # Number of partitions for topic 'yolo'
        'sorting': image_result_threads   # Number of partitions for topic 'sort'
    }

    # Create NewTopic objects for each topic
    topic_list = []
    for topic,num_partitions in topics.items():
        topic_list.append(NewTopic(topic, num_partitions, 1))
    # Create the topics
    admin_client.create_topics(topic_list)


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Remote("http://localhost:4444/wd/hub", options=chrome_options)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/",response_class=RedirectResponse)
async def process_list(background_tasks: BackgroundTasks,request: Request, items: str = Form(...)):
    global c,collection,database,collection,start
    if items:
        if ',' in items:
            item_list = items.split(',')
        else:
            item_list=[items,]
        c = 0
        start = time.time()
        background_tasks.add_task(generate_zip,item_list)
        return RedirectResponse(request.url_for('wait'), status_code=303)
    



@app.get("/processing")
async def wait(request: Request):
    if zip_file_ready:
        return templates.TemplateResponse("download.html", {"request": request})
    else:
        return templates.TemplateResponse("loading.html", {"request": request})

    
@app.get("/generate_zip")
async def generate_zip(item_list):
    start_all(item_list)
    documents = collection.find()
    with open(path + 'collection_data.json', 'w') as file:
        for document in documents:
            json.dump(document, file, default=lambda o: str(o))
            file.write('\n')
    client.close()
    zip_file_name = "images_result"
    shutil.make_archive(zip_file_name, "zip", path)
    end = time.time()
    print(end - start)
    print(count,check)
    global zip_file_ready
    zip_file_ready = True 



@app.get("/download_zip")
async def download_zip(response: Response):
    path_to_zip_file = "./images_result.zip"

    with open(path_to_zip_file, "rb") as file:
        contents = file.read()

    response.headers["Content-Disposition"] = "attachment; filename=downloaded_file.zip"
    response.headers["Content-Type"] = "application/zip"
    response.headers["Content-Length"] = str(len(contents))

    return Response(content=contents, media_type="application/zip")




def image_detect():
    consumer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'consumer_group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_conf)
    producer_conf = {'bootstrap.servers': bootstrap_servers}
    producer = Producer(producer_conf)
    consumer.subscribe([output_topic])

    def url_take(i, url):
        image_name = ("".join(ch for ch in url if ch.isalnum()))[:60]
        filename = f"{image_name}_{i}.jpg"
        mes = {}
        mes ["url"] = url
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                img_path = os.path.join(sr_path,filename)
                if url[-4:] == ".svg":
                    svg_path = os.path.join(sr_path,"sv.svg")
                    with open(svg_path, "wb") as f:
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, f)
                    png_data = cairosvg.svg2png(url=svg_path)
                    image = Image.open(io.BytesIO(png_data))
                    image = image.convert('RGB')
                    image.save(img_path, 'JPEG')
                    os.remove(svg_path)
                else:
                    with open(img_path, "wb") as f:
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, f)
                try:
                    img = Image.open(img_path)
                    mes["img"] = img_path
                    mes["file_name"] = image_name
                    mes["result"] = find_result(img)
                    return mes
                except Exception as e:
                    print(e)  
        except Exception as e:
            print(e)

    def find_result(mes):
        res={}
        # print("finding")
        model = YOLO('yolov8s.pt')
        results = model.predict(mes)
        result = results[0]
        for box in result.boxes:
            class_id = result.names[box.cls[0].item()]
            if class_id in res.keys():
                res[class_id]+=1
            else:
                res[class_id]=1
        # print(res)
        torch.cuda.empty_cache()
        return res
        # Consume messages from output_topic and perform processing

    try:
        while True: 
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print('Consumer error: {}'.format(msg.error()))
                continue
            # Process the message
            data = msg.value().decode('utf-8')
            
            message_value = json.loads(data)
            if message_value["url"] == "stop":
                break
            i,url = message_value["i"],message_value["url"]
            mes = url_take(i, url)
            if mes is None:
                continue
            mes["page"] = message_value["page"]
            next_data = json.dumps(mes)
            producer.produce(sort_topic, value=next_data.encode('utf-8'))
            producer.flush()

    except KeyboardInterrupt:
        pass
    finally:
        # Close the consumer to release resources
        consumer.close()
        # producer.close()



def image_result():
    consumer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'consumer_group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([sort_topic])
    def directory_handle(mes,re):
        for i in re:
            if (os.path.exists(path+i)==False):
                os.makedirs(path+i)
            try:
                with open(path+'/'+i+'/'+mes["file_name"], "wb") as f1, open(mes["img"], 'rb') as f2:
                    shutil.copyfileobj(f2, f1)
            except Exception as e:
                print(e)
    
    def result_process(mes):
        global check,c
        res = mes["result"]
        if len(res.keys())!=0:
            re = res.keys()
            directory_handle(mes,re)
        else:
            with open(path_all+'/'+mes["file_name"], "wb") as f1, open(mes["img"], 'rb') as f2:
                    shutil.copyfileobj(f2,f1)
        check +=1
        result = collection.insert_one(mes)
        if count <= check:
            time.sleep(5)
            if count == check:
                c = 1

    try:
        while c==0:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print('Consumer error: {}'.format(msg.error()))
                continue
            # Process the message
            data = msg.value().decode('utf-8')
            # print(data)
            message_value = json.loads(data)
            if message_value["url"] == "stop":
                consumer.close()
                break
            # try:
            if message_value == None:
                print("fail")
            else:
                result_process(message_value)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

def start_all(mesg):
    global count
    image_detection_threads = 2
    image_result_threads = 3
    producer_conf = {'bootstrap.servers': bootstrap_servers}
    producer = Producer(producer_conf)
    
   
    # Start the threads
    l=0
    threads_1 = []
    for _ in range(image_detection_threads):
        thread_1 = threading.Thread(target=image_detect)
        thread_1.start()
        threads_1.append(thread_1)

    threads_2 = []
    for _ in range(image_result_threads):

        thread_2 = threading.Thread(target=image_result)
        thread_2.start()
        threads_2.append(thread_2)

    for j in mesg:
        
        try:
            URL = j
            driver.get(URL)
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            img_urls = [i.get_attribute("src") for i in img_elements]
            img_urls = [i for i in img_urls if i != None and len(i)>0]
            img_urls = list(set(img_urls))
            count+=len(img_urls)
            for i, url in enumerate(img_urls):
                processed_data = {'i':i,"url":url,"page":j}
                json_data = json.dumps(processed_data)
                producer.produce(output_topic, value=json_data.encode('utf-8'))
                producer.flush()
        except Exception as e:
            print(e)


    else:
        
        for i in range(image_detection_threads):
            processed_data = {'i':"stop","url":"stop","page":"stop"}
            json_data = json.dumps(processed_data)
            producer.produce(output_topic, value=json_data.encode('utf-8'))
            producer.flush()

            
    for thread_1 in threads_1:
        thread_1.join()
        l+=1

    if l==2:
        message_value = {"url":"stop","page":"stop"}
        next_data = json.dumps(message_value)
        for i in range(image_result_threads):
            producer.produce(sort_topic, value=next_data.encode('utf-8'))
            producer.flush()

    for thread_2 in threads_2:
        thread_2.join()
        l+=1
    
    return