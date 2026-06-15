import os
import requests

ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
USER_ID = os.getenv("THREADS_USER_ID")

MESSAGE = "Halo Threads! Ini posting otomatis dari GitHub Actions 🚀"

# Buat konten Threads
create_url = f"https://graph.threads.net/v1.0/{USER_ID}/threads"

create_data = {
    "media_type": "TEXT",
    "text": MESSAGE,
    "access_token": ACCESS_TOKEN
}

response = requests.post(create_url, data=create_data)
result = response.json()

print("Create response:")
print(result)

# Publish konten
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
    print("Gagal membuat draft Threads")
