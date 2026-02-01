"""
Raporcu Uygulaması için PyInstaller Build Script
Bu script, uygulamayı tek bir .exe dosyası olarak paketler.

Kullanım:
    python build_exe.py

Gereksinimler:
    - PyInstaller: pip install pyinstaller
    - FFmpeg binary dosyaları (proje klasöründe)
"""

import PyInstaller.__main__
import os
import shutil
import sys

# Eski build klasörlerini temizle
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

print("🚀 Raporcu .exe oluşturuluyor...")
print("=" * 60)

# FFmpeg kontrolü
ffmpeg_path = None
ffmpeg_dirs = [
    'ffmpeg-N-119584-g06cee0c681-win64-gpl/bin',
    'ffmpeg/bin',
    'venv/Scripts'
]

print("\n🔍 FFmpeg aranıyor...")
for ffdir in ffmpeg_dirs:
    ffmpeg_exe = os.path.join(ffdir, 'ffmpeg.exe')
    if os.path.exists(ffmpeg_exe):
        ffmpeg_path = ffdir
        print(f"✅ FFmpeg bulundu: {ffmpeg_path}")
        break

if not ffmpeg_path:
    print("⚠️  UYARI: FFmpeg bulunamadı!")
    print("   Ses işleme özellikleri çalışmayacak.")
    print("   FFmpeg'i şu klasörlerden birine ekleyin:")
    for ffdir in ffmpeg_dirs:
        print(f"   - {ffdir}")
    response = input("\n   Yine de devam etmek istiyor musunuz? (e/h): ")
    if response.lower() != 'e':
        print("Build iptal edildi.")
        sys.exit(1)

if not ffmpeg_path:
    print("⚠️  UYARI: FFmpeg bulunamadı!")
    print("   Ses işleme özellikleri çalışmayacak.")
    print("   FFmpeg'i şu klasörlerden birine ekleyin:")
    for ffdir in ffmpeg_dirs:
        print(f"   - {ffdir}")
    response = input("\n   Yine de devam etmek istiyor musunuz? (e/h): ")
    if response.lower() != 'e':
        print("Build iptal edildi.")
        sys.exit(1)

# PyInstaller parametreleri
params = [
    'main.py',                          # Ana dosya
    '--name=Raporcu',                   # Exe adı
    '--onefile',                        # Tek dosya olarak paketle
    '--windowed',                       # Console penceresi açma (GUI app)
    '--add-data=templates;templates',   # Template klasörünü ekle
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=customtkinter',
    '--hidden-import=anthropic',
    '--hidden-import=openai',
    '--hidden-import=google.generativeai',
    '--hidden-import=tiktoken',
    '--hidden-import=pydub',
    '--hidden-import=speech_recognition',
    '--hidden-import=pyaudio',
    '--collect-all=customtkinter',
    '--collect-all=tkinter',
    '--noconfirm',                      # Onay isteme
    '--clean',                          # Temiz build
]

# FFmpeg varsa binary olarak ekle
if ffmpeg_path:
    print(f"\n📦 FFmpeg exe'ye dahil ediliyor...")
    params.append(f'--add-binary={os.path.join(ffmpeg_path, "ffmpeg.exe")};.')
    params.append(f'--add-binary={os.path.join(ffmpeg_path, "ffprobe.exe")};.')
    
# İkon varsa ekle
if os.path.exists('icon.svg'):
    # SVG'yi PyInstaller desteklemediği için atla
    pass
elif os.path.exists('icon.ico'):
    params.append('--icon=icon.ico')

print("\n🔨 PyInstaller çalıştırılıyor...")
print("   (Bu işlem birkaç dakika sürebilir)")
PyInstaller.__main__.run(params)

print("\n🔨 PyInstaller çalıştırılıyor...")
print("   (Bu işlem birkaç dakika sürebilir)")
PyInstaller.__main__.run(params)

print("\n" + "=" * 60)
if os.path.exists('dist/Raporcu.exe'):
    print("✅ Build tamamlandı!")
    print(f"📦 Dosya konumu: {os.path.abspath('dist/Raporcu.exe')}")
    exe_size_mb = os.path.getsize('dist/Raporcu.exe') / (1024*1024)
    print(f"📊 Dosya boyutu: {exe_size_mb:.1f} MB")
    
    if ffmpeg_path:
        print(f"✅ FFmpeg dahil edildi (ses işleme çalışacak)")
    else:
        print(f"⚠️  FFmpeg dahil edilmedi (ses işleme çalışmayacak)")
    
    print("\n💡 Test etmek için: dist\\Raporcu.exe")
    print("\n📋 Kullanım Notları:")
    print("   - İlk çalıştırmada settings.json dosyası oluşturulacak")
    print("   - API anahtarlarınızı settings.json'a ekleyin")
    print("   - Windows Defender uyarısı alabilirsiniz (normal)")
else:
    print("❌ Build başarısız!")
    print("   Hata mesajlarını kontrol edin.")
    sys.exit(1)
