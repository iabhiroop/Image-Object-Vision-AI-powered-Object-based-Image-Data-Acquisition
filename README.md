# WebImageScraper-with-YOLO-based-Object-Detection-and-Sorting

This is a FastAPI application that uses a variety of libraries and tools to perform a variety of tasks. 

Libraries/Frameworks:
- FastApi
- Pika
- RabbitMQ
- Confluent_Kafka
- Apache Kafka
- Docker
- Pillow
- Selenium
- Cairosvg
- PyMongo
- Ultralytics
- Torch
- BeautifulSoup
- Standard libraries: json, shutil, requests, os, time, io, base64, threading


Uses:
- To scrape a large number of webpages to aquire images.
- Look for presence of specific objects in images (custom train yolov8 to find specific objects) from webpages.
- Categorize images based on what they contain. 

Summary of Application:
- Receives the list of urls.
- Scrape websites using Beautiful Soup/Selenium.
- Generate SVG images using CairoSVG and save as an image.
- Perform object detection using YOLO.
- Create directories for detected objects and save the images based on detected objects.
- Store a summary of result data in MongoDB.
 

