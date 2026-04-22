import sqlite3
import os

# --- EN ÖNEMLİ KISIM BURASI ---
# Dosyanın bulunduğu klasörü tam adres olarak alıyoruz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'rentacar.db')
# ------------------------------

def veritabani_kur():
    print(f"Veritabanı şuraya kuruluyor: {DB_PATH}")
    
    # Tam adresi kullanarak bağlanıyoruz
    baglanti = sqlite3.connect(DB_PATH)
    imlec = baglanti.cursor()

    # Temizlik
    imlec.execute("DROP TABLE IF EXISTS arabalar")
    imlec.execute("DROP TABLE IF EXISTS kullanicilar")
    imlec.execute("DROP TABLE IF EXISTS rezervasyonlar")

    # Tabloları Oluştur
    imlec.execute("""
        CREATE TABLE arabalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marka TEXT,
            model TEXT,
            yil INTEGER,
            yakit TEXT,
            vites TEXT,
            gorsel TEXT,
            gunluk_fiyat REAL,
            durum INTEGER
        )
    """)

    imlec.execute("""
        CREATE TABLE kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad TEXT,
            email TEXT,
            sifre TEXT,
            telefon TEXT,
            admin INTEGER
        )
    """)

    imlec.execute("""
        CREATE TABLE rezervasyonlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            araba_id INTEGER,
            musteri_id INTEGER,
            alis_tarihi TEXT,
            donus_tarihi TEXT,
            toplam_tutar TEXT
        )
    """)

    # Verileri Ekle
    imlec.execute("INSERT INTO kullanicilar (ad_soyad, email, sifre, telefon, admin) VALUES ('EDİ Admin', 'admin@edi.com', '123', '05555555555', 1)")

    arabalar = [
        ('Fiat', 'Egea', 2023, 'Dizel', 'Manuel', 'https://www.fiat.com.tr/content/dam/fiat/tr/modeller/egea-sedan/egea-sedan-my24/agustos-my24/Egea_Sedan_Cross_Lounge_1_5_Gumus_Gri.png', 1400, 1),
        ('Mercedes', 'C200', 2024, 'Benzin', 'Otomatik', 'https://vehicle-images.dealerinspire.com/stock-images/chrome/496f8f537042079038d15024765363e7.png', 7000, 1),
        ('Renault', 'Clio', 2022, 'Benzin', 'Otomatik', 'https://cdn.group.renault.com/ren/tr/model-pages/clio/clio-ph2/visuals/renault-clio-ph2-design-lines-001.jpg.ximg.large.webp/f1694503e9.webp', 1100, 1)
    ]
    imlec.executemany("INSERT INTO arabalar (marka, model, yil, yakit, vites, gorsel, gunluk_fiyat, durum) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", arabalar)

    baglanti.commit()
    baglanti.close()
    print("✅ KURULUM BAŞARILI! Veritabanı oluşturuldu.")

if __name__ == "__main__":
    veritabani_kur()