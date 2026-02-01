@echo off
echo Raporcu Web Uygulamasını Başlatma
echo ===============================

:: Python kontrolü
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python kurulamadı. Lütfen Python 3.7 veya üstünü yükleyin.
    pause
    exit /b 1
)

:: Gerekli paketleri kur
echo Gerekli paketler yükleniyor...
pip install -r requirements_web.txt
if %errorlevel% neq 0 (
    echo Paket kurulumu başarısız oldu.
    pause
    exit /b 1
)

:: Uygulama klasörüne git
cd /d "%~dp0"

:: Web sunucusunu başlat
echo Web uygulaması başlatılıyor...
echo Uygulamaya http://localhost:5000 adresinden erişebilirsiniz.
echo Kapatmak için CTRL+C tuşlarına basın.
python web_app.py

pause
