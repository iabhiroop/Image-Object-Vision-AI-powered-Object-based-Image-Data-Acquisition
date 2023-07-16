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
 

## Versions:

#### Version 1 - Beautiful Soup to scrape websites

- Beautiful Soup library is used to extract images from URLs.
- The <img> tags in the webpages that are to be scraped are isolated and the source retrieved.
- It works quickly as it does not render the page and only deals with static pages.
- This version uses beautiful soup to quicky scrape image data from urls.
- It may not work very well with dynamic webpages but it is efficient with static webpages.

#### Version 2 - Selenium to render the page and scrape all images.

- Beautiful Soup is replaced with Selenium.
- It automates the process of interacting with a web browser.
- This can be used to extract data from dynamic websites that would otherwise be difficult or impossible to scrape with the html file.
- This version uses selenium to render headless version of chrome to load urls and scrape images.
- Since the page has to load, it is slower than beautiful soup which takes html and xml.

#### Version 3 - Docker and RabbitMQ to create a distributed application with Selenium.
- Microservices is implemented to create more scalable version to handle multiple URLs.
- This version uses Docker to create Containers. This makes it more versatile when moving from one device to another and to implement microservices.
- RabbitMQ is used for communication between microservices. 
- This version uses selenium. This is faster and more efficient when working with several urls dealing with hundreds of images. 

#### Version 4 - Kafka threads to create a concurrent application with Selenium.
- Concurency is implemented to create a single application.
- Apache Kafka server is created to host communication channels between the threads.
- Docker is used to generate the kafka server. Kafka is scalable and fault-tolerant.
- Python threading library is used to generate and run multiple threads in the program.
- This version uses threading and kafka for inter-thread communication. It is easy to set up and scale as all the threading and communication is part of a single process.
