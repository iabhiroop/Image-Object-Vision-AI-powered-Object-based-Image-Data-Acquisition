import pika
import json
from ultralytics import YOLO
import base64
from PIL import Image
import io

def find_result(img):
    res={}
    model = YOLO('yolov8s.pt')
    results = model.predict(img)
    result = results[0]
    for box in result.boxes:
        class_id = result.names[box.cls[0].item()]
        if class_id in res.keys():
            res[class_id]+=1
        else:
            res[class_id]=1
    print(res)
    return res

def recieve():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='YOLO')

    def callback(ch, method, properties, body):
        mes=json.loads(body)
        img=mes["img"]
        image_bytes_back = base64.b64decode(img)
        img = Image.open(io.BytesIO(image_bytes_back))
        res = find_result(img)
        channel.queue_declare(queue='Output')
        mes["result"] = res
        channel.basic_publish(exchange='', routing_key='Output', body=json.dumps(mes))


    channel.basic_consume(queue='YOLO', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

while 1:
    recieve()