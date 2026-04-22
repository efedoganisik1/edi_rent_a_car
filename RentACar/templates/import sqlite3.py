import sqlite3

baglanti = sqlite3.connect('rentacar.db')
imlec = baglanti.cursor()

# 1. ARABALAR TABLOSU
imlec.execute('''
    CREATE TABLE IF NOT EXISTS arabalar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marka TEXT NOT NULL,
        model TEXT NOT NULL,
        yil INTEGER,
        yakit TEXT,
        vites TEXT,
        gorsel TEXT, 
        gunluk_fiyat REAL NOT NULL,
        durum INTEGER DEFAULT 1 
    )
''')

# 2. KULLANICILAR TABLOSU (TELEFON EKLİ!)
imlec.execute('''
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_soyad TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        sifre TEXT NOT NULL,
        telefon TEXT, 
        admin INTEGER DEFAULT 0
    )
''')

# 3. REZERVASYONLAR TABLOSU
imlec.execute('''
    CREATE TABLE IF NOT EXISTS rezervasyonlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        araba_id INTEGER,
        kullanici_id INTEGER,
        alis_tarihi DATE NOT NULL,
        donus_tarihi DATE NOT NULL,
        toplam_ucret REAL,
        FOREIGN KEY(araba_id) REFERENCES arabalar(id),
        FOREIGN KEY(kullanici_id) REFERENCES kullanicilar(id)
    )
''')

# Admin Ekle
imlec.execute("INSERT OR IGNORE INTO kullanicilar (ad_soyad, email, sifre, telefon, admin) VALUES (?, ?, ?, ?, ?)", 
              ("Site Yoneticisi", "admin@rentacar.com", "1234", "5550000000", 1))

baglanti.commit()
baglanti.close()
print("Veritabanı (Telefon özellikli) yeniden kuruldu!")