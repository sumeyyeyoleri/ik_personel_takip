# İK Personel Takip

## Problem
Personel tedarik eden İK firmaları, çok sayıda çalışanı farklı müşteri firmalara yerleştirir. Hangi çalışanın hangi firmada olduğu, yıllık izin hakları, sözleşme ve belge süreleri çoğu zaman dağınık Excel tablolarında tutulur. Bu da hatalara ve zaman kaybına yol açar.

## Kimin için?
Personel tedarik firmalarında çalışan İK uzmanları ve yöneticiler için.

## Çözüm
Çalışan bilgilerini tek yerde toplayan ve yıllık izin hakkını İş Kanunu'na göre otomatik hesaplayan basit bir web uygulaması.

## Proje panosu
https://github.com/users/sumeyyeyoleri/projects/1

## Geliştirilen özellikler
- [ ] [#1 Çalışan ekleme ve listeleme](https://github.com/sumeyyeyoleri/ik_personel_takip/issues/1)
- [ ] [#2 Yıllık izin hakkını otomatik hesaplama](https://github.com/sumeyyeyoleri/ik_personel_takip/issues/2)

## Kurulum ve çalıştırma
Gereksinim: Python 3 (proje Python 3.14 ile geliştirildi). Komutlar macOS/Linux içindir.

```bash
# 1. Repoyu klonla ve klasöre gir
git clone https://github.com/sumeyyeyoleri/ik_personel_takip.git
cd ik_personel_takip

# 2. Sanal ortam oluştur ve etkinleştir
python3 -m venv .venv
source .venv/bin/activate

# 3. Paketleri kur
pip install -r requirements.txt

# 4. Uygulamayı başlat
python app.py
```

Uygulama açıldıktan sonra tarayıcıda şu adrese git: http://127.0.0.1:5001

(macOS'ta 5000 portunu AirPlay kullandığı için uygulama 5001 portunda çalışır.)

Testleri çalıştırmak için (sanal ortam etkinken):

```bash
pytest -v
```

## Özellikleri deneme
### #1 Çalışan ekleme ve listeleme
Uygulamayı başlatıp http://127.0.0.1:5001 adresini aç.

1. **Formda dört alan var:** Sayfanın üstündeki formda "Ad soyad", "Departman", "Doğum tarihi" ve "İşe başlama tarihi" alanlarını gör.
2. **Kayıt listede görünür:** Tüm alanları doldur (işe başlama tarihi bugün ya da geçmiş bir tarih olsun) ve "Kaydet"e bas. Çalışan, alttaki "Çalışanlar" tablosunda görünür.
3. **Boş ad soyad reddedilir:** Ad soyad alanını boş bırak (ya da sadece boşluk yaz), diğer alanları doldurup "Kaydet"e bas. "Ad soyad boş bırakılamaz." mesajı çıkar, kayıt eklenmez ve formdaki diğer değerler silinmez.
4. **Gelecek tarihli işe başlama reddedilir:** İşe başlama tarihine yarının tarihini seçip "Kaydet"e bas. "İşe başlama tarihi bugünden ileri bir tarih olamaz." mesajı çıkar ve kayıt eklenmez.
