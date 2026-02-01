@echo off
title Raporcu - AI Destekli Rapor Yazım Uygulaması
color 0A

echo =================================================
echo    Raporcu - AI Destekli Rapor Yazım Uygulaması
echo                 Başlatılıyor...
echo =================================================
echo.

:: Python yorumlayıcısını optimize et
set PYTHONOPTIMIZE=2
set PYTHONUTF8=1
set PYTHONDONTWRITEBYTECODE=1

:: Sanal ortam kontrolü
if exist venv\Scripts\activate.bat (
    echo Sanal ortam etkinleştiriliyor...
    call venv\Scripts\activate.bat
)

:: FFmpeg yolu kontrolü
where ffmpeg >nul 2>nul
if errorlevel 1 (
    if exist "%USERPROFILE%\FFmpeg\ffmpeg.exe" (
        set PATH=%PATH%;%USERPROFILE%\FFmpeg
        echo FFmpeg yolu eklendi.
    ) else (
        echo [!] UYARI: FFmpeg bulunamadı. Ses işleme özellikleri çalışmayabilir.
    )
)

:: Temp klasörü kontrolü
if not exist "temp" mkdir temp
if not exist "audio_files" mkdir audio_files

:: Uygulamayı başlat
echo Uygulama başlatılıyor...
python main.py

:: Hata durumunda bilgilendirme
if errorlevel 1 (
    color 0C
    echo.
    echo [!] Uygulama başlatılırken bir hata oluştu!
    echo     Lütfen kurulumu kontrol ediniz.
    echo.
    pause
) else (
    exit
)
