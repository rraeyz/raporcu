import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Temel pencere ayarları
        self.title("Ayarlar")
        self.geometry("500x500")  # Pencere boyutunu artırıyorum çünkü daha fazla ayar ekleyeceğiz
        self.minsize(500, 500)  # Minimum pencere boyutunu da artırıyorum
        
        # Ana grid yapısı
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Ana container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Ana frame grid yapısı
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0)  # Başlık
        self.main_frame.grid_rowconfigure(1, weight=1)  # Ayarlar
        self.main_frame.grid_rowconfigure(2, weight=0)  # Butonlar
        
        # Başlık
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Uygulama Ayarları",
            font=("Helvetica", 16, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=10)
        
        # Ayarlar frame - Daha basit yapıda yeniden düzenliyorum
        self.settings_frame = ctk.CTkFrame(self.main_frame)
        self.settings_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Ayarlar frame grid yapısı - Her ayar için 2 satır (etiket ve değer)
        self.settings_frame.grid_columnconfigure(0, weight=1)
        
        # Ayarlar içerisindeki elementlerin hizalanması için yeni bir iç frame
        self.inner_settings_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.inner_settings_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.inner_settings_frame.grid_columnconfigure(0, weight=0)  # Etiket sütunu
        self.inner_settings_frame.grid_columnconfigure(1, weight=1)  # Değer sütunu
        
        # Satır takibi
        current_row = 0
        
        # 1. AI Model seçimi
        self.model_label = ctk.CTkLabel(self.inner_settings_frame, text="AI Model:")
        self.model_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
        
        self.model_var = tk.StringVar()
        self.model_combobox = ctk.CTkComboBox(
            self.inner_settings_frame,
            values=[
                "Gemini 2.0 Flash",
                "Gemini 2.5 Flash",
                "Gemini 2.5 Pro",
                "Claude 3 Opus",
                "Claude 3 Sonnet",
                "GPT-4 Turbo",
                "GPT-4",
                "GPT-3.5 Turbo"
            ],
            variable=self.model_var,
            command=self.on_model_change,
            width=250
        )
        self.model_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
        
        current_row += 1
        
        # 2. API Anahtarı
        self.api_provider_label = ctk.CTkLabel(self.inner_settings_frame, text="API Anahtarı:")
        self.api_provider_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
        
        # API Anahtarı giriş alanı ve göster/gizle için container
        api_container = ctk.CTkFrame(self.inner_settings_frame, fg_color="transparent")
        api_container.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
        api_container.grid_columnconfigure(0, weight=1)
        api_container.grid_columnconfigure(1, weight=0)
        
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ctk.CTkEntry(
            api_container,
            textvariable=self.api_key_var,
            show="*",
            width=200
        )
        self.api_key_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.show_api_var = tk.BooleanVar(value=False)
        self.show_api_btn = ctk.CTkCheckBox(
            api_container,
            text="Göster",
            variable=self.show_api_var,
            command=self.toggle_api_visibility,
            width=20
        )
        self.show_api_btn.grid(row=0, column=1, sticky="e")
        
        current_row += 1
        
        # 3. Ses Tanıma Motoru
        self.speech_engine_label = ctk.CTkLabel(self.inner_settings_frame, text="Ses Tanıma Motoru:")
        self.speech_engine_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
        
        self.speech_engine_var = tk.StringVar()
        self.speech_engine_combobox = ctk.CTkComboBox(
            self.inner_settings_frame,
            values=["Whisper", "Google Speech"],
            variable=self.speech_engine_var,
            width=250
        )
        self.speech_engine_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
        
        current_row += 1
        
        # 4. Dil
        self.language_label = ctk.CTkLabel(self.inner_settings_frame, text="Dil:")
        self.language_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
        
        self.language_var = tk.StringVar()
        self.language_combobox = ctk.CTkComboBox(
            self.inner_settings_frame,
            values=["Türkçe", "İngilizce"],
            variable=self.language_var,
            width=250
        )
        self.language_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
        
        current_row += 1
        
        # 5. YENİ: Tema Seçimi
        self.theme_label = ctk.CTkLabel(self.inner_settings_frame, text="Tema:")
        self.theme_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
        
        self.theme_var = tk.StringVar()
        self.theme_combobox = ctk.CTkComboBox(
            self.inner_settings_frame,
            values=["Sistem", "Koyu", "Açık"],
            variable=self.theme_var,
            width=250
        )
        self.theme_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
        
        current_row += 1
        
        # 6. YENİ: Yazı Tipi Boyutu
        self.font_size_label = ctk.CTkLabel(self.inner_settings_frame, text="Yazı Tipi Boyutu:")
        self.font_size_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
        
        font_size_frame = ctk.CTkFrame(self.inner_settings_frame, fg_color="transparent")
        font_size_frame.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
        font_size_frame.grid_columnconfigure(0, weight=1)
        font_size_frame.grid_columnconfigure(1, weight=0)
        
        self.font_size_var = tk.IntVar(value=12)
        self.font_size_slider = ctk.CTkSlider(
            font_size_frame,
            from_=10,
            to=18,
            number_of_steps=8,
            variable=self.font_size_var,
            command=self.on_font_size_change
        )
        self.font_size_slider.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.font_size_value_label = ctk.CTkLabel(
            font_size_frame,
            text="12 pt",
            width=50
        )
        self.font_size_value_label.grid(row=0, column=1, sticky="e")
        
        current_row += 1
        
        # 7. YENİ: Rapor Şablonu Seçimi
        self.template_label = ctk.CTkLabel(self.inner_settings_frame, text="Rapor Şablonu:")
        self.template_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
        
        # Şablon bilgileri
        template_names = self.parent.config.get_template_names()
        template_values = list(template_names.values())
        template_keys = list(template_names.keys())
        
        self.template_var = tk.StringVar()
        self.template_combobox = ctk.CTkComboBox(
            self.inner_settings_frame,
            values=template_values,
            variable=self.template_var,
            width=250,
            state="readonly",
            command=self.on_template_change
        )
        self.template_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
        
        # Şablon açıklaması için etiket
        current_row += 1
        self.template_desc_label = ctk.CTkLabel(
            self.inner_settings_frame, 
            text="", 
            wraplength=400,
            justify="left",
            anchor="w"
        )
        self.template_desc_label.grid(row=current_row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        current_row += 1
        
        # Esnek boşluk
        spacer = ctk.CTkFrame(self.inner_settings_frame, fg_color="transparent", height=20)
        spacer.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Butonlar frame
        self.buttons_frame = ctk.CTkFrame(self.main_frame)
        self.buttons_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        # Butonlar frame grid yapısı
        self.buttons_frame.grid_columnconfigure(0, weight=1)  # Boşluk
        self.buttons_frame.grid_columnconfigure(1, weight=0)  # İptal butonu
        self.buttons_frame.grid_columnconfigure(2, weight=0)  # Kaydet butonu
        
        # İptal butonu
        self.cancel_btn = ctk.CTkButton(
            self.buttons_frame,
            text="❌ İptal",
            command=self.destroy,
            fg_color="#AA5555",
            width=100
        )
        self.cancel_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Kaydet butonu
        self.save_btn = ctk.CTkButton(
            self.buttons_frame,
            text="💾 Kaydet",
            command=self.save_settings,
            fg_color="#2AAA8A",
            width=100
        )
        self.save_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Ayarları yükle
        self.load_settings()
        
        # İlk model seçimine göre API giriş alanını güncelle
        self.update_api_key_section(self.model_var.get())
    
    def toggle_api_visibility(self):
        """API anahtarını göster/gizle"""
        if self.show_api_var.get():
            self.api_key_entry.configure(show="")
        else:
            self.api_key_entry.configure(show="*")
    
    def update_api_key_section(self, model_name):
        """Seçilen modele göre API anahtar bölümünü güncelle"""
        if not model_name:
            return
            
        model_info = self.parent.config.available_models.get(model_name, {})
        provider = model_info.get("provider", "")
        
        if provider:
            # API etiketi güncelleniyor
            self.api_provider_label.configure(text=f"{provider} API Anahtarı:")
            
            # Mevcut seçilen sağlayıcının API anahtarını göster
            current_api_key = self.parent.config.api_keys.get(provider, "")
            self.api_key_var.set(current_api_key)
    
    def on_model_change(self, model_name):
        """Model değiştiğinde çağrılır"""
        self.update_api_key_section(model_name)
    
    def on_template_change(self, template_name):
        """Şablon değiştiğinde çağrılır"""
        print(f"on_template_change çağrıldı. Seçilen şablon: {template_name}")
        
        # Şablon adına göre şablon ID'sini bul
        template_names = self.parent.config.get_template_names()
        template_keys = list(template_names.keys())
        template_values = list(template_names.values())
        
        print(f"Şablon anahtarları: {template_keys}")
        print(f"Şablon değerleri: {template_values}")
        
        if template_name in template_values:
            template_index = template_values.index(template_name)
            template_id = template_keys[template_index]
            
            print(f"Şablon adından ID bulundu: {template_id}")
            
            # Aktif şablonu güncelle
            success = self.parent.config.set_active_template(template_id)
            print(f"Şablon güncellemesi başarılı mı: {success}")
            
            # Şablon açıklamasını güncelle
            template_data = self.parent.config.templates.get(template_id, {})
            template_description = template_data.get("description", "")
            self.template_desc_label.configure(text=template_description)
        else:
            print(f"Şablon adı bulunamadı: {template_name}")
    
    def load_settings(self):
        """Mevcut ayarları yükle"""
        config = self.parent.config
        
        # Model
        self.model_var.set(config.ai_model)
        
        # Seçilen modelin API anahtarını yükle
        provider = config.get_current_provider()
        self.api_key_var.set(config.api_keys.get(provider, ""))
        
        # Ses tanıma motoru
        self.speech_engine_var.set(config.speech_recognition_engine)
        
        # Dil
        self.language_var.set(config.language)
        
        # YENİ: Tema
        self.theme_var.set(config.theme)
        
        # YENİ: Yazı tipi boyutu
        self.font_size_var.set(config.font_size)
        self.font_size_value_label.configure(text=f"{config.font_size} pt")
        
        # YENİ: Şablon
        active_template = config.get_active_template()
        template_name = active_template.get("name", "")
        if template_name and template_name in self.template_combobox._values:
            self.template_var.set(template_name)
            # Şablon açıklamasını güncelle
            self.template_desc_label.configure(text=active_template.get("description", ""))
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            # Ayarları güncelle
            selected_model = self.model_var.get()
            self.parent.config.ai_model = selected_model
            
            # Seçilen modelin sağlayıcısının API anahtarını güncelle
            provider = self.parent.config.available_models.get(selected_model, {}).get("provider", "")
            if provider:
                self.parent.config.api_keys[provider] = self.api_key_var.get()
            
            self.parent.config.speech_recognition_engine = self.speech_engine_var.get()
            self.parent.config.language = self.language_var.get()
            
            # YENİ: Tema ve yazı tipi ayarlarını kaydet
            self.parent.config.theme = self.theme_var.get()
            self.parent.config.font_size = self.font_size_var.get()
            
            # YENİ: Seçilen şablonu kaydet
            template_name = self.template_var.get()
            if template_name:
                template_names = self.parent.config.get_template_names()
                template_keys = list(template_names.keys())
                template_values = list(template_names.values())
                
                if template_name in template_values:
                    template_index = template_values.index(template_name)
                    template_id = template_keys[template_index]
                    self.parent.config.set_active_template(template_id)
              # Ayarları kaydet
            self.parent.config.save_settings()
            
            # AI servisini tamamen yeniden başlat
            self.parent.ai_service.current_client = None
            # Önceki sağlayıcı önbelleğini temizle
            provider = self.parent.config.get_current_provider()
            if provider in self.parent.ai_service._provider_clients:
                self.parent.ai_service._provider_clients[provider] = None
            
            # YENİ: Tema ve yazı tipi değişikliklerini uygula
            self.parent.apply_theme_settings()
            self.parent.apply_font_settings()
            
            messagebox.showinfo("Başarılı", "Ayarlar başarıyla kaydedildi!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilirken bir hata oluştu: {str(e)}")
    
    def on_font_size_change(self, value):
        """Yazı tipi boyutu değeri değiştiğinde çağrılır"""
        size = int(value)
        self.font_size_value_label.configure(text=f"{size} pt")
        self.font_size_var.set(size)