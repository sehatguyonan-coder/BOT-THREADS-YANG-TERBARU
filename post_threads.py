import os
import json
import time
import requests
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials


# ==================================================
# KONFIGURASI GOOGLE SHEET
# ==================================================

GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]


# ==================================================
# LOGIN GOOGLE SHEET
# ==================================================

google_credentials = json.loads(
    os.environ["GOOGLE_CREDENTIALS"]
)

credentials = Credentials.from_service_account_info(
    google_credentials,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets"
    ]
)

client = gspread.authorize(credentials)

spreadsheet = client.open_by_key(
    GOOGLE_SHEET_ID
)


# ==================================================
# MEMBACA SEMUA AKUN THREADS
# DARI accounts.json
# ==================================================

def load_accounts():

    with open(
        "accounts.json",
        "r",
        encoding="utf-8"
    ) as file:

        accounts = json.load(file)

    print(
        "\n======================"
    )
    print(
        f"Total akun ditemukan: {len(accounts)}"
    )
    print(
        "======================"
    )

    for akun in accounts:

        print(
            f"✅ {akun['username']}"
        )

    return accounts


# ==================================================
# WAKTU SEKARANG
# ==================================================

def get_current_time():

    sekarang = datetime.now()

    tanggal = sekarang.strftime(
        "%Y-%m-%d"
    )

    jam = sekarang.strftime(
        "%H:%M"
    )

    return tanggal, jam


# ==================================================
# MENCARI POSTING YANG SIAP DIPOSTING
# DI SETIAP TAB AKUN
# ==================================================

def get_pending_posts(worksheet):

    semua_data = worksheet.get_all_values()

    hasil = []

    tanggal_sekarang, jam_sekarang = get_current_time()


    for nomor_baris, row in enumerate(
        semua_data,
        start=1
    ):

        if nomor_baris == 1:
            continue


        try:

            status = row[1].strip().upper()
            tanggal = row[2].strip()
            jam = row[3].strip()


            if (
                status == "PENDING"
                and tanggal == tanggal_sekarang
                and jam == jam_sekarang
            ):

                hasil.append(
                    {
                        "baris": nomor_baris,
                        "data": row
                    }
                )


        except Exception as e:

            print(
                f"Error membaca baris {nomor_baris}: {e}"
            )


    return hasil# ==================================================
# MENGAMBIL DATA POSTING DARI GOOGLE SHEET
# ==================================================

def get_post_data(row):

    return {
        "caption": row[4].strip(),

        "media": [
            row[5].strip(),
            row[7].strip(),
            row[9].strip()
        ]
    }


# ==================================================
# UPLOAD MEDIA KE THREADS
# ==================================================

def upload_media(
    access_token,
    user_id,
    media_url,
    media_type
):

    url = (
        f"https://graph.threads.net/v1.0/"
        f"{user_id}/threads"
    )


    payload = {
        "media_type": media_type,
        "image_url": None,
        "video_url": None,
        "access_token": access_token
    }


    if media_type == "IMAGE":

        payload["image_url"] = media_url


    elif media_type == "VIDEO":

        payload["video_url"] = media_url


    response = requests.post(
        url,
        data=payload
    )


    result = response.json()


    if "id" not in result:

        print(
            "❌ Gagal upload media:"
        )
        print(result)

        return None


    media_id = result["id"]


    print(
        f"✅ Media berhasil dibuat: {media_id}"
    )


    return media_id


# ==================================================
# CEK STATUS PROCESSING VIDEO
# ==================================================

def wait_until_ready(
    media_id,
    access_token
):

    url = (
        f"https://graph.threads.net/v1.0/"
        f"{media_id}"
    )


    while True:

        response = requests.get(
            url,
            params={
                "fields": "status",
                "access_token": access_token
            }
        )


        result = response.json()


        status = result.get(
            "status",
            ""
        )


        print(
            f"Status media: {status}"
        )


        if status == "FINISHED":

            return True


        if status == "ERROR":

            return False


        time.sleep(5)# ==================================================
# MEMBUAT DAN PUBLISH POST THREADS
# ==================================================

def publish_threads(
    access_token,
    user_id,
    caption,
    media_ids
):

    create_url = (
        f"https://graph.threads.net/v1.0/"
        f"{user_id}/threads"
    )


    payload = {
        "media_type": "CAROUSEL",
        "children": ",".join(media_ids),
        "text": caption,
        "access_token": access_token
    }


    response = requests.post(
        create_url,
        data=payload
    )


    result = response.json()


    if "id" not in result:

        print(
            "❌ Gagal membuat carousel:"
        )
        print(result)

        return False


    creation_id = result["id"]


    print(
        f"✅ Carousel dibuat: {creation_id}"
    )


    # ==========================================
    # PUBLISH KE THREADS
    # ==========================================

    publish_url = (
        f"https://graph.threads.net/v1.0/"
        f"{user_id}/threads_publish"
    )


    response = requests.post(
        publish_url,
        data={
            "creation_id": creation_id,
            "access_token": access_token
        }
    )


    result = response.json()


    if "id" in result:

        print(
            f"🎉 Berhasil posting: {result['id']}"
        )

        return True


    else:

        print(
            "❌ Gagal publish:"
        )

        print(result)

        return False


# ==================================================
# UBAH STATUS DI GOOGLE SHEET
# ==================================================

def update_status(
    worksheet,
    nomor_baris
):

    try:

        worksheet.update_cell(
            nomor_baris,
            2,
            "POSTED"
        )


        print(
            f"✅ Status baris {nomor_baris} diubah menjadi POSTED"
        )


    except Exception as e:

        print(
            f"❌ Gagal update status: {e}"
        )# ==================================================
# PROGRAM UTAMA
# ==================================================

accounts = load_accounts()


for account in accounts:

    username = account["username"]
    access_token = account["access_token"]
    user_id = account["user_id"]
    sheet_name = account["sheet"]


    print("\n========================")
    print(f"MEMPROSES AKUN: {username}")
    print("========================")


    try:

        worksheet = spreadsheet.worksheet(
            sheet_name
        )

    except Exception as e:

        print(
            f"❌ Tab Google Sheet tidak ditemukan: {sheet_name}"
        )

        continue


    posts = get_pending_posts(
        worksheet
    )


    if not posts:

        print(
            "⏰ Tidak ada posting sesuai jadwal"
        )

        continue


    print(
        f"📌 Ditemukan {len(posts)} posting siap upload"
    )


    for post in posts:

        baris_sheet = post["baris"]

        data = get_post_data(
            post["data"]
        )


        caption = data["caption"]
        media_urls = data["media"]


        media_ids = []


        for media_url in media_urls:

            if not media_url:

                continue


            if media_url.lower().endswith(
                ".mp4"
            ):

                media_type = "VIDEO"

            else:

                media_type = "IMAGE"


            print(
                f"📤 Upload {media_type}: {media_url}"
            )


            media_id = upload_media(
                access_token,
                user_id,
                media_url,
                media_type
            )


            if not media_id:

                continue


            if media_type == "VIDEO":

                ready = wait_until_ready(
                    media_id,
                    access_token
                )


                if not ready:

                    print(
                        "❌ Video gagal diproses"
                    )

                    continue


            media_ids.append(
                media_id
            )


        if not media_ids:

            print(
                "❌ Tidak ada media yang berhasil upload"
            )

            continue


        sukses = publish_threads(
            access_token,
            user_id,
            caption,
            media_ids
        )


        if sukses:

            update_status(
                worksheet,
                baris_sheet
            )


print(
    "\n========================"
)
print(
    "🎉 SEMUA AKUN SELESAI DIPROSES"
)
print(
    "========================"
)
