import os
import json
import server
from bson.json_util import dumps
import sys
from pymongo import MongoClient

# mongo_client = MongoClient("mongo")
# db = mongo_client["cse312"]
# logs_collection = db["logs"] #db.collection
# chatlogs_collection = db["userComment"] # user : comment collection

def getRESPONSE(request_path,databse, token, self):
    if request_path == "/hello":
        self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: 11\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nHello World").encode())
    
    elif request_path == "/hi":
        self.request.sendall(("HTTP/1.1 301 Moved Permanently\r\nContent-Length: 0\r\nLocation: /hello").encode())
    
    elif request_path == "/":
        cxrf = token
        html_file = open("index.html", "r").read()
        #sizeh = os.path.getsize("index.html")
        sizeinbyte = len(html_file)
        html_file = html_file.replace("{{TOKEN}}", '<input value="' +cxrf + '" name="xsrf_token" hidden>')
        html_file = html_file.replace("{{LOOP}}", databse)
        size = len(html_file)
        
        self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + str(size) + "\r\nContent-Type: text/html; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\n"+ html_file).encode() )

    elif request_path == "/style.css":
        css_file = open("style.css").read()
        #sizes = os.path.getsize("style.css")
        sizeinbyte = len(css_file)
        
        #print(css_file)
        temp = "HTTP/1.1 200 OK\r\nContent-Length: " + str(sizeinbyte) + "\r\nContent-Type: text/css; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\n" + css_file
        #print(temp)
        self.request.sendall(temp.encode())

    elif request_path == "/functions.js":
        js_file = open("functions.js").read()
        #sizef = os.path.getsize("functions.js")
        sizeinbyte = len(js_file)
        
        self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + str(sizeinbyte) + "\r\nContent-Type: text/javascript; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\n" + js_file).encode())
    
    elif request_path == "/image/flamingo.jpg":
        p = request_path[1:]
        images = open(p, "rb").read()
        #print(images)
        self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Type: image/jpg\r\nX-Content-Type-Options: nosniff\r\n\r\n".encode() + images))

    
    
    # elif "/image" in request_path:
    #     image_path = "/image"
    #     p = request_path[1:]
    #     # p = p[6:]
    #     # p = p.replace("/","")
    #     # p = image_path
    #     images = open(p, "rb").read()
    #     self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Type: image/jpg\r\nX-Content-Type-Options: nosniff\r\n\r\n".encode() + images))

    elif "/Uimages" in request_path:
        p = request_path[1:] 
        p = p.replace("/","")
        images = open(p, "rb").read()
        self.request.sendall((("HTTP/1.1 200 OK\r\nContent-Length: " + str(len(images)) + "\r\nContent-Type: image/jpeg\r\nX-Content-Type-Options: nosniff\r\n\r\n").encode() + images))

        #print(p)
        
        #print(images)

    
    
    

    else:
        text = "The request content does not exist"
        self.request.sendall(("HTTP/1.1 404 Not Found\r\nContent-Length: " + str(len(text)) + "\r\nContent-Type: text/plain\r\n\r\n" + text).encode())

