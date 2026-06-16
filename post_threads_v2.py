import csv
import os
import requests
from datetime import datetime, timedelta


# ======================================
# KONFIGURASI THREADS
# ======================================

TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
USER_ID = os.getenv("THREADS_USER_ID")

if not TOKEN:
    print("❌ THREADS_ACCESS_TOKEN tidak ditemukan")
    exit()

if not USER_ID:
    print("❌ THREADS_USER_ID tidak ditemukan")
    exit()

print("✅ Secret Threads terbaca")


# ======================================
# WAKTU SEKARANG WIB
# ======================================

sekarang = datetime.utcnow() + timedelta(hours=7)

print("Waktu WIB:", sekarang.strftime("%Y-%m-%d %H:%M"))


# ======================================
# BACA JADWAL CSV
# ======================================

with open(
    "jadwal.csv",
    "r",
    encoding="utf-8"
) as file:

    rows = list(csv.DictReader(file))


print("✅ Jadwal berhasil dibaca")


# ======================================
# CARI JADWAL PENDING
# ======================================

postingan = None
index_postingan = None


for index, row in enumerate(rows):

    status = row["STATUS"].strip().upper()


    if status != "PENDING":
        continue


    waktu_jadwal = datetime.strptime(
        row["TANGGAL"].strip()
        + " "
        + row["JAM"].strip(),
        "%Y-%m-%d %H:%M"
    )


    if sekarang >= waktu_jadwal:

        postingan = row
        index_postingan = index
        break


if postingan is None:

    print("⏳ Tidak ada posting yang harus dijalankan")
    exit()


print("🚀 Jadwal posting ditemukan")


# ======================================
# AMBIL CAPTION
# ======================================

caption = postingan["CAPTION"].strip()


# ======================================
# AMBIL SEMUA MEDIA
# ======================================

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


if not media_list:

    print("❌ Tidak ada media ditemukan")
    exit()


print("Jumlah media:", len(media_list))


# ======================================
# BUAT CHILD MEDIA CONTAINER
# ======================================

child_ids = []


for nomor, media in enumerate(
    media_list,
    start=1
):

    print(
        f"\n📤 Upload media {nomor}"
    )


    if ".mp4" in media.lower():

        media_type = "VIDEO"

    else:

        media_type = "IMAGE"


    url = (
        f"https://graph.threads.net/v1.0/"
        f"{USER_ID}/threads"
    )


    payload = {
        "media_type": media_type,
        "access_token": TOKEN
    }


    if media_type == "IMAGE":

        payload["image_url"] = media

    else:

        payload["video_url"] = media


    response = requests.post(
        url,
        data=payload
    )


    hasil = response.json()


    print("RESPONSE:")
    print(hasil)


    if "id" not in hasil:

        print("❌ Gagal membuat child container")
        exit()


    child_id = hasil["id"]


    child_ids.append(
        child_id
    )


    print(
        "✅ Child berhasil:",
        child_id
    )


print("\n✅ Semua child berhasil dibuat")


# ======================================
# BUAT CAROUSEL CONTAINER
# ======================================


print("\n🎠 Membuat Carousel")


url = (
    f"https://graph.threads.net/v1.0/"
    f"{USER_ID}/threads"
)


payload = {
    "media_type": "CAROUSEL",
    "children": ",".join(child_ids),
    "text": caption,
    "access_token": TOKEN
}


response = requests.post(
    url,
    data=payload
)


hasil = response.json()


print("RESPONSE CAROUSEL:")
print(hasil)


if "id" not in hasil:

    print("❌ Gagal membuat carousel")
    exit()


carousel_id = hasil["id"]


print(
    "✅ Carousel dibuat:",
    carousel_id
)


# ======================================
# PUBLISH CAROUSEL
# ======================================


print("\n🚀 Publish ke Threads")


url = (
    f"https://graph.threads.net/v1.0/"
    f"{USER_ID}/threads_publish"
)


response = requests.post(
    url,
    data={
        "creation_id": carousel_id,
        "access_token": TOKEN
    }
)


hasil = response.json()


print("RESPONSE PUBLISH:")
print(hasil)


if "id" not in hasil:

    print("❌ Publish gagal")
    exit()


thread_id = hasil["id"]


print("\n🎉 BERHASIL POST KE THREADS")
print(
    "THREAD ID:",
    thread_id
)


# ======================================
# UPDATE STATUS MENJADI POSTED
# ======================================


rows[index_postingan]["STATUS"] = "POSTED"


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
            "MEDIA1",
            "MEDIA2",
            "MEDIA3",
            "MEDIA4",
            "CAPTION"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)


print("✅ Status berubah menjadi POSTED")
