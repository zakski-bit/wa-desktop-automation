"""
WA Mentoring Sender - Script Otomatisasi WhatsApp Desktop untuk Undangan Mentoring
"""

import os
import sys

# Konfigurasi encoding UTF-8 untuk terminal Windows (agar support emoji tanpa error charmap)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
import random
import urllib.parse
import re
import csv
from datetime import datetime

import config
import ctypes

user32 = ctypes.windll.user32
VK_RETURN = 0x0D
KEYEVENTF_KEYUP = 0x0002

# Coba import pyautogui jika tersedia
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

def ensure_default_desktop():
    """Memastikan thread terhubung ke desktop interaktif pengguna"""
    try:
        hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)
    except Exception:
        pass

def find_whatsapp_hwnd():
    """Mencari handle jendela WhatsApp Desktop yang aktif"""
    ensure_default_desktop()
    wa_hwnd = None
    from ctypes import wintypes
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    
    def foreach_window(hwnd, lParam):
        nonlocal wa_hwnd
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                if buff.value == "WhatsApp":
                    wa_hwnd = hwnd
                    return False
        return True

    user32.EnumWindows(WNDENUMPROC(foreach_window), 0)
    return wa_hwnd

def press_enter_native():
    """
    Fokuskan jendela WhatsApp Desktop ke paling depan lalu kirim tombol Enter 
    dengan scan code hardware (0x1C) agar 100% terbaca oleh aplikasi WhatsApp UWP.
    """
    ensure_default_desktop()
    
    # Cari dan fokuskan jendela WhatsApp
    hwnd = find_whatsapp_hwnd()
    if hwnd:
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.4)
        
    # Kirim tombol Enter dengan Scan Code 0x1C
    SCAN_CODE_ENTER = 0x1C
    KEYEVENTF_SCANCODE = 0x0008
    user32.keybd_event(VK_RETURN, SCAN_CODE_ENTER, 0, 0)
    time.sleep(0.08)
    user32.keybd_event(VK_RETURN, SCAN_CODE_ENTER, KEYEVENTF_KEYUP, 0)
    
    # Fallback tambahan jika pyautogui aktif
    if HAS_PYAUTOGUI:
        try:
            pyautogui.FAILSAFE = False
            pyautogui.press("enter")
        except Exception:
            pass


def normalize_phone(raw_phone):
    """
    Membersihkan dan menstandarkan format nomor HP ke format internasional: 628xxxxxxx
    Contoh:
    - 08123456789 -> 628123456789
    - 8123456789  -> 628123456789
    - +62 812-3456-789 -> 628123456789
    """
    if raw_phone is None:
        return None
    
    # Ubah ke string dan hilangkan trailing .0 jika terbaca dari float
    s = str(raw_phone).strip()
    if s.endswith(".0"):
        s = s[:-2]
        
    # Hapus semua karakter non-digit
    digits = re.sub(r"\D", "", s)
    
    if not digits:
        return None
        
    # Standardisasi ke format 62
    if digits.startswith("08"):
        digits = "628" + digits[2:]
    elif digits.startswith("8"):
        digits = "628" + digits[1:]
    elif digits.startswith("6208"):
        digits = "628" + digits[4:]
    elif not digits.startswith("62"):
        digits = "62" + digits

    # Validasi panjang nomor HP Indonesia (biasanya 10 - 15 digit setelah 62)
    if 10 <= len(digits) <= 15:
        return digits
    return None


def read_template(filepath=config.TEMPLATE_FILE):
    """Membaca isi template pesan dari file teks"""
    if not os.path.exists(filepath):
        print(f"[!] File template tidak ditemukan di {filepath}. Membuat template bawaan...")
        default_template = "Halo Kak {panggilan}, salam kenal dari Tim Mentor Gugus {gugus}!"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(default_template)
        return default_template
        
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


def format_message(template, row_data):
    """Mengganti placeholder {nama}, {panggilan}, {gugus}, {jurusan}, {prodi} dengan data penerima"""
    panggilan = str(row_data.get("panggilan", "")).strip()
    nama = str(row_data.get("nama", "")).strip()
    
    # Jika panggilan kosong, gunakan nama pertama dari nama lengkap
    if not panggilan or panggilan.lower() in ("nan", "none", "-"):
        if nama and nama.lower() not in ("nan", "none", "-"):
            panggilan = nama.split()[0]
        else:
            panggilan = "Kak"
            
    gugus = str(row_data.get("gugus", "")).strip()
    jurusan = str(row_data.get("jurusan", "")).strip()
    prodi = str(row_data.get("prodi", "")).strip()

    # Sanitasi teks nan / none
    gugus = "" if gugus.lower() in ("nan", "none") else gugus
    jurusan = "" if jurusan.lower() in ("nan", "none") else jurusan
    prodi = "" if prodi.lower() in ("nan", "none") else prodi

    params = {
        "panggilan": panggilan,
        "nama": nama if nama and nama.lower() not in ("nan", "none") else panggilan,
        "gugus": gugus,
        "jurusan": jurusan,
        "prodi": prodi
    }
    
    try:
        msg = template.format(**params)
    except KeyError:
        msg = template
        for k, v in params.items():
            msg = msg.replace(f"{{{k}}}", v)
            
    # Rapikan spasi ganda, pengulangan kata Gugus, atau tanda kurung kosong
    msg = re.sub(r"\b(Gugus|gugus)\s+(Gugus|gugus)\b", "Gugus", msg)
    msg = msg.replace("()", "").replace("( )", "").strip()
    return msg


def load_sent_log(log_path=config.LOG_FILE):
    """Membaca nomor-nomor yang sudah berhasil dikirimi pesan agar tidak dobel kirim"""
    sent_numbers = set()
    if not os.path.exists(log_path):
        return sent_numbers
        
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r.get("Status") == "BERHASIL" and r.get("Nomor_WA"):
                    sent_numbers.add(r["Nomor_WA"])
    except Exception as e:
        print(f"[!] Catatan: Tidak dapat membaca log lama ({e})")
    return sent_numbers


def append_sent_log(row_data, phone, status, log_path=config.LOG_FILE):
    """Mencatat hasil pengiriman pesan ke file log"""
    file_exists = os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Nama", "Panggilan", "Nomor_WA", "Gugus", "Jurusan", "Status"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            row_data.get("nama", "-"),
            row_data.get("panggilan", "-"),
            phone,
            row_data.get("gugus", "-"),
            row_data.get("jurusan", "-"),
            status
        ])


def find_data_file():
    """Mencari file data kontak yang ada di direktori kerja"""
    for p in config.DEFAULT_DATA_PATHS:
        if os.path.exists(p):
            return p
    return None


def read_csv_rows(filepath):
    """Membaca file CSV murni dengan modul bawaan Python csv"""
    rows = []
    with open(filepath, mode="r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def read_excel_rows(filepath):
    """Membaca file Excel .xlsx dengan modul openpyxl"""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(filepath, data_only=True)
        ws = wb.active
        raw_rows = list(ws.iter_rows(values_only=True))
        if not raw_rows:
            return []
            
        headers = [str(c or "").strip() for c in raw_rows[0]]
        dict_rows = []
        for row in raw_rows[1:]:
            row_dict = {}
            for col_idx, val in enumerate(row):
                if col_idx < len(headers):
                    row_dict[headers[col_idx]] = val
            dict_rows.append(row_dict)
        return dict_rows
    except ImportError:
        print("[!] Modul 'openpyxl' belum terpasang untuk membaca file .xlsx.")
        return []


def load_contacts(filepath):
    """Membaca file Excel atau CSV dan memetakan kolom-kolomnya"""
    if not os.path.exists(filepath):
        print(f"[!] File data {filepath} tidak ditemukan!")
        return []

    print(f"[*] Membaca data dari: {filepath}")
    if filepath.endswith(".xlsx") or filepath.endswith(".xls"):
        raw_data = read_excel_rows(filepath)
    else:
        raw_data = read_csv_rows(filepath)

    if not raw_data:
        print("[!] File data kosong atau tidak bisa dibaca.")
        return []

    sample_keys = list(raw_data[0].keys())

    # Deteksi otomatis nama kolom
    col_mapping = {}
    for col in sample_keys:
        c_low = str(col).lower()
        if any(k in c_low for k in ["whatsapp", "wa", "no. hp", "nomor hp", "telepon", "phone"]):
            if "phone" not in col_mapping:
                col_mapping["phone"] = col
        elif any(k in c_low for k in ["panggilan", "nickname"]):
            col_mapping["panggilan"] = col
        elif any(k in c_low for k in ["nama lengkap", "nama"]):
            if "nama" not in col_mapping:
                col_mapping["nama"] = col
        elif "gugus" in c_low:
            col_mapping["gugus"] = col
        elif "jurusan" in c_low:
            col_mapping["jurusan"] = col
        elif any(k in c_low for k in ["program studi", "prodi"]):
            col_mapping["prodi"] = col

    if "phone" not in col_mapping:
        print("[!] Gagal mendeteksi kolom nomor WhatsApp!")
        print("Daftar kolom yang ada:", sample_keys)
        return []

    contacts = []
    for row in raw_data:
        raw_phone = row.get(col_mapping.get("phone"))
        norm_phone = normalize_phone(raw_phone)
        if not norm_phone:
            continue

        item = {
            "phone": norm_phone,
            "nama": str(row.get(col_mapping.get("nama", ""), "") or ""),
            "panggilan": str(row.get(col_mapping.get("panggilan", ""), "") or ""),
            "gugus": str(row.get(col_mapping.get("gugus", ""), "") or ""),
            "jurusan": str(row.get(col_mapping.get("jurusan", ""), "") or ""),
            "prodi": str(row.get(col_mapping.get("prodi", ""), "") or ""),
            "raw_row": row
        }
        contacts.append(item)

    print(f"[+] Berhasil memuat {len(contacts)} kontak dengan nomor valid.")
    return contacts


def send_whatsapp_message(phone, message, load_delay=config.WHATSAPP_LOAD_DELAY):
    """
    Mengirim pesan menggunakan protokol resmi WhatsApp Desktop di Windows:
    whatsapp://send?phone=...&text=...
    """
    encoded_text = urllib.parse.quote(message)
    wa_url = f"whatsapp://send?phone={phone}&text={encoded_text}"
    
    # Buka WhatsApp Desktop
    os.startfile(wa_url)
    
    # Tunggu WhatsApp memuat halaman chat dan meletakkan kursor di kotak pesan
    time.sleep(load_delay)
    
    # Tekan Enter untuk mengirim pesan (menggunakan Win32 API native yang stabil)
    press_enter_native()


def test_single_number():
    """Mode uji coba untuk mengirim ke 1 nomor"""
    print("\n--- UJI COBA PENGIRIMAN 1 NOMOR ---")
    target = input("Masukkan nomor WhatsApp uji coba (contoh: 08123456789): ").strip()
    phone = normalize_phone(target)
    if not phone:
        print("[!] Nomor tidak valid.")
        return

    template = read_template()
    dummy_data = {
        "nama": "Kak Uji Coba",
        "panggilan": "Tester",
        "gugus": "Contoh 5",
        "jurusan": "Teknik Informatika",
        "prodi": "D4 Teknik Multimedia Digital"
    }
    pesan = format_message(template, dummy_data)
    
    print("\n[Preview Pesan Uji Coba]:")
    print("-" * 40)
    print(pesan)
    print("-" * 40)
    print(f"Tujuan: {phone}")
    
    konfirmasi = input("\nKirim pesan uji coba sekarang? (y/n): ").strip().lower()
    if konfirmasi == "y":
        print("[*] Membuka WhatsApp Desktop...")
        try:
            send_whatsapp_message(phone, pesan)
            print("[+] Pesan uji coba berhasil dikirim via WhatsApp Desktop!")
        except Exception as e:
            print(f"[!] Terjadi kesalahan: {e}")


def preview_data(contacts):
    """Melihat ringkasan data dan contoh pesan yang akan dikirim"""
    if not contacts:
        print("[!] Belum ada kontak yang dimuat.")
        return

    template = read_template()
    sent_list = load_sent_log()
    pending = [c for c in contacts if c["phone"] not in sent_list]

    print("\n--- RINGKASAN DATA KONTAK ---")
    print(f"Total Kontak Valid   : {len(contacts)}")
    print(f"Sudah Pernah Dikirim : {len(sent_list)}")
    print(f"Siap Dikirim         : {len(pending)}")
    print("-" * 50)

    print("\n[Contoh 3 Pesan Pertama yang Akan Dikirim]:")
    for i, c in enumerate(pending[:3], 1):
        pesan = format_message(template, c)
        print(f"\n--- Kontak #{i}: {c['nama']} ({c['phone']}) ---")
        print(pesan)
    print("-" * 50)


def run_batch_sending(contacts):
    """Menjalankan pengiriman massal dengan jeda acak aman dan pencatatan riwayat"""
    template = read_template()
    sent_list = load_sent_log()
    pending = [c for c in contacts if c["phone"] not in sent_list]

    if not pending:
        print("\n[✓] Semua kontak dalam data sudah pernah dikirimi pesan!")
        return

    print("\n" + "=" * 55)
    print(f"SIAP MENGIRIM PESAN KE {len(pending)} KONTAK")
    print(f"Jeda aman antar pesan: {config.MIN_DELAY_BETWEEN_CHATS} - {config.MAX_DELAY_BETWEEN_CHATS} detik")
    print("=" * 55)
    
    limit_input = input(f"Berapa kontak yang ingin dikirim dalam sesi ini? (Enter untuk semua {len(pending)}): ").strip()
    if limit_input.isdigit():
        limit = int(limit_input)
        pending = pending[:limit]

    print("\n[PERINGATAN PENTING]")
    print("1. Pastikan aplikasi WhatsApp Desktop sudah dalam kondisi login.")
    print("2. JANGAN menggerakkan mouse atau mengetik di aplikasi lain saat pesan sedang dikirim.")
    print("3. Untuk berhenti darurat kapan saja, tekan Ctrl + C di terminal ini.\n")

    konfirmasi = input(f"Ketik 'MULAI' untuk melanjutkan pengiriman ke {len(pending)} nomor: ").strip()
    if konfirmasi != "MULAI":
        print("Pengiriman dibatalkan.")
        return

    print("\n[*] Memulai pengiriman dalam 5 detik... Silakan biarkan layar tetap terbuka.")
    for i in range(5, 0, -1):
        print(f"Mulai dalam {i}...", end="\r")
        time.sleep(1)
    print("\n" + "-" * 55)

    sukses = 0
    gagal = 0

    for idx, c in enumerate(pending, 1):
        phone = c["phone"]
        nama = c.get("nama") or c.get("panggilan")
        pesan = format_message(template, c)

        print(f"[{idx}/{len(pending)}] Mengirim ke: {nama} ({phone})...")
        try:
            send_whatsapp_message(phone, pesan)
            append_sent_log(c, phone, "BERHASIL")
            sukses += 1
            print(f"      -> Terkirim!")
        except Exception as e:
            print(f"      -> GAGAL: {e}")
            append_sent_log(c, phone, f"GAGAL: {e}")
            gagal += 1

        # Jika masih ada kontak berikutnya, beri jeda acak
        if idx < len(pending):
            delay = random.randint(config.MIN_DELAY_BETWEEN_CHATS, config.MAX_DELAY_BETWEEN_CHATS)
            print(f"      -> Menunggu jeda aman {delay} detik sebelum kontak berikutnya...", end="", flush=True)
            for d in range(delay, 0, -1):
                time.sleep(1)
                print(f"\r      -> Menunggu jeda aman {d} detik sebelum kontak berikutnya...", end="", flush=True)
            print("\r" + " " * 75 + "\r", end="")

    print("\n" + "=" * 55)
    print(f"PROSES SELESAI!")
    print(f"Berhasil Terkirim : {sukses}")
    print(f"Gagal             : {gagal}")
    print(f"Log tersimpan di  : {config.LOG_FILE}")
    print("=" * 55)


def main():
    print("=" * 60)
    print("      WA MENTORING SENDER - AUTOMATION TOOL")
    print("=" * 60)

    # Cari file data kontak
    data_file = find_data_file()
    if not data_file:
        print("[!] File data kontak bawaan tidak ditemukan.")
        data_file = input("Masukkan path file Excel (.xlsx) atau CSV Anda: ").strip(' "\'')

    contacts = []
    if data_file and os.path.exists(data_file):
        contacts = load_contacts(data_file)
    else:
        print("[!] File data tidak valid atau belum dipilih.")

    while True:
        print("\n--- MENU UTAMA ---")
        print("1. Kirim Uji Coba (Test Send ke 1 Nomor Anda)")
        print("2. Preview Pesan & Daftar Penerima (Dry Run)")
        print("3. Mulai Pengiriman Massal ke Calon Mentee")
        print("4. Ganti / Muat Ulang File Data Kontak")
        print("5. Keluar")
        
        pilihan = input("\nPilih menu (1-5): ").strip()

        if pilihan == "1":
            test_single_number()
        elif pilihan == "2":
            preview_data(contacts)
        elif pilihan == "3":
            if not contacts:
                print("[!] Data kontak masih kosong. Muat file data terlebih dahulu (Menu 4).")
            else:
                run_batch_sending(contacts)
        elif pilihan == "4":
            new_path = input("Masukkan path file Excel (.xlsx) atau CSV baru: ").strip(' "\'')
            if os.path.exists(new_path):
                data_file = new_path
                contacts = load_contacts(data_file)
            else:
                print("[!] File tidak ditemukan.")
        elif pilihan == "5":
            print("Sampai jumpa!")
            break
        else:
            print("[!] Pilihan tidak valid.")


if __name__ == "__main__":
    main()
