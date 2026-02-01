@echo off
setlocal enabledelayedexpansion
title Raporcu Kurulum Sihirbazı
color 0A

echo =================================================
echo    Raporcu - AI Destekli Rapor Yazım Uygulaması
echo                Kurulum Sihirbazı
echo =================================================
echo.

:: Python kontrolü
echo Python sürüm kontrolü yapılıyor...
python --version 2>NUL
if errorlevel 1 (
    echo [!] Python bulunamadı! Python 3.11 veya üzeri gereklidir.
    echo     https://www.python.org/downloads/ adresinden indirebilirsiniz.
    pause
    exit /b 1
)

:: Gerekli klasörleri oluştur
echo Gerekli klasörler oluşturuluyor...
if not exist "audio_files" mkdir audio_files
if not exist "temp" mkdir temp

:: Sanal ortam opsiyonu
echo.
echo Kurulum yöntemi seçiniz:
echo 1. Sanal ortam kullanarak kurulum (önerilen)
echo 2. Doğrudan sistem Python'ına kurulum
echo.
set /p install_type="Seçiminiz (1/2): "

set use_venv=0
if "%install_type%"=="1" (
    set use_venv=1
    
    :: Sanal ortam kontrolü ve oluşturma
    if exist venv (
        echo Mevcut sanal ortam bulundu. Yeniden oluşturmak ister misiniz? (E/H)
        set /p rebuild=
        if /i "!rebuild!"=="E" (
            echo Mevcut sanal ortam kaldırılıyor...
            rmdir /s /q venv
            echo Yeni sanal ortam oluşturuluyor...
            python -m venv venv
        )
    ) else (
        echo Sanal ortam oluşturuluyor...
        python -m venv venv
    )

    :: Sanal ortamı etkinleştir
    echo Sanal ortam etkinleştiriliyor...
    call venv\Scripts\activate.bat
)

:: Pip'i güncelle
echo Pip güncelleniyor...
python -m pip install --upgrade pip

:: FFmpeg dosyalarını kopyala
echo FFmpeg kurulumu yapılıyor...

:: Proje içindeki FFmpeg dosyalarının varlığını kontrol et
if exist "ffmpeg-N-119584-g06cee0c681-win64-gpl\bin\ffmpeg.exe" (
    echo Proje içinde FFmpeg bulundu, kopyalanıyor...
    
    if "%use_venv%"=="1" (
        :: Sanal ortama kopyala
        echo FFmpeg dosyaları sanal ortama kopyalanıyor...
        xcopy "ffmpeg-N-119584-g06cee0c681-win64-gpl\bin\*" "venv\Scripts\" /Y
    ) else (
        :: Kullanıcı dizinine kopyala
        echo FFmpeg dosyaları kullanıcı dizinine kopyalanıyor...
        if not exist "%USERPROFILE%\FFmpeg" mkdir "%USERPROFILE%\FFmpeg"
        xcopy "ffmpeg-N-119584-g06cee0c681-win64-gpl\bin\*" "%USERPROFILE%\FFmpeg\" /Y
        
        :: PATH'e ekleme
        echo PATH değişkeni güncelleniyor...
        setx PATH "%PATH%;%USERPROFILE%\FFmpeg"
        echo NOT: FFmpeg'in PATH değişkenine eklenmesi için komut istemi penceresini kapatıp yeniden açmanız gerekebilir.
    )
    
    echo FFmpeg kurulumu tamamlandı.
) else (
    :: FFmpeg kontrolü
    echo FFmpeg proje içinde bulunamadı, sistem kontrolü yapılıyor...
    where ffmpeg >nul 2>nul
    if errorlevel 1 (
        echo [!] FFmpeg bulunamadı! Ses işleme için gereklidir.
        echo     FFmpeg indirilip kurulsun mu? (E/H)
        set /p install_ffmpeg=
        
        if /i "!install_ffmpeg!"=="E" (
            echo FFmpeg indiriliyor ve kuruluyor...
            
            :: FFmpeg indirme ve kurma işlemleri
            if not exist "temp\ffmpeg" mkdir temp\ffmpeg
            powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'temp\ffmpeg.zip'}"
            
            echo FFmpeg dosyaları çıkartılıyor...
            powershell -Command "& {Expand-Archive -Path 'temp\ffmpeg.zip' -DestinationPath 'temp\ffmpeg' -Force}"
            
            if "%use_venv%"=="1" (
                :: Sanal ortama kopyala
                echo FFmpeg dosyaları sanal ortama kopyalanıyor...
                xcopy "temp\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\*" "venv\Scripts\" /Y
            ) else (
                :: Sistem yoluna ekle
                echo FFmpeg dosyaları sistem yoluna ekleniyor...
                if not exist "%USERPROFILE%\FFmpeg" mkdir "%USERPROFILE%\FFmpeg"
                xcopy "temp\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\*" "%USERPROFILE%\FFmpeg\" /Y
                
                :: PATH'e ekleme
                echo PATH değişkeni güncelleniyor...
                setx PATH "%PATH%;%USERPROFILE%\FFmpeg"
                echo NOT: FFmpeg'in PATH değişkenine eklenmesi için komut istemi penceresini kapatıp yeniden açmanız gerekebilir.
            )
            
            echo FFmpeg kurulumu tamamlandı.
            del /q "temp\ffmpeg.zip"
            rmdir /s /q "temp\ffmpeg"
        ) else (
            echo [!] FFmpeg kurulmadı. Ses işleme özellikleri çalışmayabilir.
            echo     https://ffmpeg.org/download.html adresinden manuel kurulum yapabilirsiniz.
        )
    ) else (
        echo FFmpeg sistemde zaten yüklü, kurulum atlanıyor...
    )
)

:: Gerekli kütüphaneleri yükle
echo Gerekli kütüphaneler yükleniyor...
echo Bu işlem biraz zaman alabilir, lütfen bekleyin...

:: PyTorch paketlerini önce temizle (çakışmaları önlemek için)
pip uninstall -y torch torchvision torchaudio

:: Whisper paketini sil (gerekirse yeniden yüklenecek)
pip uninstall -y whisper openai-whisper

:: Diğer paketleri yükle
echo Bağımlılıklar yükleniyor...
pip install -r requirements.txt

:: basla.bat dosyasını oluştur (daha gelişmiş, daha önce sağladığım versiyonu)
echo @echo off > basla.bat
echo title Raporcu - AI Destekli Rapor Yazım Uygulaması >> basla.bat
echo color 0A >> basla.bat
echo. >> basla.bat
echo echo ================================================= >> basla.bat
echo echo    Raporcu - AI Destekli Rapor Yazım Uygulaması >> basla.bat
echo echo                 Başlatılıyor... >> basla.bat
echo echo ================================================= >> basla.bat
echo echo. >> basla.bat
echo. >> basla.bat
echo :: Python yorumlayıcısını optimize et >> basla.bat
echo set PYTHONOPTIMIZE=2 >> basla.bat
echo set PYTHONUTF8=1 >> basla.bat
echo set PYTHONDONTWRITEBYTECODE=1 >> basla.bat
echo. >> basla.bat

if "%use_venv%"=="1" (
    echo :: Sanal ortam etkinleştir >> basla.bat
    echo if exist venv\Scripts\activate.bat ( >> basla.bat
    echo     echo Sanal ortam etkinleştiriliyor... >> basla.bat
    echo     call venv\Scripts\activate.bat >> basla.bat
    echo ) >> basla.bat
    echo. >> basla.bat
)

echo :: FFmpeg yolu kontrolü >> basla.bat
echo where ffmpeg ^>nul 2^>nul >> basla.bat
echo if errorlevel 1 ( >> basla.bat
echo     if exist "%%USERPROFILE%%\FFmpeg\ffmpeg.exe" ( >> basla.bat
echo         set PATH=%%PATH%%;%%USERPROFILE%%\FFmpeg >> basla.bat
echo         echo FFmpeg yolu eklendi. >> basla.bat
echo     ) else ( >> basla.bat
echo         echo [!] UYARI: FFmpeg bulunamadı. Ses işleme özellikleri çalışmayabilir. >> basla.bat
echo     ) >> basla.bat
echo ) >> basla.bat
echo. >> basla.bat
echo :: Gerekli klasörleri kontrol et >> basla.bat
echo if not exist "temp" mkdir temp >> basla.bat
echo if not exist "audio_files" mkdir audio_files >> basla.bat
echo. >> basla.bat
echo :: Uygulamayı başlat >> basla.bat
echo echo Uygulama başlatılıyor... >> basla.bat
echo python main.py >> basla.bat
echo. >> basla.bat
echo :: Hata durumunda bilgilendirme >> basla.bat
echo if errorlevel 1 ( >> basla.bat
echo     color 0C >> basla.bat
echo     echo. >> basla.bat
echo     echo [!] Uygulama başlatılırken bir hata oluştu! >> basla.bat
echo     echo     Lütfen kurulumu kontrol ediniz. >> basla.bat
echo     echo. >> basla.bat
echo     pause >> basla.bat
echo ) else ( >> basla.bat
echo     exit >> basla.bat
echo ) >> basla.bat

echo.
echo =================================================
echo    Kurulum başarıyla tamamlandı!
echo    Uygulamayı başlatmak için basla.bat dosyasını
echo    çalıştırabilirsiniz.
echo =================================================
echo.

pause