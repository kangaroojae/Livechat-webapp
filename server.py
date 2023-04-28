import socketserver
import getREQUEST
import sys
import postREQUEST
import secrets
from pymongo import MongoClient
import hashlib
import base64
import json
import html
import random
# docker-compose up --build (start server)
# ctrl c (stop server)
# http://localhost:8080/
mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
logs_collection = db["logs"] #db.collection
chatlogs_collection = db["userComment"] # user : comment collection
image_counter_collection = db["count"] # counter to update the image name find_one and update_one
image_counter_collection.insert_one({"counter" : 0})
chat_messages = db["chat_messages"] # stores user messages


class MyTCPHandler(socketserver.BaseRequestHandler):
    connections = set()
    def handle(self):
        #dictionary to parse key : value pair
        
        

        received_data = self.request.recv(2048) # data get from server
        #.split("\r\n",1)
        # bytes of a request
        
        bytess = received_data
        separator = bytess.find(b'\r\n\r\n')
        bHeader = bytess[:separator]
        bBody = bytess[separator + 4:]
        data = bHeader.decode()
        # print(data)

        #parsing data
        
        
        request_line = data.split("\r\n",1)[0]
        line = request_line.split(" ")
        request_type = line[0]
        
        replace_html = ""
        
        for listOfDict in chatlogs_collection.find({},{"_id": 0}):
            for log in listOfDict:
                users = log
                comments = listOfDict[log]
                if users != "images":
                    replace_html += users + ": " + comments + "<br/>"
                else:
                    replace_html += "<img src= " + comments +  "> <br/>"






        #GET REQUEST
        if request_type == "GET":
            strings = received_data.decode()
            request_body = strings.split("\r\n") 
            keys = ""
            for lines in request_body:
                    if "Sec-WebSocket-Key:" in lines:
                        keys = lines.split(" ")[1]
            print(keys.encode()) 
                        
                
            getREQUEST.getRESPONSE(line[1], replace_html, keys, self)

            


        print("\n")
        sys.stdout.flush()
        sys.stderr.flush()



if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()