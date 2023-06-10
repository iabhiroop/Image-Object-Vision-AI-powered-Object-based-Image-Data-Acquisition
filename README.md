# WebImageScraper-with-YOLO-based-Object-Detection-and-Sorting

This is a FastAPI application that uses a variety of libraries and tools to perform a variety of tasks. 

libraries and software:
- fastapi
- pika
- rabbitmq
- confluent_kafka
- Apache Kafka
- docker
- pillow
- selenium
- cairosvg
- pymongo
- yolov8
- torch
- BeautifulSoup
- Standard libraries: json, shutil, requests, os, time, io, base64, threading


Uses:
- To scrape a large number of webpages to aquire images.
- Look for presence of specific objects in images (custom train yolov8 to find specific objects) from webpages.
- categorize images based on what they contain. 

Summary of application:
- Receives the list of urls.
- Scrape websites using Beautiful Soup/Selenium.
- Save images and generate SVG images using CairoSVG.
- Perform object detection using YOLO.
- Sort data into directories based on detected objects.
- Store result data in MongoDB.
 
There are four different versions:

- The first version uses Beautiful Soup to scrape websites
Beautiful Soup is a powerful and easy-to-use library that can be used to extract data from a wide variety of HTML and XML documents. It creates a parse tree for parsed pages that can be used to extract data from HTML, which is useful for web scraping. It is a must-have tool for any Python developer who needs to work with web data.
This version uses beautiful soup to quicky scrape image data from urls. It may not work very well with dynamic webpages but is efficient.

- The second version uses Selenium to render the page and scrape all images.
Selenium is an open-source tool for automating web browser testing. It can be used to automate a wide range of tasks, such as functional testing, performance testing, and security testing. It allows you to automate the process of interacting with a web browser, which means you can use it to extract data from websites that would otherwise be difficult or impossible to scrape.
This version uses selenium to render headless version of chrome to load urls and scrape images. Since the page has to load, it is slower than beautiful soup which takes html and xml.

- The third version uses Docker and RabbitMQ to create a distributed application.
Docker is a software platform that allows you to build, run, and share applications within containers. Containers are lightweight, standalone, and executable units of software that package up code and all its dependencies so the application runs quickly and reliably from one computing environment to another.
RabbitMQ is an open-source message broker software that originally implemented the Advanced Message Queuing Protocol (AMQP). RabbitMQ is a popular choice for building microservices-based applications. It provides a reliable and scalable way for applications to communicate with each other. RabbitMQ can be used to decouple applications, improve performance, and make applications more resilient to failure.
This version uses selenium like the previous one. Containers and RabbitMQ are used to create scalable microservices that communicate with each other using RabbitMQ. This is faster and more efficient when working with several urls dealing with hundreds of images. 

- The fourth version uses Kafka threads to create a concurrent application.
Apache Kafka is an open-source distributed streaming platform. It is used by companies of all sizes to process and analyze streaming data. Kafka is designed to be highly scalable and fault-tolerant, making it a good choice for mission-critical applications.
Concurrency can be used to improve the performance of an application by allowing multiple tasks to run simultaneously. Python threading library allows the creation of multiple threads in a program.
This version uses threading and kafka for inter-thread communication. This is easier to set up and scale as it only requires the number of threads to be increased.
