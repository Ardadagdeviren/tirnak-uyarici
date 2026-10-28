# Tırnak Uyarıcı

Bilgisayar başındayken kamerayı izler; elin ağzına gidip yarım saniye kadar orada kalırsa
ekran kırmızı parlar ve **"Elini ağzından çek!"** uyarısı çıkar. Uyarı tüm pencerelerin
üstünde görünür ama tıklamaları engellemez, yani çalışmanı bölmez.

Görüntü hiçbir yere gönderilmez ve kaydedilmez; tüm işlem bilgisayarında yapılır.

---

## Windows'ta çalıştırma

Üç yol var. Programcı değilsen **1. yol** yeterli.

### 1. yol: Hazır programı indir (en kolay)

1. Bu sayfanın sağındaki **Releases** bölümüne tıkla (ya da depo adresinin sonuna `/releases` ekle).
2. En üstteki sürümden **`TirnakUyarici-windows.zip`** dosyasını indir.
3. Zip'e sağ tıkla → **Tümünü ayıkla…** → örneğin `C:\Programlar\TirnakUyarici` klasörüne çıkar.
   > Zip'in içinden doğrudan çalıştırma; önce mutlaka klasöre çıkar.
4. Çıkan klasördeki **`TirnakUyarici.exe`** dosyasına çift tıkla.
5. **"Windows bilgisayarınızı korudu"** mavi ekranı çıkarsa: **Ek bilgi** → **Yine de çalıştır**.
   (Program imzalı olmadığı için Windows ilk seferde böyle uyarır.)
6. Sağ alttaki saatin yanında kırmızı yuvarlak bir simge belirir. Görünmüyorsa **^** (gizli
   simgeler) okuna tıkla; simgeyi sürükleyip görev çubuğuna sabitleyebilirsin.

İlk denemede simgeye sağ tıklayıp **Uyarıyı test et**'i seç; kırmızı parlamayı görürsün.
Ardından simgeye **çift tıkla**: kamera önizlemesi açılır, elini ağzına götürünce noktaların
kırmızıya döndüğünü görebilirsin.

**Her açılışta otomatik başlasın istersen:** simgeye sağ tıkla → **Ayarlar…** →
**Windows açılınca otomatik başlat** → **Kaydet**.

### 2. yol: Kaynak koddan çalıştır

1. [python.org](https://www.python.org/downloads/windows/) adresinden **Python 3.12** indirip kur.
   Kurulumun ilk ekranında **"Add python.exe to PATH"** kutusunu işaretle.
2. Bu sayfada **Code** → **Download ZIP** ile projeyi indir ve bir klasöre çıkar
   (ya da `git clone` ile al). Klasör yolunda Türkçe karakter olmamasına dikkat et.
3. O klasörde adres çubuğuna `cmd` yazıp Enter'a bas; açılan pencerede sırayla:

   ```bat
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python -m tirnak_uyarici
   ```

   Sonraki açılışlarda sadece son iki satır yeterli
   (`.venv\Scripts\activate` ve `python -m tirnak_uyarici`).

### 3. yol: Kendin .exe üret

> Hazır programı 1. yoldan indirebildiğin için bu adım zorunlu değil.

1. **Python 3.12** kurulu olmalı (2. yolun 1. adımı).
2. Projeyi **Code → Download ZIP** ile indir ve **önce bir klasöre çıkar**
   (zip'in içinden çalıştırırsan dosyalar bulunamaz).
3. Çıkan klasördeki **`build_windows.bat`** dosyasına çift tıkla.
4. Pencere adım adım `[1/5] … [5/5]` ilerler; ilk seferde paket indirme birkaç dakika sürer.
   Bitince `dist\TirnakUyarici` klasörü kendiliğinden açılır, içinde **`TirnakUyarici.exe`** vardır.
   `TirnakUyarici` klasörünün tamamını istediğin yere taşıyabilirsin.

Bir sorun olursa pencere kapanmaz; nedenini yazar (Python yok, zip çıkarılmamış,
antivirüs exe'yi silmiş vb.). O ekranın görüntüsünü göndermen yeterli.

### Sorun giderme

| Sorun | Çözüm |
|---|---|
| "Kamera açılamadı" bildirimi | Zoom, Teams, Discord gibi kamerayı kullanan bir program açıksa kapat, sonra menüden **Devam et**. |
| Kamera hiç açılmıyor | **Ayarlar → Gizlilik ve güvenlik → Kamera** içinde **Kamera erişimi** ve **Masaüstü uygulamalarının kameranıza erişmesine izin ver** açık olmalı. |
| Birden fazla kamera var, yanlışı açılıyor | **Ayarlar…** → **Kamera** değerini 1, 2… yap. |
| Uyarı geç geliyor / hiç gelmiyor | **Hassasiyet**'i artır ya da **Uyarı için bekleme** süresini kısalt. Önizlemede yüzünün algılandığından emin ol (ışık arkadan geliyorsa yüz bulunamayabilir). |
| Çenemi tutarken bile uyarıyor | **Hassasiyet**'i azalt. |
| Antivirüs .exe'yi engelliyor | PyInstaller ile üretilen imzasız programlarda olabilir; dosyayı istisnalara ekle ya da 2. yolu kullan. |
| Oyun tam ekrandayken parlama görünmüyor | Tam ekran oyunlar her şeyin üstünde durur; sesli uyarı yine çalar. Oyunu "pencereli tam ekran" modunda açarsan parlama da görünür. |

Ayarlar `%APPDATA%\TirnakUyarici\config.json`, günlük dosyası `%APPDATA%\TirnakUyarici\uygulama.log`
içinde durur. Sorun bildirirken günlük dosyasını eklemek işe yarar.

---

## Kullanım

Sistem tepsisindeki simgeye **sağ tıklayınca**:

| Menü | Ne yapar |
|---|---|
| Duraklat / Devam et | Kamerayı tamamen kapatır / yeniden açar |
| Kamera önizlemesi… | Algılanan el ve ağız noktalarını canlı gösterir (simgeye çift tıklamak da açar) |
| Uyarıyı test et | Kırmızı parlamayı hemen gösterir |
| Ayarlar… | Kamera, hassasiyet, bekleme süresi, ses, Windows ile başlatma |
| Çıkış | Uygulamayı kapatır |

Kamera önizlemesindeki **Oran** değeri **Eşik** değerinin altına düştüğünde el ağızda sayılır.

## Geliştirme (Mac / Windows / Linux)

Python 3.10 veya daha yenisi gerekir (3.12 önerilir).

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m tirnak_uyarici           # uygulamayı başlat
python -m pytest --cov=tirnak_uyarici
```

**Yeni sürüm yayınlamak:** `git tag v0.2.0 && git push origin v0.2.0` — GitHub Actions Windows'ta
testleri çalıştırır, `.exe`'yi üretir ve zip'i Releases sayfasına koyar. `main` dalına yapılan
her gönderimde de derleme yapılır; zip'i Actions sekmesinden indirebilirsin.

> PyInstaller başka bir işletim sistemi için derleme yapamaz; `.exe` her zaman Windows'ta üretilir.

## Nasıl çalışır?

1. **MediaPipe** her karede elin 21, yüzün 478 noktasını bulur.
2. Parmak uçları ile dudak noktaları arasındaki en kısa mesafe, iki göz arasındaki mesafeye
   bölünür. Böylece kameraya yakın/uzak oturmak sonucu değiştirmez.
3. El, yüzden çok daha büyük görünüyorsa (kameranın önünden geçiyorsa) yok sayılır.
4. Oran eşiğin altında **ve** belirlenen süre boyunca kalırsa uyarı verilir; ardından birkaç
   saniye tekrar uyarı verilmez.
5. El ağzı kapatınca yüz algılaması kaybolabilir; bu yüzden ağzın son konumu 1 saniye hatırlanır.

| Dosya | Görev |
|---|---|
| `gesture_logic.py` | Mesafe, eşik, süre ve bekleme mantığı (saf fonksiyonlar, test edilebilir) |
| `detector.py` | MediaPipe el + yüz tespiti |
| `camera_worker.py` | Kamerayı arka planda okuyan iş parçacığı |
| `alert_overlay.py` | Her ekranda kırmızı parlama penceresi |
| `tray_app.py` | Sistem tepsisi menüsü ve parçaların bağlantısı |
| `settings_dialog.py` | Ayarlar penceresi |
| `config.py` | Ayarlar (`%APPDATA%\TirnakUyarici\config.json`) |
| `platform_utils.py` | Windows uyarı sesi ve açılışta başlatma |

Model dosyaları (`models/*.task`) Google MediaPipe'ın resmi modelleridir.
