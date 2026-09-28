"""
Demo Script: WA Automation Simulator (Safe Dry-Run Mode)
Menampilkan demonstrasi alur kerja otomasi WhatsApp tanpa harus membuka aplikasi WhatsApp sungguhan.
Cocok untuk demonstrasi video, screenshot README GitHub, atau pengujian data.
"""

import sys
import time
import os

# Konfigurasi UTF-8 untuk output terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import wa_sender

def run_demo():
    print("=" * 65)
    print("      🚀 WA AUTOMATION SENDER - INTERACTIVE DEMO (DRY-RUN)")
    print("=" * 65)
    print("[*] Mode: Simulasi Aman (Tidak akan mengirim pesan nyata)")
    
    sample_file = os.path.join(os.path.dirname(__file__), "kontak_sample.csv")
    if not os.path.exists(sample_file):
        print("[!] File kontak_sample.csv tidak ditemukan.")
        return

    print(f"[*] Memuat data contoh dari: {os.path.basename(sample_file)}")
    contacts = wa_sender.load_contacts(sample_file)
    template = wa_sender.read_template()
    
    print("\n" + "-" * 65)
    print("📝 TEMPLATE PESAN AKTIF:")
    print("-" * 65)
    print(template)
    print("-" * 65)
    
    print(f"\n[+] Total kontak contoh siap diproses: {len(contacts)}")
    print("\nTekan Enter untuk memulai simulasi pengiriman otomatis...")
    try:
        input()
    except EOFError:
        pass

    print("\n" + "=" * 65)
    print("               MEMULAI SIMULASI PENGIRIMAN")
    print("=" * 65)

    for i, c in enumerate(contacts, 1):
        phone = c["phone"]
        nama = c["nama"]
        panggilan = c["panggilan"]
        pesan = wa_sender.format_message(template, c)
        
        print(f"\n[{i}/{len(contacts)}] Memproses Kontak: {nama} ({phone})")
        print(f"      📌 Sapaan: Kak {panggilan} | Gugus: {c['gugus']}")
        print(f"      🔗 Protocol: whatsapp://send?phone={phone}&text=[ENCODED_MESSAGE]")
        print("      ⏳ Membuka jendela & menunggu fokus... [SIMULASI]")
        time.sleep(1.2)
        print("      ⌨️ Mengirim event keyboard: ENTER (Hardware ScanCode 0x1C)")
        time.sleep(0.5)
        print(f"      ✅ [STATUS: BERHASIL] Pesan terkirim ke {panggilan}!")
        
        if i < len(contacts):
            delay = 3  # jeda demo dipersingkat agar cepat
            print(f"      ⏱️ Menunggu jeda acak anti-spam ({delay}s)...", end="", flush=True)
            for d in range(delay, 0, -1):
                time.sleep(1)
                print(f"\r      ⏱️ Menunggu jeda acak anti-spam ({d}s)...", end="", flush=True)
            print("\r" + " " * 50 + "\r", end="")

    print("\n" + "=" * 65)
    print("             🎉 SIMULASI SELESAI DENGAN SUKSES!")
    print("=" * 65)
    print("Semua data berhasil diparsing, nomor distandardisasi ke format 62,")
    print("dan template pesan berhasil dipersonalisasi.")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_demo()
