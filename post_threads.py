import os
import requests

ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")

url = "https://graph.threads.net/v1.0/me"

params = {
    "fields": "id,username",
    "access_token": ACCESS_TOKEN
}

response = requests.get(url, params=params)

print(response.json())
