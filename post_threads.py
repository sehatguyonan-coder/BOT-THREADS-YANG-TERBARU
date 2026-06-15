import os
import csv
import requests
from datetime import datetime, timedelta


# ======================================
# KONFIGURASI THREADS
# ======================================

ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
USER_ID = os.getenv("THREADS_USER_ID")

if not ACCESS_TOKEN:
    print("❌ THREADS_ACCESS_TOKEN tidak ditemukan")
    exit()

if not USER_ID:
    print("❌ THREADS_USER_ID tidak ditemukan")
    exit()

print("✅ Secret Threads terbaca")


# ======================================
# WAKTU SEKARANG (WIB)
# ======================================

sekarang = datetime.utcnow() + timedelta(hours=7)

print("Waktu WIB:", sekarang.strftime("%Y-%m-%d %H:%M"))


# ======================================
# BACA JADWAL
# ======================================

with open(
    "jadwal.csv",
    "r",
    encoding="utf-8"
) as file:

    jadwal = list(csv.DictReader(file))


if not jadwal:
    print("❌ jadwal.csv kosong")
    exit()


# ======================================
# CARI POSTING YANG SUDAH WAKTUNYA
# ======================================

posting = None
index_posting = None

for index, row in enumerate(jadwal):

    status = row["STATUS"].strip().upper()

    if status != "PENDING":
        continue


    waktu_jadwal = datetime.strptime(
        row["TANGGAL"].strip() + " " +
        row["JAM"].strip(),
        "%Y-%m-%d %H:%M"
    )


    if sekarang >= waktu_jadwal:

        posting = row
        index_posting = index
        break


if posting is None:
    print("⏳ Tidak ada posting yang harus dijalankan")
    exit()


print("✅ Jadwal ditemukan")


# ======================================
# DATA POSTING
# ======================================

MEDIA_URL = posting["MEDIA_URL"].strip()
CAPTION = posting["CAPTION"].strip()


print("Media:")
print(MEDIA_URL)

print("Caption:")
print(CAPTION)


# ======================================
# CEK JENIS MEDIA
# ======================================

media_type = "IMAGE"

if ".mp4" in MEDIA_URL.lower():
    media_type = "VIDEO"


print("Jenis media:", media_type)


# ======================================
# BUAT CONTAINER THREADS
# ======================================

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
    print("❌ Gagal membuat media container")
    exit()


CREATION_ID = create_result["id"]


# ======================================
# PUBLISH THREADS
# ======================================

publish_url = (
    f"https://graph.threads.net/v1.0/{USER_ID}/threads_publish"
)


response = requests.post(
    publish_url,
    data={
        "creation_id": CREATION_ID,
        "access_token": ACCESS_TOKEN
    }
)


publish_result = response.json()


print("PUBLISH RESPONSE:")
print(publish_result)


# ======================================
# JIKA BERHASIL
# ======================================

if "id" in publish_result:

    print("================================")
    print("🎉 BERHASIL POST KE THREADS")
    print("POST ID:")
    print(publish_result["id"])
    print("================================")


    # Ubah status menjadi POSTED
    jadwal[index_posting]["STATUS"] = "POSTED"


    with open(
        "jadwal.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "STATUS",
                "TANGGAL",
                "JAM",
                "MEDIA_URL",
                "CAPTION"
            ]
        )

        writer.writeheader()
        writer.writerows(jadwal)


    print("✅ Status berubah menjadi POSTED")


else:

    print("================================")
    print("❌ GAGAL PUBLISH")
    print(publish_result)
    print("================================")
