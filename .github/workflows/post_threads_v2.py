import os
import csv
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
# WAKTU SEKARANG WIB
# ======================================

sekarang = datetime.utcnow() + timedelta(hours=7)

print("Waktu WIB:", sekarang.strftime("%Y-%m-%d %H:%M"))


# ======================================
# BACA FILE JADWAL V2
# ======================================

try:
    with open(
        "jadwal.csv",
        "r",
        encoding="utf-8"
    ) as file:

        jadwal = list(csv.DictReader(file))

except Exception as e:

    print("❌ Gagal membaca jadwal.csv")
    print(e)
    exit()


if not jadwal:

    print("❌ jadwal.csv kosong")
    exit()


print("✅ Jadwal berhasil dibaca")


# ======================================
# CARI POSTING PENDING
# ======================================

posting = None
index_posting = None


for index, row in enumerate(jadwal):

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

        posting = row
        index_posting = index
        break



if posting is None:

    print("⏳ Tidak ada posting yang harus dijalankan")
    exit()


print("================================")
print("🚀 JADWAL POSTING DITEMUKAN")
print("================================")


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

    link = posting[kolom].strip()


    if link:
        media_list.append(link)



print("Jumlah media:", len(media_list))


for nomor, media in enumerate(
    media_list,
    start=1
):

    print(f"MEDIA {nomor}:")
    print(media)



# ======================================
# TAMPILKAN CAPTION
# ======================================


caption = posting["CAPTION"].strip()


print("================================")
print("CAPTION:")
print(caption)
print("================================")


print("✅ TEST V2 BERHASIL")
