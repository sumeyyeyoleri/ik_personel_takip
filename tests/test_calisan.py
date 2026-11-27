from datetime import date, timedelta

import pytest

from app import calisan_dogrula, create_app


@pytest.fixture
def client(tmp_path):
    # Her test için geçici, boş bir veritabanı kullanılır.
    app = create_app(veritabani_yolu=str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def gecerli_veri(**degisiklikler):
    veri = {
        "ad_soyad": "Ayşe Yılmaz",
        "departman": "Muhasebe",
        "dogum_tarihi": "1990-05-12",
        "ise_baslama_tarihi": "2020-03-01",
    }
    veri.update(degisiklikler)
    return veri


# Kabul kriteri 1: Formda dört alan bulunur.
def test_formda_dort_alan_bulunur(client):
    html = client.get("/").get_data(as_text=True)
    for alan in ["ad_soyad", "departman", "dogum_tarihi", "ise_baslama_tarihi"]:
        assert f'name="{alan}"' in html


# Kabul kriteri 2: Geçerli kayıt listede görünür.
def test_gecerli_kayit_listede_gorunur(client):
    yanit = client.post("/", data=gecerli_veri(), follow_redirects=True)
    html = yanit.get_data(as_text=True)
    assert yanit.status_code == 200
    assert "Ayşe Yılmaz" in html
    assert "Muhasebe" in html
    assert "1990-05-12" in html
    assert "2020-03-01" in html


# Kabul kriteri 3: Boş ad soyad reddedilir.
@pytest.mark.parametrize("ad_soyad", ["", "   "])
def test_bos_ad_soyad_reddedilir(client, ad_soyad):
    yanit = client.post("/", data=gecerli_veri(ad_soyad=ad_soyad))
    html = yanit.get_data(as_text=True)
    assert yanit.status_code == 400
    assert "Ad soyad boş bırakılamaz." in html
    assert "Henüz kayıtlı çalışan yok." in html  # Kayıt yapılmadı


# Kabul kriteri 4: Gelecek tarihli işe başlama reddedilir.
def test_gelecek_tarihli_ise_baslama_reddedilir(client):
    yarin = (date.today() + timedelta(days=1)).isoformat()
    yanit = client.post("/", data=gecerli_veri(ise_baslama_tarihi=yarin))
    html = yanit.get_data(as_text=True)
    assert yanit.status_code == 400
    assert "İşe başlama tarihi bugünden ileri bir tarih olamaz." in html
    assert "Henüz kayıtlı çalışan yok." in html  # Kayıt yapılmadı


def test_hata_olunca_form_degerleri_korunur(client):
    yanit = client.post("/", data=gecerli_veri(ad_soyad=""))
    html = yanit.get_data(as_text=True)
    assert 'value="Muhasebe"' in html
    assert 'value="1990-05-12"' in html


# Doğrulama fonksiyonunun doğrudan testleri
def test_dogrula_gecerli_veride_hata_yok():
    assert calisan_dogrula(gecerli_veri()) == []


def test_dogrula_bugun_ise_baslama_kabul_edilir():
    bugun = date(2026, 1, 15)
    veri = gecerli_veri(ise_baslama_tarihi="2026-01-15")
    assert calisan_dogrula(veri, bugun=bugun) == []


def test_dogrula_yarin_ise_baslama_reddedilir():
    bugun = date(2026, 1, 15)
    veri = gecerli_veri(ise_baslama_tarihi="2026-01-16")
    assert calisan_dogrula(veri, bugun=bugun) == [
        "İşe başlama tarihi bugünden ileri bir tarih olamaz."
    ]
