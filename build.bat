@echo off
echo ========================================
echo   Raporcu EXE Builder
echo ========================================
echo.

REM Virtual environment'i aktif et (varsa)
if exist venv\Scripts\activate.bat (
    echo Virtual environment aktif ediliyor...
    call venv\Scripts\activate.bat
)

REM PyInstaller yoksa yükle
echo PyInstaller kontrol ediliyor...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller bulunamadi, yukleniyor...
    pip install pyinstaller
)

REM Build scripti calistir
echo.
echo Build baslatiiliyor...
python build_exe.py

echo.
echo ========================================
echo   Build tamamlandi!
echo ========================================
echo.
echo dist\Raporcu.exe dosyasini test edebilirsiniz.
echo.
pause
