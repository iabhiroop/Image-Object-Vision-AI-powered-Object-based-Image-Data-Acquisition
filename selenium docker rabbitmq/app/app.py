from fastapi import FastAPI,Response, Request, Form , BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import json
import shutil
import base64
import os, time
import pika
from pymongo import MongoClient

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

client = MongoClient("mongodb://abhi:abhi@mongodb:27017")
database = client["imagedatabase"]
collection = database["imagelist"]
if collection.drop():
    collection = database["imagelist"]
# document = { 'images': 'Format - image<image_number>', 'results': 'list of objects found'}
# result = collection.insert_one(document)
 

# Global variable to track zip file status
zip_file_ready = False
path = './images/'
if not os.path.exists(path):
    os.makedirs(path)
path_all = './images/remaining'
if not os.path.exists(path_all):
    os.makedirs(path_all)
file_no = 1
c = 0
cc = 0
start = 0

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
        client = MongoClient("mongodb://abhi:abhi@mongodb:27017")
        database = client["imagedatabase"]
        collection = database["imagelist"]
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='URL')
        for i in item_list:
            mes={"url":i,}
            channel.basic_publish(exchange='', routing_key='URL', body=json.dumps(mes))
        background_tasks.add_task(generate_zip)
        return RedirectResponse(request.url_for('wait'), status_code=303)
    



@app.get("/processing")
async def wait(request: Request):
    if zip_file_ready:
        return templates.TemplateResponse("download.html", {"request": request})
    else:
        return templates.TemplateResponse("loading.html", {"request": request})

    
@app.get("/generate_zip")
async def generate_zip():
    result_process()
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



def directory_handle(mes,re):
    for i in re:
        if (os.path.exists(path+i)==False):
            os.makedirs(path+i)
        try:
            image_bytes_back = base64.b64decode(mes['img'])
            with open(path+'/'+i+'/'+mes["file_name"], "wb") as f:
                f.write(image_bytes_back)
        except Exception as e:
            print(e)



def result_process():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    queues = ["images", "Output"]
    for queue in queues:
        channel.queue_declare(queue=queue)
    

    def callback1(ch, method, properties, body):
        global c,file_no
        mes=json.loads(body)
        file_no += 1
        mes["file_name"] = "image" + str(file_no) + ".jpg"
        res = mes["result"]
        if len(res.keys())!=0:
            re= res.keys()
            directory_handle(mes,re)
        else:
            image_bytes_back = base64.b64decode(mes['img'])
            with open(path_all+'/'+mes["file_name"], "wb") as f:
                f.write(image_bytes_back)
        del mes["img"]
        print(mes)
        result = collection.insert_one(mes)
        c+=1
        if c==cc:
            channel.stop_consuming()
            channel.close()
            connection.close()
            return

    def callback2(ch, method, properties, body):
        global cc
        cc = int(body)

    channel.basic_consume(queue='images', on_message_callback=callback2, auto_ack=True)
    channel.basic_consume(queue='Output', on_message_callback=callback1, auto_ack=True)
    channel.start_consuming()


