from datetime import date

import pytest

from app import create_app
from izin import kidem_hesapla, yas_hesapla, yillik_izin_hakki

# Testlerde sonuç günden güne değişmesin diye sabit bir "bugün" kullanılır.
BUGUN = date(2026, 6, 15)
YETISKIN = date(1990, 1, 1)  # 36 yaşında; yaş kuralı devreye girmez


def izin(ise_baslama, dogum=YETISKIN):
    return yillik_izin_hakki(dogum, ise_baslama, bugun=BUGUN)


# Kural 1: Kıdem 1 yıldan az -> 0 gün
def test_bir_yila_bir_gun_kala_izin_yok():
    assert izin(date(2025, 6, 16)) == 0


# Kural 2: Kıdem 1-5 yıl (5 dahil) -> 14 gün
def test_tam_bir_yil_14_gun():
    assert izin(date(2025, 6, 15)) == 14


def test_tam_bes_yil_14_gun():
    assert izin(date(2021, 6, 15)) == 14


def test_bes_yil_bir_gun_14_gun():
    # Kıdem tam yıl olarak sayıldığı için 5 yıl + 1 gün hâlâ 5 yıldır.
    # 20 güne geçiş, 6. yıldönümünde olur.
    assert izin(date(2021, 6, 14)) == 14


# Kural 3: Kıdem 5 yıldan fazla, 15 yıldan az -> 20 gün
def test_alti_yil_20_gun():
    assert izin(date(2020, 6, 15)) == 20


def test_on_bes_yila_bir_gun_kala_20_gun():
    assert izin(date(2011, 6, 16)) == 20


# Kural 4: Kıdem 15 yıl ve üzeri -> 26 gün
def test_tam_on_bes_yil_26_gun():
    assert izin(date(2011, 6, 15)) == 26


# Kural 5: 18 yaş altı veya 50 yaş ve üzeri, kıdem >= 1 ise en az 20 gün
def test_on_yedi_yasinda_en_az_20_gun():
    assert izin(date(2025, 6, 15), dogum=date(2009, 1, 1)) == 20


def test_tam_elli_yasinda_en_az_20_gun():
    assert izin(date(2023, 6, 15), dogum=date(1976, 6, 15)) == 20


def test_elli_yasina_bir_gun_kala_14_gun():
    assert izin(date(2023, 6, 15), dogum=date(1976, 6, 16)) == 14


def test_on_sekiz_yas_alti_ama_kidem_bir_yildan_az_izin_yok():
    assert izin(date(2025, 12, 1), dogum=date(2009, 1, 1)) == 0


def test_elli_yas_ustu_ve_on_bes_yil_kidem_26_gun():
    # Yaş kuralı "en az 20" dediği için 26 gün düşmez.
    assert izin(date(2000, 1, 1), dogum=date(1960, 1, 1)) == 26


# Yardımcı fonksiyonlar ve 29 Şubat
def test_dogum_gunu_gelmediyse_yil_sayilmaz():
    assert yas_hesapla(date(2000, 6, 16), BUGUN) == 25
    assert yas_hesapla(date(2000, 6, 15), BUGUN) == 26


def test_29_subat_dogumlu_hata_vermez():
    dogum = date(2008, 2, 29)
    assert yas_hesapla(dogum, date(2026, 2, 28)) == 17  # Doğum günü henüz dolmadı
    assert yas_hesapla(dogum, date(2026, 3, 1)) == 18


def test_29_subat_ise_baslama_kidemi():
    assert kidem_hesapla(date(2024, 2, 29), date(2025, 2, 28)) == 0
    assert kidem_hesapla(date(2024, 2, 29), date(2025, 3, 1)) == 1


def test_bugun_verilmezse_hata_vermez():
    assert yillik_izin_hakki(date(1990, 1, 1), date(2000, 1, 1)) == 26


# Ana sayfada izin sütunu
@pytest.fixture
def client(tmp_path):
    app = create_app(veritabani_yolu=str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def test_ana_sayfada_izin_sutunu_dogru_deger_gosterir(client):
    # 2010'da işe başlayan biri bugün (ve ileride) 15+ yıl kıdemlidir -> 26 gün.
    veri = {
        "ad_soyad": "Mehmet Kaya",
        "departman": "Depo",
        "dogum_tarihi": "1990-01-01",
        "ise_baslama_tarihi": "2010-01-01",
    }
    html = client.post("/", data=veri, follow_redirects=True).get_data(as_text=True)
    assert "Kıdem (yıl)" in html
    assert "Yıllık izin (gün)" in html
    assert '<td class="izin">26</td>' in html
