import os
import json
import threading

class Config:
    """Uygulama konfigürasyon sınıfı"""
    def __init__(self, async_load=True):
        # Temel ayarları hemen yükle
        self._initialize_base_settings()
        
        # Eğer asenkron yükleme isteniyorsa
        if async_load:
            # Diğer ayarları arka planda yükle
            threading.Thread(target=self._load_additional_settings, daemon=True).start()
        else:
            # Senkron olarak tüm ayarları hemen yükle
            self._load_additional_settings()
    
    def _initialize_base_settings(self):
        """Temel ayarları yükle"""
        # AI Model seçenekleri
        self.available_models = {
            "Gemini 2.0 Flash": {
                "name": "gemini-2.0-flash",
                "provider": "Google",
                "max_tokens": 30720
            },
            "Gemini 2.5 Flash": {
                "name": "gemini-2.5-flash-preview-05-20",
                "provider": "Google", 
                "max_tokens": 30720
            },
            "Gemini 2.5 Pro": {
                "name": "gemini-2.5-pro-preview-05-06",
                "provider": "Google",
                "max_tokens": 30720
            },
            "Claude 3 Opus": {
                "name": "claude-3-opus",
                "provider": "Anthropic",
                "max_tokens": 200000
            },
            "Claude 3 Sonnet": {
                "name": "claude-3-sonnet",
                "provider": "Anthropic",
                "max_tokens": 100000
            },
            "GPT-4 Turbo": {
                "name": "gpt-4-turbo-preview",
                "provider": "OpenAI",
                "max_tokens": 128000
            },
            "GPT-4": {
                "name": "gpt-4",
                "provider": "OpenAI",
                "max_tokens": 8192
            },
            "GPT-3.5 Turbo": {
                "name": "gpt-3.5-turbo",
                "provider": "OpenAI",
                "max_tokens": 4096
            }
        }

        # Varsayılan ayarlar
        self.ai_model = "Gemini 2.5 Pro"  # Varsayılan model güncellendi
        
        # Her sağlayıcı için ayrı API anahtarları
        self.api_keys = {
            "Google": "",
            "Anthropic": "",
            "OpenAI": ""
        }
        
        self.speech_recognition_engine = "Whisper"
        self.language = "Türkçe"
        self.audio_segment_length = 30  # saniye
        
        # YENİ: Kullanıcı arayüzü ayarları
        self.theme = "Sistem"  # Sistem, Koyu veya Açık
        self.font_size = 12    # Varsayılan yazı tipi boyutu
        
        # Dosya yolları
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_dir = os.path.join(self.base_dir, "audio_files")
        self.temp_dir = os.path.join(self.base_dir, "temp")
        self.config_file = os.path.join(self.base_dir, "settings.json")
        self.templates_dir = os.path.join(self.base_dir, "templates")
        
        # Şablon sistemi
        self.active_template = "standard"  # Varsayılan şablon
        self.templates = {}  # Şablonlar bu sözlükte saklanacak
        
        # Kritik klasörleri oluştur
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def _load_additional_settings(self):
        """Ek ayarları arka planda yükle"""
        self.load_settings()
        self.load_templates()
    
    def load_settings(self):
        """Ayarları yapılandırma dosyasından yükler"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Ayarları güncelle
                self.ai_model = settings.get('ai_model', self.ai_model)
                
                # Her sağlayıcı için API anahtarları
                saved_api_keys = settings.get('api_keys', {})
                for provider in self.api_keys:
                    if provider in saved_api_keys:
                        self.api_keys[provider] = saved_api_keys[provider]
                
                self.speech_recognition_engine = settings.get('speech_recognition_engine', self.speech_recognition_engine)
                self.language = settings.get('language', self.language)
                self.audio_segment_length = settings.get('audio_segment_length', self.audio_segment_length)
                
                # YENİ: Kullanıcı arayüzü ayarlarını yükle
                self.theme = settings.get('theme', self.theme)
                self.font_size = settings.get('font_size', self.font_size)
                
                # Şablon ayarını yükle
                self.active_template = settings.get('active_template', self.active_template)
                
                # Pencere durumu ayarlarını yükle
                self.window_settings = settings.get('window', {"geometry": "1200x800", "state": "normal"})
        except Exception as e:
            print(f"Ayarlar yüklenirken hata oluştu: {e}")
    
    def save_settings(self):
        """Ayarları yapılandırma dosyasına kaydeder"""
        try:
            settings = {
                'ai_model': self.ai_model,
                'api_keys': self.api_keys,
                'speech_recognition_engine': self.speech_recognition_engine,
                'language': self.language,
                'audio_segment_length': self.audio_segment_length,
                'window': getattr(self, 'window_settings', {"geometry": "1200x800", "state": "normal"}),
                'theme': self.theme,
                'font_size': self.font_size,
                'active_template': self.active_template
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            return True
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata oluştu: {e}")
            return False
    
    def load_settings_from_file(self):
        """Ayarları JSON dosyasından yükler"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    print(f"Ayarlar dosyadan yüklendi: {settings}")
                    return settings
            else:
                print("Ayarlar dosyası bulunamadı, varsayılanlar kullanılacak")
                return {}
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
            return {}
    
    def save_settings_to_file(self, settings):
        """Ayarları JSON dosyasına kaydeder"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                print(f"Ayarlar dosyaya kaydedildi: {settings}")
            return True
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
            return False

    def save_settings_to_file(self, settings):
        """Ayarları doğrudan yapılandırma dosyasına kaydeder"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Ayarlar dosyası yazılırken hata: {e}")
            return False
    
    def get_model_name(self):
        """AI model adını API için uygun formata dönüştürür"""
        model_info = self.available_models.get(self.ai_model, {})
        return model_info.get("name", "gpt-3.5-turbo")
    
    def get_current_provider(self):
        """Mevcut modelin sağlayıcısını döndürür"""
        model_info = self.available_models.get(self.ai_model, {})
        return model_info.get("provider", "OpenAI")
    
    def get_api_key_for_current_model(self):
        """Mevcut model için API anahtarını döndürür"""
        provider = self.get_current_provider()
        return self.api_keys.get(provider, "")
    
    def get_language_code(self):
        """Dil kodunu döndürür"""
        language_codes = {
            "Türkçe": "tr-TR",
            "İngilizce": "en-US"
        }
        return language_codes.get(self.language, "tr-TR")
    
    def save_window_state(self, geometry, state):
        """Pencere durumunu ve konumunu kaydeder"""
        try:
            # Mevcut ayarları yükle
            settings = self.load_settings_from_file()
            
            # Pencere durumunu ekle
            settings["window"] = {
                "geometry": geometry,
                "state": state
            }
            
            # Ayarları dosyaya yaz
            self.save_settings_to_file(settings)
            return True
        except Exception as e:
            print(f"Pencere durumu kaydedilemedi: {e}")
            return False

    def get_window_state(self):
        """Kaydedilen pencere durumunu döndürür"""
        try:
            # Mevcut ayarları yükle
            settings = self.load_settings_from_file()
            
            # Pencere durumunu al
            window_settings = settings.get("window", {})
            geometry = window_settings.get("geometry", "1200x800")
            state = window_settings.get("state", "normal")
            
            return geometry, state
        except Exception as e:
            print(f"Pencere durumu okunamadı: {e}")
            return "1200x800", "normal"  # Varsayılan değerler
            
    def load_templates(self):
        """Tüm şablonları yükler"""
        try:
            self.templates = {}
            template_files = [f for f in os.listdir(self.templates_dir) if f.endswith('.json')]
            
            print(f"Bulunan şablon dosyaları: {template_files}")
            
            for template_file in template_files:
                template_path = os.path.join(self.templates_dir, template_file)
                template_id = os.path.splitext(template_file)[0]
                
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        self.templates[template_id] = template_data
                        print(f"Şablon yüklendi: {template_id} - {template_data.get('name', 'Bilinmiyor')}")
                except Exception as e:
                    print(f"Şablon yüklenemedi {template_path}: {e}")
            
            # Aktif şablonu ayarla
            settings = self.load_settings_from_file()
            old_active_template = self.active_template
            self.active_template = settings.get('active_template', 'standard')
            
            print(f"Aktif şablon ayarlardan güncellendi: {old_active_template} -> {self.active_template}")
            
            # Eğer aktif şablon yüklenmemişse, varsayılan şablonu kullan
            if self.active_template not in self.templates and self.templates:
                old_active_template = self.active_template
                self.active_template = list(self.templates.keys())[0]
                print(f"Aktif şablon bulunamadığı için ilk şablon kullanılıyor: {old_active_template} -> {self.active_template}")
            
            print(f"Toplam {len(self.templates)} şablon yüklendi. Aktif şablon: {self.active_template}")
            return True
        except Exception as e:
            print(f"Şablonlar yüklenirken hata: {e}")
            return False
    
    def get_template_names(self):
        """Şablon isimlerini döndürür"""
        template_names = {template_id: template.get('name', template_id) for template_id, template in self.templates.items()}
        print(f"Mevcut şablonlar: {template_names}")
        return template_names
    
    def get_active_template(self):
        """Aktif şablonu döndürür"""
        active_template = self.templates.get(self.active_template, {})
        print(f"get_active_template çağrıldı. Aktif şablon ID: {self.active_template}")
        print(f"Döndürülen şablon: {active_template.get('name', 'Bilinmiyor')}")
        return active_template
    
    def set_active_template(self, template_id):
        """Aktif şablonu değiştirir"""
        print(f"set_active_template çağrıldı. Yeni şablon ID: {template_id}")
        if template_id in self.templates:
            self.active_template = template_id
            
            # Ayarları güncelle
            settings = self.load_settings_from_file()
            settings['active_template'] = template_id
            self.save_settings_to_file(settings)
            
            print(f"Aktif şablon değiştirildi: {template_id}")
            return True
        print(f"Şablon bulunamadı: {template_id}")
        return False
