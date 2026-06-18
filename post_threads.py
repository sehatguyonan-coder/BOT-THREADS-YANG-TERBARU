import os
import json
import time
import requests
import gspread
from datetime import datetime, timedelta
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

client = gspread.authorize(
    credentials
)

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
# MENCARI POSTING YANG SIAP DIPOSTING
# BERDASARKAN TANGGAL DAN JAM
# ==================================================

def get_pending_posts(worksheet):

    semua_data = worksheet.get_all_values()

    hasil = []

    sekarang = datetime.now() + timedelta(
        hours=7
    )


    for nomor_baris, row in enumerate(
        semua_data,
        start=1
    ):

        if nomor_baris == 1:
            continue


        try:

            status = row[1].strip().upper()

            tanggal = row[2].strip()

            jam = row[3].strip()            if status != "PENDING":

                continue


            if not tanggal or not jam:

                continue


            waktu_jadwal = datetime.strptime(
                f"{tanggal} {jam}",
                "%Y-%m-%d %H:%M"
            )


            if sekarang >= waktu_jadwal:

                hasil.append(
                    {
                        "baris": nomor_baris,
                        "data": row
                    }
                )


        except Exception as e:

            print(
                f"❌ Error membaca baris {nomor_baris}: {e}"
            )


    return hasil


# ==================================================
# MENGAMBIL DATA POSTING DARI GOOGLE SHEET
# ==================================================

def get_post_data(row):

    return {

        # Kolom K
        "caption": row[10].strip(),

        # Kolom E, G, I
        "media": [

            row[4].strip(),

            row[6].strip(),

            row[8].strip()

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


    if media_type == "VIDEO":

        payload["video_url"] = media_url


    elif media_type == "IMAGE":

        payload["image_url"] = media_url


    response = requests.post(
        url,
        data=payload
    )


    result = response.json()


    if "id" not in result:

        print(
            "❌ Gagal upload media:"
        )

        print(
            result
        )

        return None


    print(
        f"✅ Media berhasil dibuat: {result['id']}"
    )


    return result["id"]# ==================================================
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


        time.sleep(5)


# ==================================================
# MEMBUAT CAROUSEL DAN PUBLISH KE THREADS
# ==================================================

def publish_threads(
    access_token,
    user_id,
    caption,
    media_ids
):

    if len(media_ids) < 2:

        print(
            "❌ Carousel minimal harus memiliki 2 media"
        )

        return False


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

        print(
            result
        )

        return False


    creation_id = result["id"]


    print(
        f"✅ Carousel berhasil dibuat: {creation_id}"
    )


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
            f"🎉 BERHASIL POSTING: {result['id']}"
        )

        return True


    print(
        "❌ Gagal publish:"
    )

    print(
        result
    )


    return False


# ==================================================
# UPDATE STATUS POSTING DI GOOGLE SHEET
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


    print(
        "\n========================"
    )

    print(
        f"MEMPROSES AKUN: {username}"
    )

    print(
        "========================"
    )


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


            # Deteksi jenis file Dropbox
            if ".mp4" in media_url.lower():

                media_type = "VIDEO"


            elif ".png" in media_url.lower():

                media_type = "IMAGE"


            else:

                print(
                    f"❌ Format tidak dikenali: {media_url}"
                )

                continue


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


            # Video harus selesai diproses
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


        if len(media_ids) < 2:

            print(
                "❌ Tidak cukup media untuk membuat carousel"
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
