#!/bin/bash
# Tırnak Uyarıcı - Mac için TirnakUyarici.app üretir.
# Çift tıklayarak ya da Terminal'de "bash build_mac.command" ile çalıştır.
set -uo pipefail
cd "$(dirname "$0")" || exit 1

HAND_URL="https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
FACE_URL="https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
APP="dist/TirnakUyarici.app"

finish() {
    [ -z "${CI:-}" ] && read -r -p "Kapatmak için Enter'a bas..." _
    exit "$1"
}

fail() {
    echo
    echo "HATA: $1"
    finish 1
}

if [ ! -f requirements.txt ] || [ ! -f tirnak_uyarici.spec ]; then
    fail "Proje dosyaları bulunamadı. Zip'i önce bir klasöre çıkar, sonra bu dosyayı oradan çalıştır."
fi

echo
echo "[1/5] Python aranıyor..."
PY=""
for candidate in python3.12 python3.13 python3.11 python3.14 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 \
        && "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >/dev/null 2>&1; then
        PY="$candidate"
        break
    fi
done
[ -n "$PY" ] || fail "Python 3.10 veya daha yenisi bulunamadı. https://www.python.org/downloads/macos/ adresinden Python 3.12 kur, sonra bu dosyayı tekrar çalıştır."
"$PY" --version

echo
echo "[2/5] Sanal ortam hazırlanıyor..."
if [ ! -x .venv/bin/python ]; then
    "$PY" -m venv .venv || fail "Sanal ortam oluşturulamadı."
fi
VPY="$PWD/.venv/bin/python"

echo
echo "[3/5] Paketler kuruluyor (ilk seferde birkaç dakika sürebilir)..."
"$VPY" -m pip --version >/dev/null 2>&1 || "$VPY" -m ensurepip --upgrade >/dev/null 2>&1
"$VPY" -m pip install --upgrade pip || fail "pip güncellenemedi."
"$VPY" -m pip install -r requirements.txt pyinstaller || fail "Paketler kurulamadı. İnternet bağlantını kontrol et."

echo
echo "[4/5] Model dosyaları kontrol ediliyor..."
mkdir -p models
[ -f models/hand_landmarker.task ] || curl -sSfL -o models/hand_landmarker.task "$HAND_URL" || fail "El modeli indirilemedi."
[ -f models/face_landmarker.task ] || curl -sSfL -o models/face_landmarker.task "$FACE_URL" || fail "Yüz modeli indirilemedi."

echo
echo "[5/5] Uygulama oluşturuluyor..."
"$VPY" -m PyInstaller --noconfirm --clean tirnak_uyarici.spec || fail "Uygulama oluşturulamadı."
[ -d "$APP" ] || fail "Derleme bitti ama TirnakUyarici.app oluşmadı."
# İndirilen zip'ten gelen "internetten indirildi" işaretini kaldır; yoksa macOS açılışı engelleyebilir.
xattr -cr "$APP" 2>/dev/null

echo
echo "Uygulama sınanıyor (kamera açılmaz)..."
"$APP/Contents/MacOS/TirnakUyarici" --self-test >/dev/null 2>&1 \
    || fail "Uygulama oluştu ama sınamada çalışmadı. Ayrıntılar: ~/.config/TirnakUyarici/uygulama.log"
echo "Sınama başarılı."

echo
echo "============================================================"
echo " HAZIR: $PWD/$APP"
echo " Uygulamayı Uygulamalar (Applications) klasörüne sürükleyebilirsin."
echo "============================================================"
[ -z "${CI:-}" ] && open dist
finish 0
