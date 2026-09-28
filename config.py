import os

# Direktori dasar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File sumber data kontak bawaan (mencari current_sheet.csv di parent dir atau file lokal)
DEFAULT_DATA_PATHS = [
    os.path.join(BASE_DIR, "kontak_prioritas.csv"),
    os.path.join(BASE_DIR, "kontak.csv"),
    os.path.join(BASE_DIR, "kontak.xlsx"),
    os.path.abspath(os.path.join(BASE_DIR, "..", "current_sheet.csv")),
    os.path.abspath(os.path.join(BASE_DIR, "..", "Data_Ikhwan_MABA_Gugus_Grouped.xlsx")),
]

# File template pesan
TEMPLATE_FILE = os.path.join(BASE_DIR, "template_pesan.txt")

# File log riwayat pengiriman
LOG_FILE = os.path.join(BASE_DIR, "sent_log.csv")

# Waktu tunggu WhatsApp Desktop memuat jendela chat sebelum menekan tombol Enter (detik)
WHATSAPP_LOAD_DELAY = 4.0

# Jeda acak antar pesan (detik) ekstra aman untuk melindungi nomor WA Bisnis
MIN_DELAY_BETWEEN_CHATS = 18
MAX_DELAY_BETWEEN_CHATS = 28
