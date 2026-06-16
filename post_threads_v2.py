import csv
import os
import requests
from datetime import datetime, timedelta


# ===============================
# WAKTU WIB
# ===============================

wib = datetime.utcnow() + timedelta(hours=7)

print("✅ Secret Threads terbaca")

token = os.getenv("THREADS_ACCESS_TOKEN")
user_id = os.getenv("THREADS_USER_ID")

if not token or not user_id:
    print("❌ Secret tidak ditemukan")
    exit()


print("Waktu WIB:", wib.strftime("%Y-%m-%d %H:%M"))


# ===============================
# BACA CSV
# ===============================

with open("jadwal.csv", "r", encoding="utf-8") as file:
    data = csv.DictReader(file)
    rows = list(data)


print("✅ Jadwal berhasil dibaca")


# ===============================
# CARI JADWAL PENDING
# ===============================

postingan = None

for row in rows:

    status = row["STATUS"].strip()

    tanggal = row["TANGGAL"].strip()
    jam = row["JAM"].strip()


    jadwal = datetime.strptime(
        f"{tanggal} {jam}",
        "%Y-%m-%d %H:%M"
    )


    if status == "PENDING" and wib >= jadwal:
        postingan = row
        break



if not postingan:
    print("⏳ Tidak ada posting yang harus dijalankan")
    exit()


print("\n🚀 JADWAL POSTING DITEMUKAN")


# ===============================
# AMBIL MEDIA
# ===============================

media_list = []


for kolom in [
    "MEDIA1",
    "MEDIA2",
    "MEDIA3",
    "MEDIA4"
]:

    link = postingan[kolom].strip()

    if link:
        media_list.append(link)



print("\nJumlah media:", len(media_list))


for i, media in enumerate(media_list, start=1):

    if ".mp4" in media.lower():
        jenis = "VIDEO"
    else:
        jenis = "IMAGE"


    print(
        f"""
MEDIA {i}
Jenis : {jenis}
Link  : {media}
"""
    )


# ===============================
# CAPTION
# ===============================


caption = postingan["CAPTION"]

print("CAPTION:")
print("================")
print(caption)
print("================")
# ===============================
# BUAT CHILD MEDIA CONTAINER
# ===============================

child_ids = []
for i, media in enumerate(media_list, start=1):

    if ".mp4" in media.lower():
        media_type = "VIDEO"
    else:
        media_type = "IMAGE"


    print(f"\n📤 Upload media {i}")

    url = (
        f"https://graph.threads.net/v1.0/{user_id}/threads"
    )


    payload = {
        "media_type": media_type,
        "image_url" if media_type == "IMAGE"
        else "video_url": media,
        "access_token": token
    }


    response = requests.post(
        url,
        data=payload
    )


    hasil = response.json()


    print("RESPONSE:")
    print(hasil)


    if "id" not in hasil:
        print("❌ Gagal membuat child media")
        exit()


    child_ids.append(hasil["id"])


    print(
        f"✅ Child ID {i}:",
        hasil["id"]
    )


print("\n========================")
print("SEMUA CHILD BERHASIL")
print("TOTAL CHILD:", len(child_ids))
print("========================")
# ===============================
# BUAT CAROUSEL CONTAINER
# ===============================

print("\n🎠 Membuat Carousel Container")


url = f"https://graph.threads.net/v1.0/{user_id}/threads"


payload = {
    "media_type": "CAROUSEL",
    "children": ",".join(child_ids),
    "text": caption,
    "access_token": token
}


response = requests.post(
    url,
    data=payload
)


hasil = response.json()


print("RESPONSE CAROUSEL:")
print(hasil)


if "id" not in hasil:
    print("❌ Gagal membuat Carousel Container")
    exit()


carousel_id = hasil["id"]


print("\n✅ Carousel Container berhasil dibuat")
print("Carousel ID:", carousel_id)
