# 📱 WhatsApp Desktop Automation Sender

Script otomasi berbasis Python untuk mengirimkan pesan WhatsApp secara terpersonalisasi melalui aplikasi **WhatsApp Desktop (Windows)** dengan jeda aman (*rate-limiting*), penanganan jendela otomatis, dan integrasi data CSV/Excel.

> [!NOTE]
> Proyek ini dirancang untuk otomasi kegiatan kepanitiaan, broadcast mentoring, dan korespondensi resmi dengan tetap mengedepankan jeda waktu santai (*anti-spam*) serta personalisasi nama penerima.

---

## ✨ Fitur Utama

- 🔗 **Native Windows Protocol Integration:** Membuka obrolan langsung via URI resmi `whatsapp://send?phone=...&text=...` tanpa dependensi browser berat.
- 🎯 **Smart Window Focusing & Hardware Key Injection:** Secara otomatis mencari jendela WhatsApp Desktop, mengangkatnya ke posisi aktif (*foreground*), dan mengirim event Enter menggunakan hardware scan code `0x1C` (Win32 API).
- 🏷️ **Dynamic Template Rendering:** Mengisi variabel dinamis otomatis seperti `{nama}`, `{panggilan}`, `{gugus}`, `{jurusan}`, dan `{prodi}`.
- ⏱️ **Configurable Anti-Spam Delays:** Dilengkapi jeda waktu acak yang dapat disesuaikan (misal 15–25 detik) untuk menghindari pembatasan pengiriman massal.
- 📊 **Smart Column Detection:** Otomatis mendeteksi kolom nomor WhatsApp, nama, panggilan, dan gugus baik dari file `.csv` maupun `.xlsx` (Excel).
- 🛡️ **Anti-Duplicate Sending & Logger:** Setiap nomor yang berhasil dikirim langsung dicatat ke `sent_log.csv` sehingga tidak ada pesan yang terkirim dobel jika script dijalankan ulang.
- 🎮 **Interactive Demo (Dry-Run Mode):** Dilengkapi script simulator `demo.py` untuk menguji data dan alur kerja tanpa membuka aplikasi WhatsApp sungguhan.

---

## 🖥️ Demonstrasi Output Terminal (Dry-Run Mode)

```text
=================================================================
      🚀 WA AUTOMATION SENDER - INTERACTIVE DEMO (DRY-RUN)
=================================================================
[*] Mode: Simulasi Aman (Tidak akan mengirim pesan nyata)
[*] Memuat data contoh dari: kontak_sample.csv
[+] Berhasil memuat 4 kontak dengan nomor valid.

-----------------------------------------------------------------
📝 TEMPLATE PESAN AKTIF:
-----------------------------------------------------------------
Assalamualaikum, halo {panggilan}, mohon maaf mengganggu waktunya...
-----------------------------------------------------------------

[1/4] Memproses Kontak: Ahmad Budi Santoso (6281234567890)
      📌 Sapaan: Kak Budi | Gugus: Gugus 1
      🔗 Protocol: whatsapp://send?phone=6281234567890&text=[ENCODED]
      ⏳ Membuka jendela & menunggu fokus... [SIMULASI]
      ⌨️ Mengirim event keyboard: ENTER (Hardware ScanCode 0x1C)
      ✅ [STATUS: BERHASIL] Pesan terkirim ke Budi!
      ⏱️ Menunggu jeda acak anti-spam (3s)...
```

---

## 📁 Struktur Direktori

```text
wa-mentoring-sender/
├── .gitignore             # Mencegah nomor telepon pribadi & log terunggah
├── config.py              # Pengaturan jeda waktu, path file, dan delay
├── demo.py                # Simulator demonstrasi alur kerja (Aman / Dry-Run)
├── kontak_sample.csv      # Contoh format data kontak dummy
├── requirements.txt       # Daftar dependensi Python
├── template_pesan.txt     # Template pesan yang dapat disesuaikan
├── wa_sender.py           # Engine utama automasi WhatsApp Desktop
└── jalankan_bot.bat       # Launcher praktis untuk pengguna Windows
```

---

## 🚀 Panduan Instalasi & Penggunaan

### 1. Kloning Repositori
```bash
git clone https://github.com/USERNAME/wa-desktop-automation.git
cd wa-desktop-automation
```

### 2. Pasang Dependensi
Pastikan Python 3.8+ sudah terpasang di sistem Windows Anda:
```bash
pip install -r requirements.txt
```

### 3. Jalankan Demo (Simulasi Aman)
Uji coba alur kerja tanpa mengirim pesan nyata:
```bash
python demo.py
```

### 4. Menjalankan Pengiriman Nyata
1. Buka aplikasi **WhatsApp Desktop** di Windows dan pastikan sudah dalam keadaan login.
2. Edit pesan Anda di `template_pesan.txt`.
3. Masukkan data kontak Anda (format CSV atau Excel).
4. Jalankan script interaktif:
   ```bash
   python wa_sender.py
   ```
   *atau cukup klik dua kali file `jalankan_bot.bat`.*

---

## ⚙️ Format Data Kontak (`kontak.csv` / `.xlsx`)

Format kolom yang didukung (script otomatis mendeteksi nama kolom):
```csv
Nama Lengkap,Panggilan,Gugus,Jurusan,Program Studi,No. WhatsApp
Ahmad Budi Santoso,Budi,Gugus 1,Teknik Informatika,D4 Teknik Informatika,081234567890
Muhammad Dimas Pratama,Dimas,Gugus 5,Teknik Mesin,D3 Teknik Mesin,081987654321
```

> **Catatan Normalisasi Nomor:** Script akan otomatis mengubah format nomor lokal `08xx`, `+62xx`, `8xx`, maupun angka desimal float Excel `.0` menjadi format standar internasional `628xx`.

---

## ⚠️ Disclaimer & Kebijakan Privasi

1. **Privasi Data:** Repositori ini dilengkapi konfigurasi `.gitignore` ketat untuk memastikan nomor telepon, nama pribadi, dan riwayat pengiriman tidak akan pernah ter-commit ke GitHub.
2. **Kebijakan WhatsApp:** Script ini ditujukan untuk mempermudah komunikasi panitia/organisasi secara wajar. Gunakan jeda waktu yang bijak dan hindari pengiriman massal tanpa jeda guna mematuhi *Terms of Service* WhatsApp.

---

## 📄 Lisensi
Didistribusikan di bawah lisensi MIT. Silakan gunakan dan kembangkan untuk kebutuhan organisasi atau kampus Anda.
