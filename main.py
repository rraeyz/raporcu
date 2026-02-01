import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import shutil
import time
import re  # regex modülü
from settings import SettingsWindow
from progress_indicator import ProgressIndicator

from config import Config
from audio_processor import AudioProcessor
from file_processor import FileProcessor
from ai_service import AIService
from utils import center_window

class RaporApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Config'i hemen yükle çünkü pencere ayarlarına ihtiyacımız var
        self.config = Config()
        
        # Temel pencere ayarları
        self.title("Deney Raporu Yazım Uygulaması")
        
        # Pencere konumunu ve boyutunu ayarla (kayıtlı durumdan)
        self.saved_geometry, self.saved_state = self.config.get_window_state()
        
        # Geometriyi ayarla
        self.geometry(self.saved_geometry)
        
        # Minimum boyut
        self.minsize(1000, 700)
        
        # Pencere durumunu ayarla
        if self.saved_state == "zoomed" and sys.platform == 'win32':
            self.state('zoomed')  # Windows için tam ekran
        elif self.saved_state == "maximized" and sys.platform != 'win32':
            self.attributes('-zoomed', '1')  # Linux için tam ekran
    
        # Asenkron yükleme için değişkenler
        self.services_ready = False
        self.ui_ready = False
        
        # Önce UI elementlerini yükle
        self.after(10, self.initialize_ui)
        
        # Servisleri arka planda başlat
        threading.Thread(target=self.initialize_services, daemon=True).start()

        # Pencere kapatma olayını bağla
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def initialize_ui(self):
        """UI elementlerini yükle"""
        # Tema ve yazı tipi ayarlarını uygula
        self.apply_theme_settings()
        
        self.create_ui_elements()
    
        # Kaydedilmiş bir pencere konumu yoksa merkeze konumlandır
        if not hasattr(self, 'saved_geometry') or self.saved_geometry == "1200x800":
            center_window(self)
        
        self.ui_ready = True
        self.check_initialization()
    
    def apply_theme_settings(self):
        """Tema ayarlarını uygula"""
        theme = self.config.theme
        
        if theme == "Sistem":
            ctk.set_appearance_mode("system")
        elif theme == "Koyu":
            ctk.set_appearance_mode("dark")
        elif theme == "Açık":
            ctk.set_appearance_mode("light")
            
        ctk.set_default_color_theme("blue")
        
    def apply_font_settings(self):
        """Yazı tipi boyutu ayarlarını uygula"""
        font_size = self.config.font_size
        
        # Tüm metin alanlarını güncelle
        if hasattr(self, 'procedure_text'):
            self.procedure_text.configure(font=("Arial", font_size))
            
        if hasattr(self, 'reference_text'):
            self.reference_text.configure(font=("Arial", font_size))
            
        if hasattr(self, 'result_text'):
            self.result_text.configure(font=("Arial", font_size))
    
    # initialize_services fonksiyonu - mevcut yapıyı koruyarak optimize edelim
    def initialize_services(self):
        """Servisleri arka planda yükle - optimized lazy loading"""
        print("Servisler başlatılıyor...")
        
        # Config zaten __init__ içinde yüklendiği için tekrar oluşturmuyoruz
        # Diğer servisleri başlat ama içlerindeki ağır yüklemeleri yapma
        # Bu servisler içerisindeki modeller ve kütüphaneler lazy loading ile yüklenecek
        self.audio_processor = AudioProcessor(self)
        self.file_processor = FileProcessor()
        self.ai_service = AIService(self.config)
        
        # Başlangıçta geçici dosyaları temizle (72 saatten eski dosyalar)
        threading.Thread(target=self.audio_processor.cleanup_temp_files, args=(72,), daemon=True).start()
        
        self.services_ready = True
        self.after(0, self.check_initialization)
    
    def check_initialization(self):
        """Tüm bileşenlerin yüklenip yüklenmediğini kontrol et"""
        if self.services_ready and self.ui_ready:
            self.event_generate("<<ApplicationReady>>")
    
    def create_ui_elements(self):
        # Ana grid yapısı
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Ana container (grid sistemi)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Main frame grid yapısı
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0)  # Üst panel
        self.main_frame.grid_rowconfigure(1, weight=3)  # İçerik paneli
        self.main_frame.grid_rowconfigure(2, weight=2)  # Sonuç panel
        
        # Sekmeleri oluştur
        self.tabs = ctk.CTkTabview(self.main_frame)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.tabs.add("Rapor")
        self.tabs.add("Görsel İçerik")
        self.tabs.set("Rapor")  # Varsayılan sekme
        
        # Üst panel
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Üst panel grid yapısı
        self.top_frame.grid_columnconfigure(0, weight=0)  # Ayarlar butonu
        self.top_frame.grid_columnconfigure(1, weight=0)  # Başlık etiketi
        self.top_frame.grid_columnconfigure(2, weight=1)  # Başlık giriş alanı
        self.top_frame.grid_columnconfigure(3, weight=0)  # Rapor oluştur butonu
        
        # Ayarlar butonu
        self.settings_btn = ctk.CTkButton(
            self.top_frame, 
            text="⚙️ Ayarlar", 
            command=self.open_settings,
            width=100
        )
        self.settings_btn.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Deney başlığı
        self.title_label = ctk.CTkLabel(self.top_frame, text="Deney Başlığı:")
        self.title_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        self.title_entry = ctk.CTkEntry(self.top_frame, width=400)
        self.title_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # Rapor oluştur butonu
        self.generate_btn = ctk.CTkButton(
            self.top_frame, 
            text="Rapor Oluştur", 
            command=self.generate_report,
            fg_color="#2AAA8A"
        )
        self.generate_btn.grid(row=0, column=3, padx=5, pady=5, sticky="e")
        
        # İçerik paneli (alt panel)
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # İçerik panel grid yapısı
        self.content_frame.grid_columnconfigure(0, weight=1)  # Sol panel
        self.content_frame.grid_columnconfigure(1, weight=1)  # Sağ panel
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Sol panel (Deneyin Yapılışı)
        self.left_frame = ctk.CTkFrame(self.content_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Sol panel grid yapısı
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=0)  # Etiket
        self.left_frame.grid_rowconfigure(1, weight=1)  # Metin alanı
        
        self.procedure_label = ctk.CTkLabel(self.left_frame, text="Deneyin Yapılışı:")
        self.procedure_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.procedure_text = ctk.CTkTextbox(self.left_frame, wrap="word")
        self.procedure_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Yazı tipi boyutunu uygula
        self.procedure_text.configure(font=("Arial", self.config.font_size))
        
        # Sağ panel
        self.right_frame = ctk.CTkFrame(self.content_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Sağ panel grid yapısı
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0)  # Ses işleme paneli
        self.right_frame.grid_rowconfigure(1, weight=1)  # Referans metinler paneli
        
        # Ses işleme paneli
        self.audio_frame = ctk.CTkFrame(self.right_frame)
        self.audio_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Ses işleme panel grid yapısı
        self.audio_frame.grid_columnconfigure(0, weight=1)
        self.audio_frame.grid_rowconfigure(0, weight=0)  # Etiket
        self.audio_frame.grid_rowconfigure(1, weight=0)  # Butonlar
        self.audio_frame.grid_rowconfigure(2, weight=0)  # Durum
        
        self.audio_label = ctk.CTkLabel(self.audio_frame, text="Ses Kaydı:")
        self.audio_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Ses işleme butonları
        self.audio_buttons_frame = ctk.CTkFrame(self.audio_frame)
        self.audio_buttons_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Butonlar çerçevesi grid yapısı
        self.audio_buttons_frame.grid_columnconfigure(0, weight=1)
        self.audio_buttons_frame.grid_columnconfigure(1, weight=1)
        self.audio_buttons_frame.grid_columnconfigure(2, weight=1)
        self.audio_buttons_frame.grid_columnconfigure(3, weight=1)
        
        self.record_btn = ctk.CTkButton(
            self.audio_buttons_frame,
            text="🎙️ Kayıt Başlat",
            command=self.toggle_recording,
            fg_color="#FF5555"
        )
        self.record_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.pause_btn = ctk.CTkButton(
            self.audio_buttons_frame,
            text="⏸️ Duraklat",
            command=self.pause_recording,
            state="disabled"
        )
        self.pause_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.upload_audio_btn = ctk.CTkButton(
            self.audio_buttons_frame,
            text="📁 Ses Dosyası Yükle",
            command=self.upload_audio_file
        )
        self.upload_audio_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.process_audio_btn = ctk.CTkButton(
            self.audio_buttons_frame,
            text="🔄 Ses İşle",
            command=self.process_recorded_audio,
            state="disabled"  # Başlangıçta devre dışı
        )
        self.process_audio_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Gelişmiş ilerleme göstergesi
        self.audio_progress = ProgressIndicator(self.audio_frame)
        self.audio_progress.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.audio_progress.set_status("Kayıt Hazır")
        
        # Referans metinler paneli
        self.reference_frame = ctk.CTkFrame(self.right_frame)
        self.reference_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Referans panel grid yapısı
        self.reference_frame.grid_columnconfigure(0, weight=1)
        self.reference_frame.grid_rowconfigure(0, weight=0)  # Etiket
        self.reference_frame.grid_rowconfigure(1, weight=1)  # Metin alanı
        self.reference_frame.grid_rowconfigure(2, weight=0)  # Buton
        
        self.reference_label = ctk.CTkLabel(self.reference_frame, text="Referans Metinler:")
        self.reference_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.reference_text = ctk.CTkTextbox(self.reference_frame, wrap="word")
        self.reference_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Yazı tipi boyutunu uygula
        self.reference_text.configure(font=("Arial", self.config.font_size))
        
        self.upload_ref_btn = ctk.CTkButton(
            self.reference_frame,
            text="📁 Referans Dosya Yükle",
            command=self.upload_reference_file
        )
        self.upload_ref_btn.grid(row=2, column=0, padx=5, pady=5)
        
        # Sonuç panel
        self.result_frame = ctk.CTkFrame(self.main_frame)
        self.result_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # Sonuç panel grid yapısı
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_rowconfigure(0, weight=0)  # Etiket
        self.result_frame.grid_rowconfigure(1, weight=1)  # Metin alanı
        self.result_frame.grid_rowconfigure(2, weight=0)  # İlerleme göstergesi
        self.result_frame.grid_rowconfigure(3, weight=0)  # Buton
        
        self.result_label = ctk.CTkLabel(self.result_frame, text="Oluşturulan Rapor:")
        self.result_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.result_text = ctk.CTkTextbox(self.result_frame, wrap="word")
        self.result_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Yazı tipi boyutunu uygula
        self.result_text.configure(font=("Arial", self.config.font_size))
        
        # AI ilerleme göstergesi
        self.ai_progress = ProgressIndicator(self.result_frame)
        self.ai_progress.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.ai_progress.set_status("Rapor oluşturmak için hazır")
        
        # Rapor kaydetme butonları çerçevesi
        self.save_buttons_frame = ctk.CTkFrame(self.result_frame)
        self.save_buttons_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        # Butonları eşit ağırlıkta yerleştir
        self.save_buttons_frame.grid_columnconfigure(0, weight=1)
        self.save_buttons_frame.grid_columnconfigure(1, weight=1)
        
        # Word olarak kaydet butonu
        self.save_docx_btn = ctk.CTkButton(
            self.save_buttons_frame,
            text="� Word Olarak Kaydet",
            command=lambda: self.save_report_as("docx"),
            state="disabled"
        )
        self.save_docx_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # PDF olarak kaydet butonu
        self.save_pdf_btn = ctk.CTkButton(
            self.save_buttons_frame,
            text="📑 PDF Olarak Kaydet",
            command=lambda: self.save_report_as("pdf"),
            state="disabled"
        )
        self.save_pdf_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Kayıt durumu değişkenleri
        self.recording = False
        self.paused = False
        
        # Sonuç çerçevesi
        self.create_result_frame()
    
    def create_result_frame(self):
        """Sonuç çerçevesini oluşturur"""
        result_frame = ctk.CTkFrame(self.tabs.tab("Rapor"), fg_color="transparent")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Başlık ve diğer elemanlar
        # ...mevcut kodunuz...
        
        # Araç çubuğu frame'i
        toolbar_frame = ctk.CTkFrame(result_frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Zengin metin düzenleme araçları
        self.add_image_btn = ctk.CTkButton(
            toolbar_frame, 
            text="Görsel Ekle", 
            width=100, 
            command=self.add_image_to_report
        )
        self.add_image_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.add_table_btn = ctk.CTkButton(
            toolbar_frame, 
            text="Tablo Ekle", 
            width=100, 
            command=self.add_table_to_report
        )
        self.add_table_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.add_formula_btn = ctk.CTkButton(
            toolbar_frame, 
            text="Formül Ekle", 
            width=100, 
            command=self.add_formula_to_report
        )
        self.add_formula_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.manage_references_btn = ctk.CTkButton(
            toolbar_frame, 
            text="Kaynakları Yönet", 
            width=120, 
            command=self.manage_references
        )
        self.manage_references_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Aşağıdaki metodlar aynı kalacak, yalnızca arayüz değişiklikleri yaptık
    def open_settings(self):
        """Ayarlar penceresini açar"""
        settings_window = SettingsWindow(self)
        settings_window.grab_set()  # Modal pencere yapma
    
    def toggle_recording(self):
        """Ses kaydını başlatır veya durdurur"""
        if not self.recording:
            # Kayıt başlatma
            self.recording = True
            self.paused = False
            
            # Buton durumları güncelleme
            self.record_btn.configure(text="⏹️ Kaydı Durdur")
            self.pause_btn.configure(state="normal")
            self.upload_audio_btn.configure(state="disabled")
            
            # İlerleme göstergesini güncelle
            self.audio_progress.set_status("Kayıt Yapılıyor...")
            self.audio_progress.start_indeterminate()
            
            # Ses kaydını başlat
            threading.Thread(target=self.audio_processor.start_recording, daemon=True).start()
        else:
            # Kayıt durdurma
            self.recording = False
            self.paused = False
            
            # İlerleme göstergesini güncelle
            self.audio_progress.stop()
            self.audio_progress.set_status("Kayıt Tamamlandı")
            
            # Buton durumlarını güncelle
            self.record_btn.configure(text="🎙️ Kayıt Başlat")
            self.pause_btn.configure(state="disabled")
            self.upload_audio_btn.configure(state="normal")
            self.process_audio_btn.configure(state="normal")  # Ses işle butonunu aktif et
            
            # Kaydı durdur ve kaydet
            self.audio_processor.stop_recording()
    
    def pause_recording(self):
        """Ses kaydını duraklatır veya devam ettirir"""
        if self.recording:
            if not self.paused:
                # Kaydı duraklat
                self.paused = True
                self.pause_btn.configure(text="▶️ Devam Et")
                
                # İlerleme göstergesini güncelle
                self.audio_progress.set_status("Kayıt Duraklatıldı")
                self.audio_progress.stop()
                
                # Ses kaydını duraklat
                self.audio_processor.pause_recording()
            else:
                # Kayda devam et
                self.paused = False
                self.pause_btn.configure(text="⏸️ Duraklat")
                
                # İlerleme göstergesini güncelle
                self.audio_progress.set_status("Kayıt Yapılıyor...")
                self.audio_progress.start_indeterminate()
                
                # Ses kaydına devam et
                self.audio_processor.resume_recording()
    
    def upload_audio_file(self):
        """Ses dosyası yükler"""
        file_path = filedialog.askopenfilename(
            title="Ses Dosyası Seç",
            filetypes=[
                ("Ses Dosyaları", "*.wav;*.mp3;*.ogg;*.m4a"),
                ("Tüm Dosyalar", "*.*")
            ]
        )
        
        if file_path:
            # Dosyayı temp klasörüne kopyala
            file_name = os.path.basename(file_path)
            temp_path = os.path.join(self.config.temp_dir, file_name)
            
            # İlerleme göstergesini güncelle
            self.audio_progress.set_status("Ses Dosyası Yükleniyor...")
            self.audio_progress.start_indeterminate()
            
            def copy_file():
                try:
                    shutil.copy2(file_path, temp_path)
                    
                    def update_ui():
                        # Dosya yolunu sakla ve butonları güncelle
                        self.audio_processor.temp_file_path = temp_path
                        self.audio_progress.set_status("Ses Dosyası Hazır")
                        self.audio_progress.stop()
                        self.process_audio_btn.configure(state="normal")
                    
                    self.after(0, update_ui)
                except Exception as e:
                    def show_error():
                        messagebox.showerror("Hata", f"Dosya kopyalanırken bir hata oluştu: {str(e)}")
                        self.audio_progress.set_error("Dosya Yüklenemedi!")
                    
                    self.after(0, show_error)
            
            # Arka planda kopyalama işlemini yap
            threading.Thread(target=copy_file, daemon=True).start()

    def process_recorded_audio(self):
        """Kaydedilmiş sesi işler"""
        try:
            # İlerleme göstergesini güncelle
            self.audio_progress.set_status("Ses Dosyası İşleniyor...")
            self.audio_progress.start_indeterminate()
            self.process_audio_btn.configure(state="disabled")
            
            def process_audio():
                try:
                    # İlerleme göstergesini güncelle
                    self.audio_progress.set_status("Ses dosyası işleniyor...")
                    self.audio_progress.start_indeterminate()
                    
                    # Son kaydedilen ses dosyasını işle
                    text = self.audio_processor.process_last_recording()
                    
                    def update_ui():
                        if text:
                            # Metni prosedür alanına ekle
                            current_text = self.procedure_text.get("1.0", tk.END).strip()
                            if current_text:
                                text_to_add = f"\n{text}"
                            else:
                                text_to_add = text
                            self.procedure_text.insert(tk.END, text_to_add)
                            
                            # İlerleme göstergesini güncelle
                            self.audio_progress.set_success("Ses Başarıyla İşlendi")
                            messagebox.showinfo("Başarılı", "Ses metne dönüştürüldü ve editöre eklendi.")
                        else:
                            # Hata durumunda ilerleme göstergesini güncelle
                            self.audio_progress.set_error("Ses İşlenemedi!")
                            
                            # Kullanıcıya ne yapabileceği konusunda bilgi ver
                            result = messagebox.askokcancel(
                                "Ses Tanıma Başarısız", 
                                "Ses tanıma işlemi başarısız oldu.\n\n"
                                "Olası çözümler:\n"
                                "- Daha yüksek sesle ve net konuşun\n"
                                "- Ayarlardan farklı bir tanıma motoru seçin\n"
                                "- Ses dosyasını manuel olarak editöre yazın\n\n"
                                "Ayarlar penceresini açmak ister misiniz?",
                                icon="warning"
                            )
                            if result:
                                self.open_settings()
                        
                        self.process_audio_btn.configure(state="normal")
                    
                    self.after(0, update_ui)
                    
                except Exception as e:
                    def show_error():
                        error_msg = str(e)
                        messagebox.showerror("Hata", f"Ses işlenirken bir hata oluştu: {error_msg}")
                        self.audio_progress.set_error("Hata: " + error_msg)
                        self.process_audio_btn.configure(state="normal")
                    
                    self.after(0, show_error)
            
            # Arka planda işle
            threading.Thread(target=process_audio, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Hata", f"Ses işleme başlatılamadı: {str(e)}")
            self.audio_progress.set_error("Hata!")
            self.process_audio_btn.configure(state="normal")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen bir hata oluştu: {str(e)}")
            self.process_audio_btn.configure(state="normal")

    def upload_reference_file(self):
        """Referans dosyası yükleme"""
        file_path = filedialog.askopenfilename(
            title="Referans Dosya Seç",
            filetypes=[
                ("PDF Dosyaları", "*.pdf"),
                ("Word Dosyaları", "*.docx"),
                ("Metin Dosyaları", "*.txt"),
                ("Tüm Dosyalar", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Dosyayı işle
                text_content = self.file_processor.extract_text_from_file(file_path)
                
                if text_content:
                    current_text = self.reference_text.get("1.0", tk.END).strip()
                    if current_text:
                        # Mevcut metne ekle
                        self.reference_text.insert(tk.END, "\n\n" + text_content)
                    else:
                        # Metin boşsa direkt ekle
                        self.reference_text.insert("1.0", text_content)
                    
                    messagebox.showinfo("Bilgi", "Referans dosyası başarıyla yüklendi.")
                else:
                    messagebox.showwarning("Uyarı", "Dosyadan metin çıkarılamadı. Farklı bir dosya deneyin.")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya işlenirken bir hata oluştu: {str(e)}")
    
    def generate_report(self):
        """Rapor oluşturma işlemi"""
        # Gerekli verileri al
        deney_basligi = self.title_entry.get().strip()
        deneyin_yapilisi = self.procedure_text.get("1.0", tk.END).strip()
        referans_metin = self.reference_text.get("1.0", tk.END).strip()
        
        # Validasyon
        if not deney_basligi:
            messagebox.showwarning("Uyarı", "Lütfen deney başlığını girin.")
            self.title_entry.focus_set()
            return
        
        if not deneyin_yapilisi:
            messagebox.showwarning("Uyarı", "Lütfen deneyin yapılışını girin.")
            self.procedure_text.focus_set()
            return
        
        # API Anahtarı kontrolü
        current_provider = self.config.get_current_provider()
        api_key = self.config.get_api_key_for_current_model()
        
        if not api_key:
            result = messagebox.askokcancel(
                "API Anahtarı Gerekli", 
                f"Bu işlem için {current_provider} API anahtarı gereklidir. "
                f"Ayarlar penceresini açıp API anahtarı eklemek ister misiniz?",
                icon="warning"
            )
            if result:
                self.open_settings()
            return
        
        # Durum güncelleme
        self.generate_btn.configure(state="disabled", text="Rapor Oluşturuluyor...")
        
        # AI İlerleme göstergesini güncelle
        self.ai_progress.reset()
        self.ai_progress.set_status(f"{self.config.ai_model} ile rapor oluşturuluyor...")
        self.ai_progress.start_indeterminate()
        self.update_idletasks()
        
        # Arka planda rapor oluştur
        def generate_in_background():
            try:
                # Zaman damgası başlat
                start_time = time.time()
                
                # Yapay zeka ile rapor oluştur
                report = self.ai_service.generate_report(deney_basligi, deneyin_yapilisi, referans_metin)
                
                # Geçen süreyi hesapla
                elapsed_time = time.time() - start_time
                print(f"Rapor oluşturma süresi: {elapsed_time:.2f} saniye")
                
                # UI thread'inde sonuçları güncelle
                def update_ui():
                    if report and not report.startswith("API hatası") and not report.startswith("Beklenmeyen bir hata"):
                        # Eğer raporun başında bir açıklama veya teşekkür varsa kaldır
                        # Direkt olarak başlıkla başlamasını sağla
                        cleaned_report = report
                        
                        # Önce başlık ve başlık numarasını düzenle
                        if not cleaned_report.strip().startswith(deney_basligi):
                            # İlk başlık ifadesini bul
                            first_heading_pos = cleaned_report.find(deney_basligi)
                            if first_heading_pos > 0:
                                cleaned_report = cleaned_report[first_heading_pos:]
                            
                            # Eğer başlık bulunamadıysa numaralandırılmış başlığı ara
                            elif cleaned_report.find("1. ") >= 0:
                                first_heading_pos = cleaned_report.find("1. ")
                                cleaned_report = cleaned_report[first_heading_pos:]
                        
                        # Başlıkları biçimlendir
                        lines = cleaned_report.split('\n')
                        formatted_lines = []
                        
                        # İlk satır ana başlık olmalı
                        if lines and len(lines) > 0:
                            # Ana başlıktan sayıyı kaldır
                            main_title = lines[0]
                            if main_title.startswith("1. "):
                                main_title = main_title[3:].strip()
                            formatted_lines.append(main_title)
                            
                            # Diğer satırları işle
                            section_num = 1
                            for i in range(1, len(lines)):
                                line = lines[i].strip()
                                if not line:
                                    formatted_lines.append(line)
                                    continue
                                
                                # Amaçlar, Teorik Bilgiler vb. başlıkları
                                if line.lower().startswith("amaç") or \
                                   line.lower().startswith("teor") or \
                                   line.lower().startswith("malzeme") or \
                                   line.lower().startswith("deney") or \
                                   line.lower().startswith("yapıl") or \
                                   line.lower().startswith("hesap") or \
                                   line.lower().startswith("sonu") or \
                                   line.lower().startswith("yorum") or \
                                   line.lower().startswith("kaynak") or \
                                   (len(line) < 30 and ("giriş" in line.lower() or 
                                                       "amac" in line.lower() or 
                                                       "sonuç" in line.lower() or 
                                                       "özet" in line.lower() or 
                                                       "yöntem" in line.lower() or 
                                                       "tartışma" in line.lower() or 
                                                       "materyal" in line.lower() or 
                                                       "analiz" in line.lower() or 
                                                       "bulgular" in line.lower() or 
                                                       "değerlendirme" in line.lower())):
                                    
                                    # Başlığı numaralandır
                                    # Eğer başında zaten numara varsa kaldır
                                    if re.match(r'^\d+\.', line):
                                        # Numarayı kaldır
                                        title_text = re.sub(r'^\d+\.\s*', '', line)
                                        line = f"{section_num}. {title_text}"
                                    elif not re.match(r'^\d+\.', line):
                                        line = f"{section_num}. {line}"
                                    
                                    # Markdown formatında başlığı kalın yap
                                    # Eğer '**' ile başlamıyorsa başına ve sonuna ekle
                                    if not line.startswith('**') and not line.endswith('**'):
                                        line = f"**{line}**"
                                    
                                    section_num += 1
                                
                                formatted_lines.append(line)
                        
                        # Düzenlenmiş içeriği yeniden birleştir
                        cleaned_report = '\n'.join(formatted_lines)
                        
                        self.result_text.delete("1.0", tk.END)
                        self.result_text.insert("1.0", cleaned_report)
                        # Kaydetme butonlarını etkinleştir
                        self.save_docx_btn.configure(state="normal")
                        self.save_pdf_btn.configure(state="normal")
                        self.ai_progress.set_success(f"Rapor {elapsed_time:.1f} saniyede oluşturuldu")
                    else:
                        error_msg = report if report else "Bilinmeyen bir hata oluştu."
                        self.result_text.delete("1.0", tk.END)
                        self.result_text.insert("1.0", f"Hata: {error_msg}\n\nLütfen farklı bir model veya API anahtarı deneyin.")
                        self.ai_progress.set_error("Rapor oluşturulamadı!")
                        messagebox.showerror("Hata", f"Rapor oluşturulurken bir sorun oluştu:\n\n{error_msg}")
                    
                    self.generate_btn.configure(state="normal", text="Rapor Oluştur")
                
                self.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    error_msg = str(e)
                    self.ai_progress.set_error(f"Hata: {error_msg}")
                    self.result_text.delete("1.0", tk.END)
                    self.result_text.insert("1.0", f"Hata: {error_msg}\n\nLütfen ayarlarınızı kontrol edin ve tekrar deneyin.")
                    messagebox.showerror("Hata", f"Rapor oluşturulurken bir hata oluştu: {error_msg}")
                    self.generate_btn.configure(state="normal", text="Rapor Oluştur")
                
                self.after(0, show_error)
        
        # Arka planda çalıştır
        threading.Thread(target=generate_in_background, daemon=True).start()
    
    def save_report_as(self, format_type):
        """Oluşturulan raporu belirli bir formatta dosyaya kaydetme"""
        deney_basligi = self.title_entry.get().strip()
        dosya_adi = deney_basligi.replace(" ", "_") if deney_basligi else "deney_raporu"
        
        # Format tipine göre dosya uzantısı ve filtre ayarla
        if format_type == "docx":
            file_ext = ".docx"
            file_types = [("Word Dosyası", "*.docx"), ("Tüm Dosyalar", "*.*")]
            save_title = "Word Olarak Kaydet"
        elif format_type == "pdf":
            file_ext = ".pdf"
            file_types = [("PDF Dosyası", "*.pdf"), ("Tüm Dosyalar", "*.*")]
            save_title = "PDF Olarak Kaydet"
        else:
            file_ext = ".txt"
            file_types = [("Metin Dosyası", "*.txt"), ("Tüm Dosyalar", "*.*")]
            save_title = "Metin Olarak Kaydet"
        
        file_path = filedialog.asksaveasfilename(
            title=save_title,
            initialfile=f"{dosya_adi}{file_ext}",
            filetypes=file_types
        )
        
        if file_path:
            # Dosya uzantısını kontrol et ve gerekirse ekle
            if not file_path.lower().endswith(file_ext):
                file_path += file_ext
                
            # Dosya kaydetme öncesi ilerleme göstergesini güncelle
            self.ai_progress.reset()
            self.ai_progress.set_status(f"{format_type.upper()} dosyası olarak kaydediliyor...")
            self.ai_progress.start_indeterminate()
            
            # Butonları devre dışı bırak
            self.save_docx_btn.configure(state="disabled")
            self.save_pdf_btn.configure(state="disabled")
            self.update_idletasks()
            
            # Arka planda kaydet
            def save_in_background():
                success = False
                error_msg = ""
                
                try:
                    # Rapor içeriğini al
                    report_content = self.result_text.get("1.0", tk.END)
                    
                    if format_type == "docx":
                        # DOCX olarak kaydet - config örneğini ilet
                        success = self.file_processor.save_as_docx(report_content, file_path, config_instance=self.config)
                    elif format_type == "pdf":
                        # PDF olarak kaydet - config örneğini ilet
                        success = self.file_processor.save_as_pdf(report_content, file_path, config_instance=self.config)
                    else:
                        # Varsayılan olarak metin dosyası
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(report_content)
                        success = True
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"Rapor kaydedilirken hata: {error_msg}")
                
                # UI thread'inde sonuçları göster
                def update_ui():
                    # Butonları etkinleştir
                    self.save_docx_btn.configure(state="normal")
                    self.save_pdf_btn.configure(state="normal")
                    
                    if success:
                        self.ai_progress.set_success(f"Rapor {format_type.upper()} olarak kaydedildi")
                        messagebox.showinfo("Bilgi", f"Rapor başarıyla kaydedildi:\n{file_path}")
                    else:
                        self.ai_progress.set_error("Kayıt hatası!")
                        messagebox.showerror("Hata", f"Rapor kaydedilirken bir hata oluştu:\n{error_msg}")
                
                self.after(0, update_ui)
            
            # Arka planda çalıştır
            threading.Thread(target=save_in_background, daemon=True).start()
    
    def save_report(self):
        """Eski kaydetme fonksiyonu - geriye uyumluluk için korundu"""
        # Varsayılan olarak Word formatında kaydet
        self.save_report_as("docx")
    
    def add_image_to_report(self):
        """Rapora görsel ekler"""
        file_path = filedialog.askopenfilename(
            title="Görsel Seç",
            filetypes=[
                ("Görsel Dosyaları", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Tüm Dosyalar", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Görsel dosyasını temp klasörüne kopyala
                import shutil
                import os
                from datetime import datetime
                
                # Benzersiz bir isim oluştur
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                img_filename = f"img_{timestamp}_{os.path.basename(file_path)}"
                img_dest = os.path.join(self.config.temp_dir, img_filename)
                
                # Dosyayı kopyala
                shutil.copy2(file_path, img_dest)
                
                # Raporun sonuna görsel bilgisi ekle
                cursor_pos = self.result_text.index(tk.INSERT)
                self.result_text.insert(cursor_pos, f"\n[GÖRSEL: {img_dest}]\n")
                
                messagebox.showinfo("Bilgi", "Görsel rapora eklendi. PDF/DOCX dışa aktarımında görsel otomatik olarak yerleştirilecektir.")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Görsel eklenirken bir hata oluştu: {str(e)}")

    def add_table_to_report(self):
        """Rapora tablo ekler"""
        # Tablo boyutu alma penceresi
        table_dialog = ctk.CTkToplevel(self)
        table_dialog.title("Tablo Ekle")
        table_dialog.geometry("300x200")
        table_dialog.transient(self)
        table_dialog.grab_set()
        
        # Tablo boyutları
        ctk.CTkLabel(table_dialog, text="Satır Sayısı:").pack(pady=(20, 5))
        rows_var = tk.StringVar(value="3")
        rows_entry = ctk.CTkEntry(table_dialog, textvariable=rows_var, width=100)
        rows_entry.pack(pady=5)
        
        ctk.CTkLabel(table_dialog, text="Sütun Sayısı:").pack(pady=(10, 5))
        cols_var = tk.StringVar(value="3")
        cols_entry = ctk.CTkEntry(table_dialog, textvariable=cols_var, width=100)
        cols_entry.pack(pady=5)
        
        def create_table():
            try:
                rows = int(rows_var.get())
                cols = int(cols_var.get())
                
                if rows < 1 or cols < 1:
                    messagebox.showerror("Hata", "Satır ve sütun sayısı en az 1 olmalıdır.")
                    return
                    
                if rows > 20 or cols > 10:
                    messagebox.showerror("Hata", "Satır sayısı en fazla 20, sütun sayısı en fazla 10 olabilir.")
                    return
                
                # Tablo şablonu oluştur
                table = "| "
                for c in range(cols):
                    table += f"Sütun {c+1} | "
                table += "\n|"
                
                # Başlık ayıracı
                for c in range(cols):
                    table += " --- |"
                table += "\n"
                
                # Satırlar
                for r in range(rows-1):  # Başlık satırını çıkardık
                    table += "| "
                    for c in range(cols):
                        table += f"Hücre {r+1},{c+1} | "
                    table += "\n"
                
                # Tabloyu rapora ekle
                cursor_pos = self.result_text.index(tk.INSERT)
                self.result_text.insert(cursor_pos, f"\n{table}\n")
                
                table_dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli sayılar girin.")
        
        create_btn = ctk.CTkButton(table_dialog, text="Tablo Oluştur", command=create_table)
        create_btn.pack(pady=20)

    def add_formula_to_report(self):
        """Rapora matematiksel formül ekler"""
        formula_dialog = ctk.CTkToplevel(self)
        formula_dialog.title("Formül Ekle")
        formula_dialog.geometry("500x300")
        formula_dialog.transient(self)
        formula_dialog.grab_set()
        
        ctk.CTkLabel(formula_dialog, text="LaTeX formatında formülünüzü girin:").pack(pady=(20, 5))
        
        formula_text = ctk.CTkTextbox(formula_dialog, height=100)
        formula_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Örnek formüller
        example_frame = ctk.CTkFrame(formula_dialog)
        example_frame.pack(padx=10, pady=5, fill=tk.X)
        
        ctk.CTkLabel(example_frame, text="Örnekler:").pack(side=tk.LEFT, padx=5)
        
        examples = [
            ("E=mc^2", "E=mc^2"),
            ("\\frac{d}{dx}f(x)", "Türev"),
            ("\\sum_{i=1}^{n} i^2", "Toplam"),
            ("\\int_{a}^{b} f(x) dx", "İntegral")
        ]
        
        for latex, name in examples:
            def add_example(ex=latex):
                formula_text.delete("1.0", tk.END)
                formula_text.insert("1.0", ex)
            
            btn = ctk.CTkButton(example_frame, text=name, width=70, command=add_example)
            btn.pack(side=tk.LEFT, padx=5)
        
        def insert_formula():
            formula = formula_text.get("1.0", tk.END).strip()
            if formula:
                # Rapora formülü ekle
                cursor_pos = self.result_text.index(tk.INSERT)
                self.result_text.insert(cursor_pos, f"\n$$\n{formula}\n$$\n")
                
                formula_dialog.destroy()
        
        insert_btn = ctk.CTkButton(formula_dialog, text="Formülü Ekle", command=insert_formula)
        insert_btn.pack(pady=20)

    def manage_references(self):
        """Kaynakları yönetme penceresi"""
        ref_dialog = ctk.CTkToplevel(self)
        ref_dialog.title("Kaynakları Yönet")
        ref_dialog.geometry("600x500")
        ref_dialog.transient(self)
        ref_dialog.grab_set()
        
        # Sol panel - Kaynak listesi
        left_frame = ctk.CTkFrame(ref_dialog)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(left_frame, text="Kaynaklar").pack(pady=(0, 5))
        
        reference_listbox = tk.Listbox(left_frame, bg="#2b2b2b", fg="white", selectbackground="#3E3E3E")
        reference_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Mevcut kaynakları ekle
        references = self.get_references_from_text()
        for ref in references:
            reference_listbox.insert(tk.END, ref)
        
        # Sağ panel - Düzenleme
        right_frame = ctk.CTkFrame(ref_dialog)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(right_frame, text="Kaynak Düzenle").pack(pady=(0, 5))
        
        ref_type_var = tk.StringVar(value="Kitap")
        ref_type_options = ["Kitap", "Makale", "Web Sayfası", "Dergi", "Diğer"]
        ref_type_menu = ctk.CTkOptionMenu(right_frame, variable=ref_type_var, values=ref_type_options)
        ref_type_menu.pack(padx=5, pady=5, fill=tk.X)
        
        # Alanlar
        fields_frame = ctk.CTkFrame(right_frame)
        fields_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Genel kaynak alanları
        ctk.CTkLabel(fields_frame, text="Yazar:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        author_entry = ctk.CTkEntry(fields_frame, width=200)
        author_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Başlık:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        title_entry = ctk.CTkEntry(fields_frame, width=200)
        title_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Yıl:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        year_entry = ctk.CTkEntry(fields_frame, width=200)
        year_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Yayıncı/Dergi:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        publisher_entry = ctk.CTkEntry(fields_frame, width=200)
        publisher_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Butonlar
        btn_frame = ctk.CTkFrame(right_frame)
        btn_frame.pack(padx=5, pady=5, fill=tk.X)
        
        def add_reference():
            ref_type = ref_type_var.get()
            author = author_entry.get().strip()
            title = title_entry.get().strip()
            year = year_entry.get().strip()
            publisher = publisher_entry.get().strip()
            
            if not (author and title):
                messagebox.showerror("Hata", "Yazar ve başlık alanları zorunludur.")
                return
            
            # Kaynak formatı oluştur
            reference = f"{author} ({year}). {title}. "
            if ref_type == "Kitap":
                reference += f"{publisher}."
            elif ref_type == "Makale":
                reference += f"{publisher}."
            elif ref_type == "Web Sayfası":
                reference += f"URL: {publisher}"
            else:
                reference += f"{publisher}."
            
            # Listeye ekle
            reference_listbox.insert(tk.END, reference)
            
            # Alanları temizle
            author_entry.delete(0, tk.END)
            title_entry.delete(0, tk.END)
            year_entry.delete(0, tk.END)
            publisher_entry.delete(0, tk.END)
        
        def remove_reference():
            selected = reference_listbox.curselection()
            if selected:
                reference_listbox.delete(selected)
        
        def update_references():
            # Kaynak listesini al
            references = list(reference_listbox.get(0, tk.END))
            
            # Raporda mevcut kaynakça bölümünü bul veya oluştur
            report_text = self.result_text.get("1.0", tk.END)
            
            # Mevcut kaynakça bölümünü bul
            kaynakca_start = report_text.find("7. Kaynakça")
            
            if kaynakca_start >= 0:
                # Metin içindeki sonraki bölümü bul
                next_section = report_text.find("8.", kaynakca_start)
                if next_section < 0:
                    next_section = len(report_text)
                
                # Eski kaynakçayı sil
                self.result_text.delete(f"1.0 + {kaynakca_start} chars", f"1.0 + {next_section} chars")
                
                # Yeni kaynakçayı ekle
                kaynakca_text = "7. Kaynakça\n\n"
                for i, ref in enumerate(references, 1):
                    kaynakca_text += f"[{i}] {ref}\n"
                
                self.result_text.insert(f"1.0 + {kaynakca_start} chars", kaynakca_text)
            else:
                # Rapora yeni kaynakça bölümü ekle
                kaynakca_text = "\n\n7. Kaynakça\n\n"
                for i, ref in enumerate(references, 1):
                    kaynakca_text += f"[{i}] {ref}\n"
                
                self.result_text.insert(tk.END, kaynakca_text)
            
            ref_dialog.destroy()
            messagebox.showinfo("Bilgi", "Kaynakça güncellendi.")
        
        add_btn = ctk.CTkButton(btn_frame, text="Ekle", command=add_reference, width=80)
        add_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        remove_btn = ctk.CTkButton(btn_frame, text="Sil", command=remove_reference, width=80)
        remove_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        update_btn = ctk.CTkButton(btn_frame, text="Güncelle", command=update_references, width=80)
        update_btn.pack(side=tk.LEFT, padx=5, pady=10)

    def get_references_from_text(self):
        """Rapor metninden kaynakları çıkarır"""
        references = []
        
        report_text = self.result_text.get("1.0", tk.END)
        
        # Kaynakça bölümünü bul
        kaynakca_start = report_text.find("7. Kaynakça")
        
        if kaynakca_start >= 0:
            # Kaynakça bölümünden sonraki metni al
            kaynakca_text = report_text[kaynakca_start:]
            
            # Satırlara böl
            lines = kaynakca_text.split('\n')
            
            # Kaynakları bul
            for line in lines:
                # [1] ile başlayan satırları bul
                if line.strip().startswith('[') and ']' in line:
                    # Köşeli parantezi kaldır
                    reference = line.strip()
                    reference = reference[reference.find(']')+1:].strip()
                    references.append(reference)
        
        return references
    
    def on_closing(self):
        """Pencere kapatıldığında çalışacak işlemler"""
        try:
            # Eğer kayıt devam ediyorsa durdur
            if hasattr(self, 'recording') and self.recording:
                self.audio_processor.recording = False  # Doğrudan recording değişkenini false yap
                # Kayıt thread'inin tamamlanmasını bekleme (bloke etmemek için)
            
            # Mevcut pencere durumunu kaydet
            if sys.platform == 'win32':
                current_state = "zoomed" if self.state() == 'zoomed' else "normal"
            else:
                try:
                    current_state = "maximized" if self.attributes('-zoomed') == '1' else "normal"
                except:
                    current_state = "normal"
            
            # Eğer pencere normal durumdaysa geometriyi kaydet
            if current_state == "normal":
                current_geometry = self.geometry()
            else:
                # Tam ekranda iken son normal boyutu kaybetmemek için mevcut kaydı kullan
                # Eğer saved_geometry henüz tanımlanmadıysa varsayılan değeri kullan
                current_geometry = getattr(self, 'saved_geometry', "1200x800")
            
            # Pencere durumunu kaydet
            self.config.save_window_state(current_geometry, current_state)
            
            # Temp klasörünü temizle - şimdi audio_processor'ın cleanup fonksiyonunu kullanıyoruz
            if hasattr(self, 'audio_processor'):
                # Sadece 6 saatten eski geçici dosyaları temizle
                self.audio_processor.cleanup_temp_files(older_than_hours=6)
                    
        except Exception as e:
            print(f"Kapatma işlemi sırasında hata: {e}")
        finally:
            # Pencereyi kapat
            self.quit()


def main():
    # Uygulama klasörlerini oluştur
    os.makedirs("audio_files", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    app = RaporApp()
    app.mainloop()


if __name__ == "__main__":
    main()
