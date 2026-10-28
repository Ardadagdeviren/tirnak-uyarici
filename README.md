# Tırnak Uyarıcı

Bilgisayar başında çalışırken farkında olmadan tırnak mı yiyorsun? Tırnak Uyarıcı kameranla
seni izler. Elin ağzına gittiği anda ekran kırmızı yanıp söner ve **"Elini ağzından çek!"**
yazısı çıkar.

- Uyarı açık olan her şeyin üstünde görünür, ama işini bölmez; tıklamaya ve yazmaya devam edebilirsin.
- Kamera görüntün hiçbir yere gönderilmez, kaydedilmez. Her şey kendi bilgisayarında kalır.
- Saatin yanında küçük bir simge olarak sessizce çalışır.

---

## Kurulum

Kurulum yalnızca bir kez yapılır, yaklaşık 10 dakika sürer.

### 1. Python'u kur

[python.org](https://www.python.org/downloads/windows/) adresinden **Python 3.12**'yi indirip kur.

> Kurulumun ilk ekranında **"Add python.exe to PATH"** kutusunu mutlaka işaretle.

### 2. Programı oluştur

1. Bu sayfanın üstündeki yeşil **Code** düğmesine, ardından **Download ZIP**'e tıkla.
2. İnen dosyaya sağ tıkla → **Tümünü ayıkla…** ile bir klasöre çıkar
   (örneğin `C:\Programlar\TirnakUyarici`).
3. Çıkan klasördeki **`build_windows.bat`** dosyasına çift tıkla.
4. Siyah bir pencere açılır ve birkaç dakika çalışır. Bitince **HAZIR** yazar ve içinde
   **`TirnakUyarici.exe`** bulunan bir klasör kendiliğinden açılır.

Bu adımı bir daha yapman gerekmez.

### 3. Kısayol oluştur

1. **`TirnakUyarici.exe`**'ye sağ tıkla → **Diğer seçenekleri göster** → **Kısayol oluştur**.
2. Oluşan kısayolu istediğin yere taşı: masaüstü, görev çubuğu…

Programı artık hep bu kısayoldan açarsın.

> `TirnakUyarici.exe`'nin kendisini bulunduğu klasörden çıkarma; yanındaki dosyalarla birlikte çalışır.

### 4. Bilgisayar açılınca kendiliğinden başlasın

1. Programı aç. Sağ alttaki saatin yanında **kırmızı yuvarlak bir simge** belirir.
   (Görmüyorsan saatin yanındaki **^** okuna tıkla.)
2. Simgeye sağ tıkla → **Ayarlar…**
3. **Windows açılınca otomatik başlat** kutusunu işaretle → **Kaydet**.

Hepsi bu. Artık bilgisayarını her açtığında Tırnak Uyarıcı kendiliğinden çalışır.

---

## Kullanım

Kırmızı simgeye **sağ tıklayınca** şunlar çıkar:

| Seçenek | Ne işe yarar |
|---|---|
| **Duraklat / Devam et** | Uyarıları bir süre kapatır, kamera da kapanır. Görüntülü görüşmeye girerken işine yarar. |
| **Kamera önizlemesi…** | Kameranın seni nasıl gördüğünü gösterir. Elin ağzına yaklaşınca noktalar kırmızıya döner. |
| **Uyarıyı test et** | Kırmızı uyarının nasıl göründüğünü hemen gösterir. |
| **Ayarlar…** | Aşağıdaki ayarları değiştirir. |
| **Çıkış** | Programı kapatır. |

### Ayarlar

| Ayar | Ne değiştirir |
|---|---|
| **Hassasiyet** | Yüksek: elin ağzına yaklaşınca bile uyarır. Düşük: sadece elin ağzına değince uyarır. |
| **Uyarı için bekleme** | Elin ağzında ne kadar kalınca uyarı versin. Kısa yaparsan daha çabuk uyarır. |
| **Tekrar uyarı aralığı** | Elin ağzında kalmaya devam ederse kaç saniyede bir tekrar uyarsın. |
| **Uyarıda ses çal** | Kırmızı uyarıyla birlikte kısa bir ses de çalar. |
| **Kamera** | Birden fazla kameran varsa hangisinin kullanılacağı. Genelde 0 doğrudur. |
| **Windows açılınca otomatik başlat** | Bilgisayar açılınca program kendiliğinden başlar. |

---

## Sorun mu var?

| Sorun | Ne yapmalı |
|---|---|
| Ekranda **"Windows bilgisayarınızı korudu"** yazıyor | **Ek bilgi** → **Yine de çalıştır**. Bu uyarı yalnızca ilk açılışta çıkar. |
| **"Kamera açılamadı"** diyor | Zoom, Teams, Discord gibi kamerayı kullanan bir program açıksa kapat, sonra simgeden **Devam et**. |
| Kamera hiç açılmıyor | Windows **Ayarlar → Gizlilik ve güvenlik → Kamera** bölümünde kamera erişimini aç. |
| Uyarı geç geliyor ya da hiç gelmiyor | **Hassasiyet**'i artır. Yüzünün iyi aydınlandığından emin ol; arkandan gelen ışık seni görmeyi zorlaştırır. |
| Çeneme dokununca bile uyarıyor | **Hassasiyet**'i azalt. |
| Oyun oynarken kırmızı uyarı görünmüyor | Tam ekran oyunlar her şeyin üstünde durur, ama sesli uyarı yine çalar. |
| `build_windows.bat` hata verdi | Pencerede ne yapman gerektiği yazar. Çözemezsen o ekranın fotoğrafını gönder. |
