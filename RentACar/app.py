from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- MAIL AYARLARI (BURAYI DOLDURMALISIN) ---
GMAIL_ADRESIN = "edirentacar1@gmail.com"  # Kendi Gmail adresini yaz
GMAIL_SIFREN = "hcko tspl oobs ihnr"      # Google'dan aldığın 16 haneli uygulama şifresi
from werkzeug.utils import secure_filename # Dosya güvenliği için gerekli

app = Flask(__name__)
app.secret_key = "cok_gizli_ve_rastgele_bir_anahtar_kelime"

# --- VERİTABANI YOLU ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'rentacar.db')

# --- RESİM YÜKLEME AYARLARI (YENİ) ---
# Resimlerin kaydedileceği klasör: static/uploads
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Klasör yoksa otomatik oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def baglanti_kur():
    baglanti = sqlite3.connect(DB_PATH)
    baglanti.row_factory = sqlite3.Row
    return baglanti
def siparis_maili_gonder(alici_email, arac_bilgisi, alis, donus, tutar):
    try:
        baslik = "Rezervasyon Onayı - EDİ Rent A Car"
        icerik = f"""
        Merhaba,
        
        EDİ Rent A Car'ı tercih ettiğiniz için teşekkür ederiz.
        Rezervasyonunuz başarıyla alınmıştır.
        
        ARAÇ BİLGİLERİ:
        {arac_bilgisi}
        
        TARİHLER:
        Alış: {alis}
        Dönüş: {donus}
        
        TOPLAM TUTAR:
        {tutar} TL
        
        Aracı teslim alacağınız lokasyon:
        İstanbul Havalimanı, Otopark Katı R Blok.
        
        İyi yolculuklar dileriz!
        """

        # Mail Yapısını Kur
        msg = MIMEMultipart()
        msg['From'] = GMAIL_ADRESIN
        msg['To'] = alici_email
        msg['Subject'] = baslik
        msg.attach(MIMEText(icerik, 'plain'))

        # Gmail Sunucusuna Bağlan ve Gönder
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ADRESIN, GMAIL_SIFREN)
        server.send_message(msg)
        server.quit()
        print("Mail başarıyla gönderildi!")
        
    except Exception as e:
        print(f"Mail gönderme hatası: {e}")

# 1. ANA SAYFA
@app.route('/')
def ana_sayfa():
    try:
        baglanti = baglanti_kur()
        imlec = baglanti.cursor()
        imlec.execute("SELECT * FROM arabalar")
        arabalar = imlec.fetchall()
        
        imlec.execute("SELECT DISTINCT yil FROM arabalar ORDER BY yil DESC")
        yillar = imlec.fetchall()
        
        admin_mi = False
        if 'admin' in session and session['admin'] == 1:
            admin_mi = True
            
        baglanti.close()
        return render_template('index.html', arabalar=arabalar, admin_mi=admin_mi, yillar=yillar)
    except sqlite3.OperationalError:
        return "Veritabanı Hatası: Lütfen setup.py dosyasını çalıştırın."

# 2. KAYIT OL
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        ad_soyad = request.form['ad_soyad']
        email = request.form['email']
        sifre = request.form['sifre']
        telefon = request.form['telefon']

        baglanti = baglanti_kur()
        imlec = baglanti.cursor()
        imlec.execute("INSERT INTO kullanicilar (ad_soyad, email, sifre, telefon, admin) VALUES (?, ?, ?, ?, 0)", 
                      (ad_soyad, email, sifre, telefon))
        baglanti.commit()
        baglanti.close()
        flash("Kaydınız başarıyla oluşturuldu. Lütfen giriş yapın.", "basari")
        return redirect(url_for('giris'))
    return render_template('kayit.html')

# 3. GİRİŞ YAP
@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        email = request.form['email']
        sifre = request.form['sifre']

        baglanti = baglanti_kur()
        imlec = baglanti.cursor()
        imlec.execute("SELECT * FROM kullanicilar WHERE email = ? AND sifre = ?", (email, sifre))
        kullanici = imlec.fetchone()
        baglanti.close()

        if kullanici:
            session['kullanici_id'] = kullanici['id']
            session['ad_soyad'] = kullanici['ad_soyad']
            session['admin'] = kullanici['admin']
            return redirect('/')
        else:
            flash("E-posta adresi veya şifre hatalı!", "hata")
            return redirect(url_for('giris'))
    return render_template('giris.html')

# 4. ÇIKIŞ YAP
@app.route('/cikis')
def cikis():
    session.clear()
    return redirect('/')

# 5. ARAÇ EKLEME (GÜNCELLENDİ: Dosya Yüklemeli)
@app.route('/arac-ekle', methods=['GET', 'POST'])
def arac_ekle():
    if 'admin' not in session or session['admin'] != 1:
        return redirect('/')

    baglanti = baglanti_kur()
    imlec = baglanti.cursor()

    if request.method == 'POST':
        marka = request.form['marka']
        model = request.form['model']
        yil = request.form['yil']
        yakit = request.form['yakit']
        vites = request.form['vites']
        fiyat = request.form['fiyat']
        
        # --- DOSYA YÜKLEME İŞLEMİ ---
        dosya = request.files['gorsel'] # HTML'den gelen dosya
        gorsel_yolu = "" # Varsayılan boş

        if dosya and dosya.filename != '':
            filename = secure_filename(dosya.filename)
            # Dosyayı sunucuya kaydet
            dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Veritabanına kaydedilecek yol (/static/uploads/resim.jpg)
            gorsel_yolu = f"/static/uploads/{filename}"
        else:
            # Eğer resim yüklenmezse varsayılan bir resim koyabilirsin
            gorsel_yolu = "https://via.placeholder.com/300x200?text=Resim+Yok"

        imlec.execute("INSERT INTO arabalar (marka, model, yil, yakit, vites, gorsel, gunluk_fiyat, durum) VALUES (?, ?, ?, ?, ?, ?, ?, 1)", 
                      (marka, model, yil, yakit, vites, gorsel_yolu, fiyat))
        baglanti.commit()
        baglanti.close()
        return redirect('/arac-ekle')

    imlec.execute("SELECT * FROM arabalar ORDER BY id DESC")
    mevcut_arabalar = imlec.fetchall()
    baglanti.close()

    return render_template('arac_ekle.html', arabalar=mevcut_arabalar)

# 6. ARAÇ GÜNCELLEME
@app.route('/arac-guncelle/<int:id>', methods=['POST'])
def arac_guncelle(id):
    if 'admin' not in session or session['admin'] != 1:
        return redirect('/')
    
    yeni_fiyat = request.form['yeni_fiyat']
    yeni_durum = request.form['yeni_durum']

    baglanti = baglanti_kur()
    imlec = baglanti.cursor()
    imlec.execute("UPDATE arabalar SET gunluk_fiyat = ?, durum = ? WHERE id = ?", (yeni_fiyat, yeni_durum, id))
    baglanti.commit()
    baglanti.close()
    
    return redirect('/arac-ekle')

# 7. ARAÇ SİLME
@app.route('/arac-sil/<int:id>')
def arac_sil(id):
    if 'admin' not in session or session['admin'] != 1:
        return redirect('/')
        
    baglanti = baglanti_kur()
    imlec = baglanti.cursor()
    imlec.execute("DELETE FROM arabalar WHERE id = ?", (id,))
    baglanti.commit()
    baglanti.close()
    
    return redirect('/arac-ekle')

# 8. ÖDEME EKRANI
@app.route('/odeme', methods=['POST'])
def odeme():
    if 'ad_soyad' not in session:
        flash("Araç kiralamak için lütfen önce giriş yapınız.", "hata")
        return redirect(url_for('giris'))

    bilgiler = {
        'araba_id': request.form['araba_id'],
        'alis_tarihi': request.form['alis_tarihi'],
        'donus_tarihi': request.form['donus_tarihi'],
        'toplam_tutar': request.form['toplam_tutar_input']
    }

    baglanti = baglanti_kur()
    imlec = baglanti.cursor()
    imlec.execute("SELECT * FROM arabalar WHERE id = ?", (bilgiler['araba_id'],))
    araba = imlec.fetchone()
    baglanti.close()

    return render_template('odeme.html', bilgiler=bilgiler, araba=araba)

# 9. KİRALAMA İŞLEMİNİ TAMAMLA (GÜNCELLENDİ)
# 9. KİRALAMA İŞLEMİNİ TAMAMLA (MAİL GÖNDERMELİ)
@app.route('/kiralama-tamamla', methods=['POST'])
def kiralama_tamamla():
    if 'ad_soyad' not in session:
        return redirect('/')

    # Formdan verileri al
    araba_id = request.form['araba_id']
    musteri_id = session['kullanici_id']
    alis_tarihi = request.form['alis_tarihi']
    donus_tarihi = request.form['donus_tarihi']
    toplam_tutar = request.form['toplam_tutar']

    baglanti = baglanti_kur()
    imlec = baglanti.cursor()

    # 1. Rezervasyonu kaydet
    imlec.execute("INSERT INTO rezervasyonlar (araba_id, musteri_id, alis_tarihi, donus_tarihi, toplam_tutar) VALUES (?, ?, ?, ?, ?)", 
                  (araba_id, musteri_id, alis_tarihi, donus_tarihi, toplam_tutar))

    # 2. Arabayı 'Kirada' (0) yap
    imlec.execute("UPDATE arabalar SET durum = 0 WHERE id = ?", (araba_id,))

    # --- MAİL İÇİN BİLGİLERİ TOPLA ---
    # a. Müşterinin emailini bul
    imlec.execute("SELECT email FROM kullanicilar WHERE id = ?", (musteri_id,))
    musteri_email = imlec.fetchone()['email']

    # b. Arabanın adını bul (Mailde yazmak için)
    imlec.execute("SELECT marka, model FROM arabalar WHERE id = ?", (araba_id,))
    arac = imlec.fetchone()
    arac_adi = f"{arac['marka']} {arac['model']}"

    baglanti.commit()
    baglanti.close()

    # --- MAİLİ GÖNDER ---
    # Fonksiyonu çağırıyoruz
    siparis_maili_gonder(musteri_email, arac_adi, alis_tarihi, donus_tarihi, toplam_tutar)

    return redirect('/kiralama-basarili')


# 10. BAŞARILI İŞLEM SAYFASI (YENİ EKLENDİ)
@app.route('/kiralama-basarili')
def kiralama_basarili():
    return render_template('basarili.html')


if __name__ == '__main__':
    app.run(debug=True)