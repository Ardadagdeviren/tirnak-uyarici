# Tırnak Uyarıcı

Bilgisayar başındayken kamerayı izler; elin ağzına gidip yarım saniye kadar orada kalırsa
ekran kırmızı parlar ve **"Elini ağzından çek!"** uyarısı çıkar. Uyarı tüm pencerelerin
üstünde görünür ama tıklamaları engellemez, yani çalışmanı bölmez.

Görüntü hiçbir yere gönderilmez ve kaydedilmez; tüm işlem bilgisayarında yapılır.

---

## Windows'ta kurulum

Kurulum dört adım: Python'u kur, `build_windows.bat`'ı çalıştır, exe'ye kısayol oluştur,
otomatik başlatmayı aç. `build_windows.bat` **yalnızca bir kez** çalıştırılır; sonrasında
program her zaman exe'den (ya da kısayolundan) açılır.

### 1. Python'u kur (bir kez)

[python.org](https://www.python.org/downloads/windows/) adresinden **Python 3.12** indirip kur.
Kurulumun ilk ekranında **"Add python.exe to PATH"** kutusunu mutlaka işaretle.

### 2. `build_windows.bat` ile exe'yi oluştur

1. Bu sayfada **Code** → **Download ZIP** ile projeyi indir.
2. Zip'e sağ tıkla → **Tümünü ayıkla…** → örneğin `C:\Programlar\TirnakUyarici` klasörüne çıkar.
   > Zip'in içinden çalıştırma; önce mutlaka klasöre çıkar.
3. Çıkan klasördeki **`build_windows.bat`** dosyasına çift tıkla.
4. Pencere adım adım `[1/5] … [5/5]` ilerler; ilk seferde paketler indiği için birkaç dakika sürer.
   Sonunda **"HAZIR"** yazar ve `dist\TirnakUyarici` klasörü kendiliğinden açılır.
   İçinde **`TirnakUyarici.exe`** vardır.

Bir sorun olursa pencere kapanmaz ve nedenini yazar (Python yok, zip çıkarılmamış,
antivirüs exe'yi silmiş vb.). O ekranın görüntüsünü göndermen yeterli.

### 3. Kısayol oluştur ve istediğin yere taşı

1. `dist\TirnakUyarici` klasöründeki **`TirnakUyarici.exe`**'ye sağ tıkla →
   **Diğer seçenekleri göster** → **Kısayol oluştur**.
2. Oluşan kısayolu istediğin yere taşı: masaüstü, görev çubuğu, Başlat menüsü…
   Bundan sonra programı hep bu kısayoldan açarsın.

> Exe'yi tek başına klasörün dışına taşıma; yanındaki `_internal` klasörüne ihtiyaç duyar.
> Taşımak istediğin şey **kısayol** olsun.

İlk açılışta **"Windows bilgisayarınızı korudu"** mavi ekranı çıkarsa: **Ek bilgi** →
**Yine de çalıştır** (program imzalı olmadığı için Windows bir kez böyle uyarır).
Açılınca sağ alttaki saatin yanında kırmızı yuvarlak bir simge belirir; görünmüyorsa
**^** (gizli simgeler) okuna tıkla.

Denemek için simgeye sağ tıkla → **Uyarıyı test et**: kırmızı parlamayı görürsün.
Simgeye **çift tıklarsan** kamera önizlemesi açılır; elini ağzına götürünce noktaların
kırmızıya döndüğünü görebilirsin.

### 4. Bilgisayar her açıldığında otomatik başlat

Simgeye sağ tıkla → **Ayarlar…** → **Windows açılınca otomatik başlat** kutusunu işaretle →
**Kaydet**. Artık bilgisayar her açıldığında program arka planda kendiliğinden başlar.
Kapatmak için aynı kutunun işaretini kaldırman yeterli.

> Bu ayar exe'nin bulunduğu yeri kaydeder. Proje klasörünü sonradan başka yere taşırsan
> kutunun işaretini kaldırıp yeniden işaretle.

### Sorun giderme

| Sorun | Çözüm |
|---|---|
| "Kamera açılamadı" bildirimi | Zoom, Teams, Discord gibi kamerayı kullanan bir program açıksa kapat, sonra menüden **Devam et**. |
| Kamera hiç açılmıyor | **Ayarlar → Gizlilik ve güvenlik → Kamera** içinde **Kamera erişimi** ve **Masaüstü uygulamalarının kameranıza erişmesine izin ver** açık olmalı. |
| Birden fazla kamera var, yanlışı açılıyor | **Ayarlar…** → **Kamera** değerini 1, 2… yap. |
| Uyarı geç geliyor / hiç gelmiyor | **Hassasiyet**'i artır ya da **Uyarı için bekleme** süresini kısalt. Önizlemede yüzünün algılandığından emin ol (ışık arkadan geliyorsa yüz bulunamayabilir). |
| Çenemi tutarken bile uyarıyor | **Hassasiyet**'i azalt. |
| Antivirüs .exe'yi engelliyor | PyInstaller ile üretilen imzasız programlarda olabilir; dosyayı ya da proje klasörünü istisnalara ekleyip `build_windows.bat`'ı yeniden çalıştır. |
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

## Geliştiriciler için

Testler: `pip install -r requirements-dev.txt` ardından `python -m pytest --cov=tirnak_uyarici`.
GitHub Actions her gönderimde testleri çalıştırır ve exe'yi Windows'ta `build_windows.bat` ile
üretip `--self-test` ile sınar.

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
