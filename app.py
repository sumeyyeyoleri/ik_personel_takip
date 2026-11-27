import os
import sqlite3
from datetime import date

from flask import Flask, redirect, render_template, request, url_for


def calisan_dogrula(veri, bugun=None):
    """Form verisini kontrol eder ve hata mesajlarının listesini döndürür.

    Liste boşsa veri geçerlidir.
    `bugun` parametresi testlerde sabit bir tarih vermek için kullanılabilir.
    """
    if bugun is None:
        bugun = date.today()

    hatalar = []

    # Ad soyad boş olamaz (sadece boşluklardan oluşuyorsa da boş sayılır).
    if not veri.get("ad_soyad", "").strip():
        hatalar.append("Ad soyad boş bırakılamaz.")

    # Doğum tarihi geçerli bir tarih olmalı (yıllık izin hesabında gerekecek).
    try:
        date.fromisoformat(veri.get("dogum_tarihi", ""))
    except ValueError:
        hatalar.append("Geçerli bir doğum tarihi giriniz.")

    # İşe başlama tarihi geçerli olmalı ve bugünden ileri olmamalı.
    try:
        ise_baslama = date.fromisoformat(veri.get("ise_baslama_tarihi", ""))
        if ise_baslama > bugun:
            hatalar.append("İşe başlama tarihi bugünden ileri bir tarih olamaz.")
    except ValueError:
        hatalar.append("Geçerli bir işe başlama tarihi giriniz.")

    return hatalar


def create_app(veritabani_yolu=None):
    app = Flask(__name__)

    # Yol verilmezse veritabanı instance/ klasöründe oluşturulur.
    if veritabani_yolu is None:
        os.makedirs(app.instance_path, exist_ok=True)
        veritabani_yolu = os.path.join(app.instance_path, "personel.db")

    def baglanti_al():
        baglanti = sqlite3.connect(veritabani_yolu)
        baglanti.row_factory = sqlite3.Row  # Satırlara sütun adıyla erişmek için
        return baglanti

    # Tablo yoksa oluştur.
    with baglanti_al() as baglanti:
        baglanti.execute(
            """
            CREATE TABLE IF NOT EXISTS calisanlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_soyad TEXT NOT NULL,
                departman TEXT,
                dogum_tarihi TEXT NOT NULL,
                ise_baslama_tarihi TEXT NOT NULL
            )
            """
        )
    baglanti.close()

    @app.route("/", methods=["GET", "POST"])
    def index():
        hatalar = []
        form = {}

        if request.method == "POST":
            form = {
                "ad_soyad": request.form.get("ad_soyad", "").strip(),
                "departman": request.form.get("departman", "").strip(),
                "dogum_tarihi": request.form.get("dogum_tarihi", ""),
                "ise_baslama_tarihi": request.form.get("ise_baslama_tarihi", ""),
            }
            hatalar = calisan_dogrula(form)

            if not hatalar:
                with baglanti_al() as baglanti:
                    baglanti.execute(
                        "INSERT INTO calisanlar (ad_soyad, departman, dogum_tarihi, ise_baslama_tarihi) "
                        "VALUES (?, ?, ?, ?)",
                        (form["ad_soyad"], form["departman"], form["dogum_tarihi"], form["ise_baslama_tarihi"]),
                    )
                baglanti.close()
                # Kayıttan sonra sayfaya yönlendir; böylece sayfa yenilenince form tekrar gönderilmez.
                return redirect(url_for("index"))

        baglanti = baglanti_al()
        calisanlar = baglanti.execute("SELECT * FROM calisanlar ORDER BY id").fetchall()
        baglanti.close()

        durum_kodu = 400 if hatalar else 200
        return render_template("index.html", calisanlar=calisanlar, hatalar=hatalar, form=form), durum_kodu

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5001)
