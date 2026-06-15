import os
import csv
import requests
from datetime import datetime


# ===============================
# AMBIL DATA DARI GITHUB SECRETS
# ===============================

ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")

USER_ID = os.getenv("THREADS_USER_ID")


# ===============================
# CEK TOKEN
# ===============================

if not ACCESS_TOKEN:
    print("❌ THREADS_ACCESS_TOKEN belum ada")
    exit()

if not USER_ID:
    print("❌ THREADS_USER_ID belum ada")
    exit()


print("✅ Secret Threads terbaca")


# ===============================
# AMBIL WAKTU SEKARANG
# ===============================

sekarang = datetime.now()

tanggal_sekarang = sekarang.strftime("%Y-%m-%d")

jam_sekarang = sekarang.strftime("%H:%M")
# ===============================
# BACA FILE JADWAL CSV
# ===============================

with open(
    "jadwal.csv",
    "r",
    encoding="utf-8"
) as file:

    data = list(
        csv.DictReader(file)
    )


print(
    "Total jadwal:",
    len(data)
)


# ===============================
# CARI POSTING YANG HARUS JALAN
# ===============================

posting = None


for row in data:

    status = row["STATUS"]

    tanggal = row["TANGGAL"]

    jam = row["JAM"]


    if (
        status == "PENDING"
        and tanggal == tanggal_sekarang
        and jam == jam_sekarang
    ):

        posting = row

        break


# ===============================
# JIKA TIDAK ADA JADWAL
# ===============================

if posting is None:

    print(
        "Tidak ada posting saat ini."
    )

    exit()


print(
    "Posting ditemukan:"
)

print(posting)
# ===============================
# AMBIL DATA POSTING
# ===============================

nama_file = posting["FILE"]

caption = posting["CAPTION"]

path_file = "media/" + nama_file


print("File:", path_file)

print("Caption:", caption)


# ===============================
# CEK FILE MEDIA ADA ATAU TIDAK
# ===============================

if not os.path.exists(path_file):

    print("❌ File media tidak ditemukan")

    exit()


print("✅ File media ditemukan")


# ===============================
# BUAT CONTAINER THREADS
# ===============================

url_container = (
    f"https://graph.threads.net/v1.0/{USER_ID}/threads"
)


data = {
    "media_type": "TEXT",
    "text": caption,
    "access_token": ACCESS_TOKEN
}


response = requests.post(
    url_container,
    data=data
)


hasil = response.json()


print("Respon Threads:")

print(hasil)
# ===============================
# CEK HASIL DARI THREADS
# ===============================

if "id" in hasil:

    print("================================")
    print("✅ KONEKSI THREADS BERHASIL")
    print("ID CONTAINER:")
    print(hasil["id"])
    print("================================")

else:

    print("================================")
    print("❌ GAGAL MEMBUAT POST")
    print("RESPON ERROR:")
    print(hasil)
    print("================================")

    exit()


print("Bot selesai dijalankan.")

print("Tanggal:", tanggal_sekarang)
print("Jam:", jam_sekarang)
