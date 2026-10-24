@echo off
REM Windows'ta .exe üretir. Python 3.10-3.12 kurulu olmalı.
setlocal
cd /d "%~dp0"

if not exist .venv (
    py -3.12 -m venv .venv || python -m venv .venv || goto :error
)
call .venv\Scripts\activate.bat || goto :error
python -m pip install --upgrade pip || goto :error
pip install -r requirements-dev.txt || goto :error

if not exist models\hand_landmarker.task (
    curl -sSfL -o models\hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task || goto :error
)
if not exist models\face_landmarker.task (
    curl -sSfL -o models\face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task || goto :error
)

python -m pytest -q || goto :error
pyinstaller --noconfirm --clean tirnak_uyarici.spec || goto :error

echo.
echo Hazir: dist\TirnakUyarici\TirnakUyarici.exe
exit /b 0

:error
echo Derleme basarisiz oldu.
exit /b 1
