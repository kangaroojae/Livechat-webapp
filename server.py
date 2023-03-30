import socketserver
import getREQUEST
import sys
import postREQUEST
import secrets
from pymongo import MongoClient

# docker-compose up --build (start server)
# ctrl c (stop server)
# http://localhost:8080/
mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
logs_collection = db["logs"] #db.collection
chatlogs_collection = db["userComment"] # user : comment collection
image_counter_collection = db["count"] # counter to update the image name find_one and update_one
image_counter_collection.insert_one({"counter" : 0})



class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        #dictionary to parse key : value pair
        dict = {}
        
        xsrf = secrets.token_hex(10)

        received_data = self.request.recv(2048) # data get from server
        #.split("\r\n",1)
        # bytes of a request
        bytes = received_data
        separator = bytes.find(b'\r\n\r\n')
        bHeader = bytes[:separator]
        bBody = bytes[separator + 4:]
        data = bHeader.decode()
        print(data)

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

            getREQUEST.getRESPONSE(line[1], replace_html, xsrf, self)

        #POST REQUEST   
        elif request_type == "POST":

            contentLength = ""
            contentType = ""
            boundary = ""
            user = ""
            comment = ""
            counter = 0
            image = b''

            if line[1] == "/image-upload":
                PostHeader = bHeader.split(b'\r\n\r\n',1)[0]
                PostHeader = PostHeader.decode()
                PostBody = bBody
                
                # Parsing header
                for line in PostHeader.split("\r\n"):
                    if "Content-Length: " in line:
                        contentLength = line.split(" ")[1] # ex. 354
                    if "Content-Type: " in line:
                        contentType = line.split(" ")
                        boundary = contentType[2] # boundary=-----WebKitFormBoundary
                        boundary = boundary[9:] #----WebKitFormBoundary
                
                length_Body = len(bBody)
                encodedContentLength = contentLength.encode()
                print(encodedContentLength)
                encodedBoundary = boundary.encode()
                print(encodedBoundary)
                
                while length_Body < int(encodedContentLength):
                    bBody += self.request.recv(2048) #request more bytes
                    length_Body = len(bBody)
                Decoded_body = bBody.split(b'\r\n--' + encodedBoundary)
                user = Decoded_body[0].split(b'\r\n\r\n')[1].decode()
                comment = Decoded_body[1].split(b'\r\n\r\n')[1].decode()
                

                Arr_of_bytes = bBody.split(b'\r\n--' + encodedBoundary)
                print("here")
                imageLocation = Arr_of_bytes[2].split(b'\r\n\r\n',1)[1]
                print("1")
                if len(imageLocation) != 0:
                    
                    
                    print("ad")
                    count = image_counter_collection.find_one({}, {"_id" : 0})
                    counter = count["counter"]
                    print("2")


                    chatlogs_collection.insert_one({"images" : "Uimages" + str(counter) + ".jpg"})
                    
                    print("3")
                    with open("Uimages" + str(counter) + ".jpg", "wb") as file:
                        file.write(imageLocation)
                        
                        print("4")
                    image_counter_collection.update_one({"counter" : counter}, {"$set" : {"counter" : counter + 1}})
                        
                        
                        
                print(user)
                print(comment)
                print("test")
            chatlogs_collection.insert_one({user : comment})
            
            self.request.sendall(("HTTP/1.1 302 Found\r\nContent-Length: 0\r\nLocation:http://localhost:8080/").encode())


        print("\n")
        sys.stdout.flush()
        sys.stderr.flush()



if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()