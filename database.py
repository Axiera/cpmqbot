import json
import requests

url = "https://cpmqbot-default-rtdb.europe-west1.firebasedatabase.app"

def get(*args):
    global url
    request_url = '' + url
    for i in args:
        request_url += "/" + i
    request_url += "/.json"
    return json.loads(requests.get(request_url).text)

def put(jsondict, *args):
    global url
    request_url = '' + url
    for i in args:
        request_url += "/" + i
    request_url += "/.json"
    requests.put(request_url, json=jsondict)

def post(jsondict, *args):
    global url
    request_url = '' + url
    for i in args:
        request_url += "/" + i
    request_url += "/.json"
    requests.post(request_url, json=jsondict)
