import requests
import shutil
import os 
import pika
from PIL import Image
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import cairosvg
import io
import base64

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Remote("http://selenium:4444/wd/hub", options=chrome_options)
c=0
def recieve():  
    connection = pika.BlockingConnection(pika.ConnectionParameters(heartbeat=0,host='rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='URL')
    
    channel.queue_declare(queue='YOLO')

    channel.queue_declare(queue='images')
    
    def callback(ch, method, properties, body):
        global c
        try:
            mes = json.loads(body)
            URL = mes["url"]
            driver.get(URL)
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            img_urls = [i.get_attribute("src") for i in img_elements]
            img_urls = [i for i in img_urls if i != None and len(i)>0]
            sr_path = os.getcwd()
            for i, url in enumerate(img_urls):
                filename = f"image_{i}.jpg"
                mes = {}
                mes ["url"] = URL
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
                            with Image.open(img_path) as test_image:
                                img_sz = test_image.size
                            c += 1
                            file = open(img_path,"rb")
                            mes["img"] = base64.b64encode(file.read()).decode()
                            file.close()
                            os.remove(img_path)
                            channel.basic_publish(exchange='', routing_key='YOLO', body=json.dumps(mes))
                            
                            print(mes.keys())
                        except Exception as e:
                            print(e)
                            c-=1
                            os.remove(img_path)
                            continue    
                except Exception as e:
                    print(e)
                    continue
                
                try:
                    status = channel.queue_declare(queue='URL')
                    if status.method.message_count == 0:
                        channel.basic_publish(exchange='', routing_key='images', body=str(c))
                except Exception as e:
                    print(e)
            # driver.close()
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(e)
            pass
    


    channel.basic_consume(queue='URL', on_message_callback=callback, auto_ack=False)
    channel.start_consuming()


while 1:
    recieve()
