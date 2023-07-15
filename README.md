# WebImageScrapper-ObjectBased-Detect-Scrape-Store-Search

This is a FastAPI application that uses a variety of libraries and tools to perform a variety of tasks. 

## Libraries/Tools/Techniques:
|  |    |
|---------------------|-----------------|
| FastApi             |  Microservices       |
|  Confluent_Kafka    |    Apache Kafka      |
|Selenium |        RabbitMQ |
|  Pillow             |     Threading     |
|    Cairosvg      |    Containers  |
|    PyMongo        |        Inter-thread Communication    |
|      Ultralytics     | Concurrency   |
|  Torch|        Asynchronous Communication        |
| Pika |           Docker   |
|    BeautifulSoup  |                 |
|Standard libraries: json, shutil, requests, os, time, io, base64, threading|


## Uses:
- To scrape a large number of webpages to aquire images.
- Look for presence of specific objects in images (custom train yolov8 to find specific objects) from webpages.
- Categorize images based on what they contain and save them into directories for further use.
- Search and find images based on the objects in them.
- MongoDB database of images scraped and identified for easy reference.

## Summary of Application:
- Receives the list of urls.
- Scrape websites using Beautiful Soup/Selenium.
- Generate SVG images using CairoSVG and save as an image.
- Perform object detection using YOLO.
- Create directories for detected objects and save the images based on detected objects.
- Store a summary of result data in MongoDB.
 

## There are four different versions:

### Beautiful Soup to scrape websites

- Beautiful Soup is a library to extract data from HTML and XML files. It can be used to isolate the <img> tags in the webpages that are to be scraped. It works quickly as it does not render the page and only deals with static pages.
- This version uses beautiful soup to quicky scrape image data from urls. It may not work very well with dynamic webpages but it is efficient.

### Selenium to render the page and scrape all images.

- Selenium is tool for automating web browser testing. It can be used to automate the process of interacting with a web browser. This can be used to extract data from dynamic websites that would otherwise be difficult or impossible to scrape.
- This version uses selenium to render headless version of chrome to load urls and scrape images. Since the page has to load, it is slower than beautiful soup which takes html and xml.

### Docker and RabbitMQ to create a distributed application with Selenium.
- Docker is a platform to build, run, and share applications within containers. Containers are executable units of software that package up code and all its dependencies. This makes it more versatile when moving from one device to another and to implement microservices.
- RabbitMQ is a message broker software(AMQP). It provides a reliable and scalable way for communication. RabbitMQ can be used for communication between microservices. 
- This version uses selenium. Containers and RabbitMQ are used to create scalable microservices that communicate with each other using RabbitMQ. This is faster and more efficient when working with several urls dealing with hundreds of images. 

### Kafka threads to create a concurrent application with Selenium.
- Apache Kafka is a distributed streaming platform. Kafka is scalable and fault-tolerant. It can be use to create communication channels.
- Docker is used to generate the kafka server.
- Concurrency allows multiple tasks to be run simultaneously. Python threading library helps with the creation of multiple threads in a program.
- This version uses threading and kafka for inter-thread communication. It is easy to set up and scale as all the threading and communication is part of a single process.
