import csv
import os
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


print("\n✅ STEP 3 BERHASIL")
