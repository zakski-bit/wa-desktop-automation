import unittest
import os
import sys

# Tambahkan direktori kerja ke sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wa_sender import normalize_phone, format_message, read_template, load_contacts, find_data_file

class TestWaSender(unittest.TestCase):

    def test_phone_normalization(self):
        self.assertEqual(normalize_phone("08123456789"), "628123456789")
        self.assertEqual(normalize_phone("8123456789"), "628123456789")
        self.assertEqual(normalize_phone("+62 812-3456-789"), "628123456789")
        self.assertEqual(normalize_phone("628123456789"), "628123456789")
        self.assertEqual(normalize_phone("87848350765.0"), "6287848350765")
        self.assertIsNone(normalize_phone("123"))
        self.assertIsNone(normalize_phone(""))
        self.assertIsNone(normalize_phone(None))

    def test_message_formatting(self):
        template = "Halo Kak {panggilan}! Selamat datang di {gugus} ({jurusan})."
        data = {
            "nama": "BagasKara Wibowo",
            "panggilan": "Bagas",
            "gugus": "Gugus 5",
            "jurusan": "Teknik Elektro",
            "prodi": "D3 Telekomunikasi"
        }
        formatted = format_message(template, data)
        self.assertIn("Kak Bagas", formatted)
        self.assertIn("Gugus 5", formatted)
        self.assertIn("Teknik Elektro", formatted)

    def test_data_loading(self):
        data_file = find_data_file()
        self.assertIsNotNone(data_file, "File data default harus ditemukan")
        contacts = load_contacts(data_file)
        self.assertGreater(len(contacts), 0, "Kontak harus terdeteksi lebih dari 0")
        first_contact = contacts[0]
        self.assertTrue(first_contact["phone"].startswith("628"))
        print(f"\n[Test Berhasil] Terbaca {len(contacts)} kontak dari file data.")

if __name__ == "__main__":
    unittest.main()
