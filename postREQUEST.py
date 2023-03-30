import os
import json
from bson.json_util import dumps
import sys
from pymongo import MongoClient


def record_creation(received_data, self):
    

    self.request.sendall(("HTTP/1.1 201 Created\r\nContent-Type: application/json\r\n\r\n"))
