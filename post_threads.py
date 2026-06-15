# ===============================
# AMBIL SEMUA DATA DARI SHEET
# ===============================

rows = sheet.get_all_records()


# Jika tidak ada data
if len(rows) == 0:
    print("Tidak ada data di Google Sheet")
    exit()


# ===============================
# CARI POSTING STATUS PENDING
# ===============================

postingan = None
baris_ke = None


for index, row in enumerate(rows, start=2):

    status = row["STATUS"]

    if status == "PENDING":
        postingan = row
        baris_ke = index
        break


# Jika tidak ditemukan PENDING
if postingan is None:
    print("Tidak ada posting yang siap upload")
    exit()


print("Posting ditemukan:")
print(postingan)
