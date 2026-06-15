import os
import csv
import requests
from datetime import datetime, timedelta


# ==================================
# AMBIL DATA DARI GITHUB SECRETS
# ==================================

ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
USER_ID = os.getenv("THREADS_USER_ID")


if not ACCESS_TOKEN:
    print("❌ THREADS_ACCESS_TOKEN tidak ditemukan")
    exit()

if not USER_ID:
    print("❌ THREADS_USER_ID tidak ditemukan")
    exit()


print("✅ Secret Threads terbaca")


# ==================================
# BACA JADWAL CSV
# ==================================

with open(
    "jadwal.csv",
    "r",
    encoding="utf-8"
) as file:

    jadwal = list(
        csv.DictReader(file)
    )


if len(jadwal) == 0:
    print("❌ jadwal.csv kosong")
    exit()


# ==================================
# CEK WAKTU SEKARANG
# ==================================

# ==================================
# UBAH WAKTU UTC GITHUB KE WIB
# ==================================

sekarang = datetime.utcnow() + timedelta(hours=7)

tanggal = sekarang.strftime("%Y-%m-%d")

jam = sekarang.strftime("%H:%M")


print("Tanggal sekarang:", tanggal)
print("Jam sekarang:", jam)


# ==================================
# CARI POSTING PENDING
# ==================================

posting = None


for row in jadwal:

    status = row["STATUS"].strip().upper()

    tanggal_post = row["TANGGAL"].strip()

    jam_post = row["JAM"].strip()


    if (
        status == "PENDING"
        and tanggal_post == tanggal
        and jam_post == jam
    ):

        posting = row

        break


if posting is None:
    print("⏳ Tidak ada posting yang sesuai jadwal")
    exit()


print("✅ Posting ditemukan")


# ==================================
# AMBIL MEDIA DAN CAPTION
# ==================================

MEDIA_URL = posting["MEDIA_URL"].strip()

CAPTION = posting["CAPTION"].strip()


print("MEDIA:")
print(MEDIA_URL)

print("CAPTION:")
print(CAPTION)


# ==================================
# CEK JENIS MEDIA
# ==================================

media_type = "IMAGE"


if ".mp4" in MEDIA_URL.lower():
    media_type = "VIDEO"


print("Media Type:", media_type)


# ==================================
# BUAT CONTAINER THREADS
# ==================================

create_url = (
    f"https://graph.threads.net/v1.0/{USER_ID}/threads"
)


payload = {
    "media_type": media_type,
    "text": CAPTION,
    "access_token": ACCESS_TOKEN
}


if media_type == "IMAGE":
    payload["image_url"] = MEDIA_URL

else:
    payload["video_url"] = MEDIA_URL


response = requests.post(
    create_url,
    data=payload
)


create_result = response.json()


print("CREATE RESPONSE:")
print(create_result)


if "id" not in create_result:
    print("❌ Gagal membuat draft Threads")
    exit()


CREATION_ID = create_result["id"]


# ==================================
# PUBLISH THREADS
# ==================================

publish_url = (
    f"https://graph.threads.net/v1.0/{USER_ID}/threads_publish"
)


response_publish = requests.post(
    publish_url,
    data={
        "creation_id": CREATION_ID,
        "access_token": ACCESS_TOKEN
    }
)


publish_result = response_publish.json()


print("PUBLISH RESPONSE:")
print(publish_result)


# ==================================
# HASIL AKHIR
# ==================================

if "id" in publish_result:

    print("================================")
    print("🎉 BERHASIL POST KE THREADS")
    print("POST ID:")
    print(publish_result["id"])
    print("================================")

else:

    print("================================")
    print("❌ GAGAL PUBLISH")
    print(publish_result)
    print("================================")
