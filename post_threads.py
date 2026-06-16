import os
import json
import requests
import gspread

from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials


# ======================================
# KONFIGURASI THREADS
# ======================================

ACCESS_TOKEN = os.getenv(
    "THREADS_ACCESS_TOKEN"
)

USER_ID = os.getenv(
    "THREADS_USER_ID"
)


if not ACCESS_TOKEN:
    print(
        "❌ THREADS_ACCESS_TOKEN tidak ditemukan"
    )
    exit()


if not USER_ID:
    print(
        "❌ THREADS_USER_ID tidak ditemukan"
    )
    exit()


print(
    "✅ Secret Threads terbaca"
)


# ======================================
# KONFIGURASI GOOGLE SHEETS
# ======================================

GOOGLE_SHEET_ID = os.getenv(
    "GOOGLE_SHEET_ID"
)


GOOGLE_CREDENTIALS = os.getenv(
    "GOOGLE_CREDENTIALS"
)


if not GOOGLE_SHEET_ID:
    print(
        "❌ GOOGLE_SHEET_ID tidak ditemukan"
    )
    exit()


if not GOOGLE_CREDENTIALS:
    print(
        "❌ GOOGLE_CREDENTIALS tidak ditemukan"
    )
    exit()


print(
    "✅ Secret Google Sheets terbaca"
)


# ======================================
# LOGIN GOOGLE SHEETS
# ======================================


credentials_info = json.loads(
    GOOGLE_CREDENTIALS
)


scope = [
    "https://www.googleapis.com/auth/spreadsheets"
]


credentials = (
    Credentials.from_service_account_info(
        credentials_info,
        scopes=scope
    )
)


client = gspread.authorize(
    credentials
)


sheet = client.open_by_key(
    GOOGLE_SHEET_ID
)


worksheet = sheet.sheet1


print(
    "✅ Berhasil terhubung ke Google Sheet"
)


# ======================================
# WAKTU SEKARANG WIB
# ======================================


sekarang = (
    datetime.utcnow()
    + timedelta(hours=7)
)


print(
    "Waktu WIB:",
    sekarang.strftime(
        "%Y-%m-%d %H:%M"
    )
)


# ======================================
# AMBIL DATA GOOGLE SHEET
# ======================================


rows = worksheet.get_all_records()


if not rows:

    print(
        "❌ Google Sheet kosong"
    )

    exit()


print(
    "✅ Data Google Sheet berhasil dibaca"
)


# ======================================
# CARI POSTING PENDING
# ======================================


posting = None

baris_sheet = None


for index, row in enumerate(
    rows,
    start=2
):

    status = str(
        row["STATUS"]
    ).strip().upper()


    if status != "PENDING":
        continue


    tanggal = str(
        row["TANGGAL"]
    ).strip()


    jam = str(
        row["JAM"]
    ).strip()


    waktu_jadwal = datetime.strptime(
        f"{tanggal} {jam}",
        "%Y-%m-%d %H:%M"
    )


    if sekarang >= waktu_jadwal:

        posting = row

        baris_sheet = index

        break


if posting is None:

    print(
        "⏳ Tidak ada posting yang dijalankan"
    )

    exit()


print(
    "🚀 Jadwal posting ditemukan"
)


# ======================================
# CAPTION
# ======================================


caption = str(
    posting["CAPTION"]
).strip()


print(
    "✅ Caption ditemukan"
)


# ======================================
# AMBIL MEDIA
# ======================================


media_list = []


for nomor in range(1, 4):

    url = str(
        posting.get(
            f"MEDIA{nomor}",
            ""
        )
    ).strip()


    tipe = str(
        posting.get(
            f"TYPE{nomor}",
            ""
        )
    ).strip().upper()


    if url:

        media_list.append(
            {
                "url": url,
                "type": tipe
            }
        )


if not media_list:

    print(
        "❌ Tidak ada media ditemukan"
    )

    exit()


print(
    f"📁 Jumlah media: {len(media_list)}"
)
# ======================================
# UPLOAD CHILD MEDIA CONTAINER
# ======================================


child_ids = []


for nomor, media in enumerate(
    media_list,
    start=1
):

    print(
        f"\n📤 Upload media {nomor}"
    )


    media_type = media["type"]


    if media_type not in [
        "IMAGE",
        "VIDEO"
    ]:

        print(
            f"❌ TYPE media salah pada MEDIA{nomor}: {media_type}"
        )

        print(
            "Gunakan hanya IMAGE atau VIDEO di Google Sheet"
        )

        exit()


    url = (
        f"https://graph.threads.net/v1.0/"
        f"{USER_ID}/threads"
    )


    payload = {
        "media_type": media_type,
        "access_token": ACCESS_TOKEN
    }


    # Jika gambar
    if media_type == "IMAGE":

        payload[
            "image_url"
        ] = media["url"]


    # Jika video
    else:

        payload[
            "video_url"
        ] = media["url"]


    response = requests.post(
        url,
        data=payload
    )


    hasil = response.json()


    print(
        "RESPONSE:",
        hasil
    )


    if "id" not in hasil:

        print(
            "❌ Gagal membuat child media"
        )

        print(
            "Cek kembali link media atau akses API"
        )

        exit()


    child_id = hasil["id"]


    child_ids.append(
        child_id
    )


    print(
        "✅ Child berhasil dibuat:"
    )

    print(
        child_id
    )


print(
    "\n================================"
)

print(
    "✅ Semua child media berhasil"
)

print(
    "Total media:",
    len(child_ids)
)

print(
    "================================"
)


# ======================================
# MEMBUAT CAROUSEL CONTAINER
# ======================================


print(
    "\n🎠 Membuat Carousel Container"
)


url = (
    f"https://graph.threads.net/v1.0/"
    f"{USER_ID}/threads"
)


payload = {
    "media_type": "CAROUSEL",
    "children": ",".join(
        child_ids
    ),
    "text": caption,
    "access_token": ACCESS_TOKEN
}


response = requests.post(
    url,
    data=payload
)


hasil = response.json()


print(
    "RESPONSE CAROUSEL:"
)

print(
    hasil
)


if "id" not in hasil:

    print(
        "❌ Gagal membuat Carousel Container"
    )

    exit()


carousel_id = hasil["id"]


print(
    "✅ Carousel berhasil dibuat"
)

print(
    "Carousel ID:",
    carousel_id
)
# ======================================
# PUBLISH CAROUSEL KE THREADS
# ======================================


print(
    "\n🚀 Publish Carousel ke Threads"
)


url = (
    f"https://graph.threads.net/v1.0/"
    f"{USER_ID}/threads_publish"
)


payload = {
    "creation_id": carousel_id,
    "access_token": ACCESS_TOKEN
}


response = requests.post(
    url,
    data=payload
)


hasil = response.json()


print(
    "RESPONSE PUBLISH:"
)

print(
    hasil
)


# ======================================
# CEK HASIL PUBLISH
# ======================================


if "id" not in hasil:

    print(
        "❌ Gagal Publish ke Threads"
    )

    exit()


thread_id = hasil["id"]


print(
    "\n================================"
)

print(
    "🎉 BERHASIL POST KE THREADS"
)

print(
    "THREAD ID:"
)

print(
    thread_id
)

print(
    "================================"
)


# ======================================
# UPDATE STATUS MENJADI POSTED
# ======================================


print(
    "\n📝 Mengubah STATUS menjadi POSTED"
)


# Kolom STATUS ada di kolom A
worksheet.update_cell(
    baris_sheet,
    1,
    "POSTED"
)


print(
    "✅ STATUS berhasil diubah menjadi POSTED"
)


# ======================================
# SELESAI
# ======================================


print(
    "\n================================"
)

print(
    "🤖 BOT THREADS CAROUSEL SELESAI"
)

print(
    "Siap menunggu jadwal berikutnya..."
)

print(
    "================================"
)
