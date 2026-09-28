"""
Script Pengiriman Otomatis Massal ke Seluruh Kontak Prioritas
"""

import os
import sys
import time
import random

# Konfigurasi encoding UTF-8 untuk output terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import wa_sender
import config

def main():
    print("=" * 60)
    print("   MEMULAI PENGIRIMAN MASSAL KE SELURUH KONTAK PRIORITAS")
    print("=" * 60)

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        data_file = sys.argv[1]
    else:
        data_file = wa_sender.find_data_file()
        
    if not data_file:
        print("[!] File data kontak tidak ditemukan!")
        return

    contacts = wa_sender.load_contacts(data_file)
    template = wa_sender.read_template()
    sent_list = wa_sender.load_sent_log()

    pending = [c for c in contacts if c["phone"] not in sent_list]

    if not pending:
        print("[✓] Semua kontak dalam daftar prioritas sudah pernah dikirimi pesan!")
        return

    total = len(pending)
    print(f"[*] Ditemukan {total} kontak yang belum dikirim.")
    print(f"[*] Jeda aman: {config.MIN_DELAY_BETWEEN_CHATS} - {config.MAX_DELAY_BETWEEN_CHATS} detik per pesan.\n")

    sukses = 0
    gagal = 0

    for idx, c in enumerate(pending, 1):
        phone = c["phone"]
        nama = c.get("nama")
        panggilan = c.get("panggilan") or nama
        pesan = wa_sender.format_message(template, c)

        print(f"[{idx}/{total}] Mengirim ke {panggilan} ({phone})...", flush=True)

        try:
            wa_sender.send_whatsapp_message(phone, pesan, load_delay=4.0)
            wa_sender.append_sent_log(c, phone, "BERHASIL")
            sukses += 1
            print(f"       -> [BERHASIL] Pesan terkirim ke {panggilan}!", flush=True)
        except Exception as e:
            print(f"       -> [GAGAL] {e}", flush=True)
            wa_sender.append_sent_log(c, phone, f"GAGAL: {e}")
            gagal += 1

        # Beri jeda acak antar kontak jika bukan kontak terakhir
        if idx < total:
            delay = random.randint(config.MIN_DELAY_BETWEEN_CHATS, config.MAX_DELAY_BETWEEN_CHATS)
            print(f"       -> Istirahat jeda aman {delay} detik...", flush=True)
            time.sleep(delay)

    print("\n" + "=" * 60)
    print("               PENGIRIMAN SELESAI!")
    print(f"Total Berhasil : {sukses}")
    print(f"Total Gagal    : {gagal}")
    print(f"Riwayat lengkap tersimpan di: {config.LOG_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
