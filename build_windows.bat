@echo off
REM Tirnak Uyarici - Windows icin .exe uretir.
REM Cift tiklayarak calistir. Sonuc: dist\TirnakUyarici\TirnakUyarici.exe
setlocal EnableExtensions
cd /d "%~dp0"
title Tirnak Uyarici - exe derleme

if not exist "requirements.txt" goto :not_extracted
if not exist "tirnak_uyarici.spec" goto :not_extracted

echo.
echo [1/5] Python araniyor...
set "PY="
for %%V in (3.12 3.13 3.11 3.14 3.10) do (
    if not defined PY (
        py -%%V -c "import sys" >nul 2>&1 && set "PY=py -%%V"
    )
)
if not defined PY (
    python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1 && set "PY=python"
)
if not defined PY goto :no_python
echo Kullanilan Python:
%PY% --version

echo.
echo [2/5] Sanal ortam hazirlaniyor...
if not exist ".venv\Scripts\python.exe" (
    %PY% -m venv .venv || goto :fail
)
set "VPY=%CD%\.venv\Scripts\python.exe"

echo.
echo [3/5] Paketler kuruluyor (ilk seferde birkac dakika surebilir)...
"%VPY%" -m pip --version >nul 2>&1 || "%VPY%" -m ensurepip --upgrade >nul 2>&1
"%VPY%" -m pip install --upgrade pip || goto :fail
"%VPY%" -m pip install -r requirements.txt pyinstaller || goto :fail

echo.
echo [4/5] Model dosyalari kontrol ediliyor...
if not exist "models" mkdir models
if not exist "models\hand_landmarker.task" (
    curl -sSfL -o "models\hand_landmarker.task" https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task || goto :fail
)
if not exist "models\face_landmarker.task" (
    curl -sSfL -o "models\face_landmarker.task" https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task || goto :fail
)

echo.
echo [5/5] exe uretiliyor...
"%VPY%" -m PyInstaller --noconfirm --clean tirnak_uyarici.spec || goto :fail
if not exist "dist\TirnakUyarici\TirnakUyarici.exe" goto :missing_exe

echo.
echo exe sinaniyor (kamera acilmaz)...
start "" /wait "dist\TirnakUyarici\TirnakUyarici.exe" --self-test
if errorlevel 1 goto :self_test_failed
echo Sinama basarili.

echo.
echo ============================================================
echo  HAZIR: %CD%\dist\TirnakUyarici\TirnakUyarici.exe
echo  TirnakUyarici klasorunun tamamini istedigin yere tasiyabilirsin.
echo ============================================================
if not defined CI explorer "dist\TirnakUyarici"
goto :end_ok

:not_extracted
echo.
echo HATA: Proje dosyalari bulunamadi.
echo Zip dosyasini once bir klasore cikar (sag tik ^> Tumunu ayikla),
echo sonra cikan klasordeki build_windows.bat dosyasini calistir.
goto :end_fail

:no_python
echo.
echo HATA: Python 3.10 veya daha yenisi bulunamadi.
echo https://www.python.org/downloads/windows/ adresinden Python 3.12 indir.
echo Kurulumun ilk ekraninda "Add python.exe to PATH" kutusunu isaretle,
echo kurulum bitince bu dosyayi tekrar calistir.
goto :end_fail

:missing_exe
echo.
echo HATA: Derleme bitti ama TirnakUyarici.exe olusmadi.
echo Buyuk ihtimalle antivirus (Windows Defender) dosyayi sildi.
echo Windows Guvenligi ^> Virus ve tehdit korumasi ^> Koruma gecmisi
echo bolumunden dosyaya izin ver ya da bu klasoru dislamalara ekle.
goto :end_fail

:self_test_failed
echo.
echo HATA: exe olustu ama sinamada calismadi.
echo Ayrintilar: %APPDATA%\TirnakUyarici\uygulama.log
if defined CI type "%APPDATA%\TirnakUyarici\uygulama.log"
goto :end_fail

:fail
echo.
echo HATA: Yukaridaki adimda bir sorun olustu.
echo Ekrandaki son hata satirlarinin fotografini/metnini gonderirsen yardimci olabilirim.
goto :end_fail

:end_fail
if not defined CI pause
exit /b 1

:end_ok
if not defined CI pause
exit /b 0
