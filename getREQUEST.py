import os
import json
from bson.json_util import dumps
import sys
from pymongo import MongoClient
import hashlib
import base64
import random
import html
from server import MyTCPHandler
from server import chat_messages

def getRESPONSE(request_path,databse,Accept_key, self):
    if request_path == "/hello":
        self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: 11\r\nContent-Type: text/plain; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\nHello World").encode())

    
    
    elif request_path == "/":
        
        html_file = open("index.html", "r").read()
        #sizeh = os.path.getsize("index.html")
        sizeinbyte = len(html_file)
        # html_file = html_file.replace("{{TOKEN}}", '<input value="' +cxrf + '" name="xsrf_token" hidden>')
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
    

    elif request_path == "/new-javascript.js":
        js_file = open("new-javascript.js", "r").read()
        sizef = os.path.getsize('new-javascript.js')
        sizeinbyte = len(js_file)
        self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + str(sizeinbyte + 3) + "\r\nContent-Type: text/javascript; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\n" + js_file).encode())
    


    # # HW3 LO1 code starts here
    elif "/websocket" in request_path:
        WebSocket_Accept = Accept_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        WebSocket_Accept = hashlib.sha1(WebSocket_Accept.encode())
        WebSocket_Accept = base64.b64encode(WebSocket_Accept.digest())
        WebSocket_Accept += "\r\n\r\n".encode()
        # print(WebSocket_Accept)
        self.request.sendall("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ".encode() + WebSocket_Accept)
        username = "User" + str(random.randint(0,1000))
        print(username)
        
        MyTCPHandler.connections.add(self)
        while True:
            data = self.request.recv(2)
            opcode = data[0] & 0b00001111
            payload_len = data[1] & 0b01111111

            if opcode == 0x08:
                break
            
            masking_key = self.request.recv(4)
            if payload_len < 126:
                payload_data = self.request.recv(payload_len)
            else:
                break

            unMask_payload_data = b''
            for i in range(len(payload_data)):
                unMasked_byte = payload_data[i] ^ masking_key[i % 4]
                unMask_payload_data += bytes([unMasked_byte])
            
            message_from_client = json.loads(unMask_payload_data.decode("utf-8"))
            print(MyTCPHandler.connections)
            if message_from_client["messageType"] == "chatMessage":
                form_message = {
                    "messageType": "chatMessage",
                    "username": username,
                    "comment": message_from_client["comment"].replace('&', "&amp;").replace('<',"&lt").replace('>',"&gt;")
                }
                chat_messages.insert_one({'username': form_message["username"], 'comment' : form_message["comment"]})
                
                length = len(json.dumps(form_message).encode())
                if length <= 125:
                    header = bytearray([0x81, length])
                final_frame = bytes(header) + json.dumps(form_message).encode()
                
                for each_client in MyTCPHandler.connections:
                    try:
                        each_client.request.sendall(final_frame)
                    except:
                        MyTCPHandler.connections.remove(each_client)
                
                
    elif "/chat-history" in request_path:
        messages = []
        for user_message in chat_messages.find({},{"_id":0}):
            messages.append(user_message)
        messages = json.dumps(messages).encode("utf-8")
        length_message = len(messages)
        self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + str(length_message) + "\r\nContent-Type: application/json; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\n").encode() + messages)
        
    

    else:
        text = "The request content does not exist"
        self.request.sendall(("HTTP/1.1 404 Not Found\r\nContent-Length: " + str(len(text)) + "\r\nContent-Type: text/plain\r\n\r\n" + text).encode())

