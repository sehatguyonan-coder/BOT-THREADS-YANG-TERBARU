import os
import requests

ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
USER_ID = os.getenv("THREADS_USER_ID")

MESSAGE = "Ini posting gambar otomatis dari GitHub Actions 🚀"

IMAGE_URL = "https://raw.githubusercontent.com/sehatguyonan-coder/BOT-THREADS-YANG-TERBARU/main/15.png"


# 1. Buat media gambar
create_url = f"https://graph.threads.net/v1.0/{USER_ID}/threads"

create_data = {
    "media_type": "IMAGE",
    "image_url": IMAGE_URL,
    "text": MESSAGE,
    "access_token": ACCESS_TOKEN
}

response = requests.post(create_url, data=create_data)
result = response.json()

print("Create response:")
print(result)


# 2. Publish gambar
if "id" in result:
    creation_id = result["id"]

    publish_url = f"https://graph.threads.net/v1.0/{USER_ID}/threads_publish"

    publish_data = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }

    publish = requests.post(publish_url, data=publish_data)

    print("Publish response:")
    print(publish.json())

else:
    print("Gagal membuat posting gambar")
