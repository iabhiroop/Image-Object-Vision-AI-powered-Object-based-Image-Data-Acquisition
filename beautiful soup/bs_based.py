from fastapi import FastAPI,Response, Request, Form , BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import json
import shutil
import requests
from bs4 import BeautifulSoup
import os, io
from PIL import Image
import cairosvg
from pymongo import MongoClient
from ultralytics import YOLO


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

client = MongoClient("mongodb://abhi:abhi@localhost:27017")
database = client["imagedatabase"]
collection = database["imagelist"]
mes={}

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
        mes["urls"] = item_list
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
    url_take(mes)
    documents = collection.find()
    with open(path + 'collection_data.json', 'w') as file:
        for document in documents:
            json.dump(document, file, default=lambda o: str(o))
            file.write('\n')
    client.close()
    zip_file_name = "images_result"
    shutil.make_archive(zip_file_name, "zip", path)
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
            with open(path+'/'+i+'/'+mes["file_name"], "wb") as f1, open(mes["img"], 'rb') as f2:
                shutil.copyfileobj(f2, f1)
        except Exception as e:
            print(e)

def getdata(url):
    r = requests.get(url)
    return r.text
def scrape_image(URL):
    htmldata = getdata(URL) 
    soup = BeautifulSoup(htmldata, 'html.parser')
    src=[]
    images = soup.find_all('img')

    for item in images:
        try:
            if len(item['src'])>0:
                src.append(item['src'])
        except:
            pass
    return src

def url_take(mesg):
    for i in mesg["urls"]:
        URL = i
        img_urls = scrape_image(URL)
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
                    with Image.open(img_path) as test_image:
                        img_sz = test_image.size
                    mes["img"] = img_path
                    mes["result"] = find_result(img_path)
                    result_process(mes)
                    os.remove(img_path)
            except:
                pass


def find_result(mes):
    res={}
    model = YOLO('yolov8s.pt')
    results = model.predict(mes)
    result = results[0]
    for box in result.boxes:
        class_id = result.names[box.cls[0].item()]
        if class_id in res.keys():
            res[class_id]+=1
        else:
            res[class_id]=1
    return res

def result_process(mes):
    global file_no
    file_no += 1
    mes["file_name"] = "image" + str(file_no) + ".jpg"
    res = mes["result"]
    if len(res.keys())!=0:
        re= res.keys()
        directory_handle(mes,re)
    else:
        with open(path_all+'/'+mes["file_name"], "wb") as f1, open(mes["img"], 'rb') as f2:
                shutil.copyfileobj(f2,f1)
    result = collection.insert_one(mes)