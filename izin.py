"""Yıllık izin hakkı hesaplama (4857 sayılı İş Kanunu, madde 53)."""

from datetime import date


def tam_yil(baslangic, bugun):
    """İki tarih arasındaki tam yıl sayısını döndürür.

    Yıldönümü bu yıl henüz gelmediyse o yıl sayılmaz.
    Ay ve gün karşılaştırıldığı için 29 Şubat'ta hata oluşmaz:
    artık olmayan yıllarda yıldönümü 1 Mart'ta dolmuş sayılır.
    """
    yil = bugun.year - baslangic.year
    if (bugun.month, bugun.day) < (baslangic.month, baslangic.day):
        yil -= 1
    return yil


def kidem_hesapla(ise_baslama_tarihi, bugun):
    return tam_yil(ise_baslama_tarihi, bugun)


def yas_hesapla(dogum_tarihi, bugun):
    return tam_yil(dogum_tarihi, bugun)


def yillik_izin_hakki(dogum_tarihi, ise_baslama_tarihi, bugun=None):
    """Çalışanın yıllık izin hakkını gün olarak döndürür."""
    if bugun is None:
        bugun = date.today()

    kidem = kidem_hesapla(ise_baslama_tarihi, bugun)
    yas = yas_hesapla(dogum_tarihi, bugun)

    # Kural 1: Kıdem 1 yıldan azsa izin hakkı doğmamıştır.
    if kidem < 1:
        return 0

    # Kural 2-4: Kıdeme göre gün sayısı.
    if kidem <= 5:
        gun = 14
    elif kidem < 15:
        gun = 20
    else:
        gun = 26

    # Kural 5: 18 yaşından küçükler ve 50 yaş ve üzeri en az 20 gün alır.
    if yas < 18 or yas >= 50:
        gun = max(gun, 20)

    return gun
