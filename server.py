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
import bcrypt


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
users_collection = db["users"] # stores user information



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
        not_signed = "You are not signed in yet"
        
        replace_html = ""
        #GET REQUEST
        if request_type == "GET":
            strings = received_data.decode()
            request_body = strings.split("\r\n") 
            keys = ""
            auth_token = ""
            hashToken = ""
            for lines in request_body:
                    if "Sec-WebSocket-Key:" in lines:
                        keys = lines.split(" ")[1]

                    
            print(keys.encode()) 

            
                        
                
            getREQUEST.getRESPONSE(line[1], replace_html, keys,data,auth_token, self)

        elif request_type == "POST":
            post_data = bBody.decode()
            post_data = post_data.split('&')
            
            if line[1] == "/register":
                username = post_data[0].split('=')[1]
                password = post_data[1].split('=')[1]
                salty = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password.encode(), salty)
                users_collection.insert_one({"username": username, "password": hashed_password, "salt": salty})
                self.request.sendall(("HTTP/1.1 301 Moved Permanently\r\nContent-Length: 0\r\nLocation: http://localhost:8080/").encode())

            elif line[1] == "/login":
                username = post_data[0].split('=')[1]
                password = post_data[1].split('=')[1]
                user = users_collection.find_one({"username": username})
                if user and bcrypt.checkpw(password.encode(), user["password"]):
                    token = secrets.token_hex(16)
                    hashed_token = hashlib.sha256(token.encode()).hexdigest()
                    users_collection.update_one({"username": username}, {"$set": {"auth_token": hashed_token}})
                    cookie = "auth_token={}; HttpOnly; Max-Age={}".format(token, 3600)
                    self.request.sendall(("HTTP/1.1 301 Moved Permanently\r\nSet-Cookie: {}\r\nContent-Length: 0\r\nLocation: http://localhost:8080/".format(cookie)).encode())

                else:
                    self.request.sendall(("HTTP/1.1 401 Unauthorized\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE html><html><head><title>Error</title></head><body><h1>Unauthorized</h1><p>You are not authorized to access this page.</p></body></html>").encode())

        print("\n")
        sys.stdout.flush()
        sys.stderr.flush()

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()