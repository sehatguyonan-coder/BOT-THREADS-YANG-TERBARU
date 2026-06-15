import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials


# ===============================
# AMBIL DATA DARI GITHUB SECRETS
# ===============================

ACCESS_TOKEN = os.getenv(
    "THREADS_ACCESS_TOKEN"
)

USER_ID = os.getenv(
    "THREADS_USER_ID"
)

GOOGLE_JSON = os.getenv(
    "GOOGLE_CREDENTIALS"
)

SHEET_ID = os.getenv(
    "GOOGLE_SHEET_ID"
)


# ===============================
# KONEKSI KE GOOGLE SHEETS
# ===============================

credentials_dict = json.loads(
    GOOGLE_JSON
)

scope = [
    "https://www.googleapis.com/auth/spreadsheets"
]

credentials = Credentials.from_service_account_info(
    credentials_dict,
    scopes=scope
)

client = gspread.authorize(
    credentials
)

sheet = client.open_by_key(
    SHEET_ID
).sheet1
