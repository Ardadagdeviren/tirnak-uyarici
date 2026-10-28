# PyInstaller yapılandırması: pyinstaller tirnak_uyarici.spec
# Windows'ta çalıştırılınca dist/TirnakUyarici/TirnakUyarici.exe üretir.
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas = [("models/*.task", "models")] + collect_data_files("mediapipe")
binaries = collect_dynamic_libs("mediapipe")

a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    # matplotlib dışlanmamalı: mediapipe.tasks.python.vision onu içe aktarıyor.
    excludes=["tkinter", "PySide6.QtWebEngineCore", "PySide6.Qt3DCore"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TirnakUyarici",
    console=False,  # Konsol penceresi açılmasın
)
coll = COLLECT(exe, a.binaries, a.datas, name="TirnakUyarici")
