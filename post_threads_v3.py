import os
import json
import requests
import gspread

from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials


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
# KONFIGURASI GOOGLE SHEET
# ======================================

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")


if not SHEET_ID:
    print("❌ GOOGLE_SHEET_ID tidak ditemukan")
    exit()


print("✅ Google Sheet ID terbaca")


# ======================================
# KONEKSI GOOGLE SHEETS
# ======================================

scope = [
    "https://www.googleapis.com/auth/spreadsheets"
]


credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scope
)


client = gspread.authorize(credentials)


sheet = client.open_by_key(SHEET_ID)


worksheet = sheet.sheet1


print("✅ Berhasil terhubung ke Google Sheet")


# ======================================
# WAKTU SEKARANG WIB
# ======================================

sekarang = datetime.utcnow() + timedelta(hours=7)


print(
    "Waktu WIB:",
    sekarang.strftime("%Y-%m-%d %H:%M")
)


# ======================================
# BACA SEMUA DATA GOOGLE SHEET
# ======================================


rows = worksheet.get_all_records()


print(
    "✅ Data Google Sheet berhasil dibaca"
)


# ======================================
# CARI POSTING PENDING
# ======================================


postingan = None
baris_sheet = None


for index, row in enumerate(rows, start=2):

    status = str(
        row["STATUS"]
    ).strip().upper()


    if status != "PENDING":
        continue


    waktu_jadwal = datetime.strptime(
        str(row["TANGGAL"]).strip()
        + " "
        + str(row["JAM"]).strip(),
        "%Y-%m-%d %H:%M"
    )


    if sekarang >= waktu_jadwal:

        postingan = row

        baris_sheet = index

        break


if not postingan:

    print(
        "⏳ Tidak ada posting yang dijalankan"
    )

    exit()


print(
    "🚀 Jadwal posting ditemukan"
)
