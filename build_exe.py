"""
Raporcu Uygulaması için PyInstaller Build Script
Bu script, uygulamayı tek bir .exe dosyası olarak paketler.

Kullanım:
    python build_exe.py
"""

import PyInstaller.__main__
import os
import shutil

# Eski build klasörlerini temizle
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

print("🚀 Raporcu .exe oluşturuluyor...")
print("=" * 60)

# PyInstaller parametreleri
PyInstaller.__main__.run([
    'main.py',                          # Ana dosya
    '--name=Raporcu',                   # Exe adı
    '--onefile',                        # Tek dosya olarak paketle
    '--windowed',                       # Console penceresi açma (GUI app)
    '--icon=icon.svg',                  # Uygulama ikonu (varsa)
    '--add-data=templates;templates',   # Template klasörünü ekle
    '--add-data=static;static',         # Static klasörünü ekle (varsa)
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=customtkinter',
    '--hidden-import=anthropic',
    '--hidden-import=openai',
    '--hidden-import=google.generativeai',
    '--hidden-import=tiktoken',
    '--collect-all=customtkinter',
    '--collect-all=tkinter',
    '--noconfirm',                      # Onay isteme
    '--clean',                          # Temiz build
])

print("\n" + "=" * 60)
print("✅ Build tamamlandı!")
print(f"📦 Dosya konumu: {os.path.abspath('dist/Raporcu.exe')}")
print(f"📊 Dosya boyutu: {os.path.getsize('dist/Raporcu.exe') / (1024*1024):.1f} MB")
print("\n💡 Test etmek için: dist\\Raporcu.exe")
