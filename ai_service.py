import os
import importlib
from typing import Optional
import threading

class AIService:
    """Yapay zeka servisleri için sınıf"""
    def __init__(self, config):
        self.config = config
        self.current_client = None
        # Claude API'ye otomatik geçiş yapmak için
        self.fallback_to_anthropic = True
        
        # Lazy loading için cache
        self._loaded_modules = {}
        self._provider_clients = {}

    def _check_and_import(self, module_name: str) -> bool:
        """Gerekli modülün yüklü olup olmadığını kontrol eder ve sonucu cache'ler"""
        # Eğer daha önce kontrol edildiyse sonucu döndür
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]
            
        try:
            __import__(module_name)
            self._loaded_modules[module_name] = True
            return True
        except ImportError:
            print(f"{module_name} modülü yüklü değil!")
            self._loaded_modules[module_name] = False
            return False

    def initialize_client(self) -> bool:
        """Seçili modele göre ilgili API istemcisini başlatır"""
        model_info = self.config.available_models.get(self.config.ai_model)
        if not model_info:
            print("Geçersiz model seçimi!")
            return False

        provider = model_info["provider"]
        
        # API anahtarını kontrol et
        api_key = self.config.api_keys.get(provider, "")
        if not api_key:
            print(f"{provider} için API anahtarı bulunamadı!")
            return False
        
        # Eğer aynı sağlayıcı için önceden oluşturulmuş bir istemci varsa, anahtarın değişip değişmediğini kontrol et
        if provider in self._provider_clients:
            # API anahtarı değişmişse, istemciyi yenile
            current_client_info = getattr(self, f"_{provider.lower()}_api_key", None)
            if current_client_info != api_key:
                # API anahtarı değişmiş, istemciyi sıfırla
                self._provider_clients[provider] = None
        
        # Eğer aynı sağlayıcı için önceden oluşturulmuş bir istemci varsa onu kullan
        if provider in self._provider_clients and self._provider_clients[provider]:
            self.current_client = self._provider_clients[provider]
            return True
        
        try:
            if provider == "Google":
                if self._check_and_import("google.generativeai"):
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    client = genai.GenerativeModel(model_info['name'])
                    self._provider_clients["Google"] = client
                    self.current_client = client
                    setattr(self, "_google_api_key", api_key)
                    
            elif provider == "Anthropic":
                if self._check_and_import("anthropic"):
                    from anthropic import Anthropic
                    client = Anthropic(api_key=api_key)
                    self._provider_clients["Anthropic"] = client
                    self.current_client = client
                    setattr(self, "_anthropic_api_key", api_key)
                    
            elif provider == "OpenAI":
                if self._check_and_import("openai"):
                    import openai
                    client = openai.OpenAI(api_key=api_key)
                    self._provider_clients["OpenAI"] = client
                    self.current_client = client
                    setattr(self, "_openai_api_key", api_key)
            
            return True if self.current_client else False
            
        except Exception as e:
            print(f"API istemcisi başlatılırken hata: {e}")
            return False

    def generate_response(self, prompt: str) -> Optional[str]:
        """Seçili modele göre yanıt üretir"""
        if not self.current_client:
            if not self.initialize_client():
                return "API bağlantısı kurulamadı. Lütfen API anahtarını kontrol edin."

        try:
            model_info = self.config.available_models.get(self.config.ai_model)
            provider = model_info["provider"]

            if provider == "Google":
                # Hata ayıklama bilgisi
                print(f"Google API kullanılıyor, model: {model_info['name']}")
                try:
                    response = self.current_client.generate_content(prompt)
                    return response.text
                except Exception as e:
                    error_msg = str(e)
                    print(f"Google API hatası: {error_msg}")
                    
                    # Kullanıcıya daha anlaşılır hata mesajları
                    if "rate limit" in error_msg.lower():
                        return "Google API istek limiti aşıldı. Lütfen daha sonra tekrar deneyin."
                    elif "invalid api key" in error_msg.lower():
                        return "Google API anahtarı geçersiz. Lütfen ayarlardan kontrol edin."
                    elif "model not found" in error_msg.lower():
                        return "Seçilen model bulunamadı. Model adını kontrol edin veya başka bir model seçin."
                    
                    # Alternatif olarak başka bir modeli dene
                    if hasattr(self, 'fallback_to_anthropic') and self.fallback_to_anthropic:
                        print("Claude API'ye geçiş yapılıyor...")
                        self.config.ai_model = "Claude 3 Sonnet"
                        return self.generate_response(prompt)
                    return "API hatası: " + error_msg
                
            elif provider == "Anthropic":
                try:
                    response = self.current_client.messages.create(
                        model=model_info["name"].lower(),
                        max_tokens=model_info["max_tokens"],
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.content[0].text
                except Exception as e:
                    error_msg = str(e)
                    print(f"Anthropic API hatası: {error_msg}")
                    
                    if "rate limit" in error_msg.lower():
                        return "Claude API istek limiti aşıldı. Lütfen daha sonra tekrar deneyin."
                    elif "invalid api key" in error_msg.lower():
                        return "Claude API anahtarı geçersiz. Lütfen ayarlardan kontrol edin."
                    return "Claude API hatası: " + error_msg
                
            elif provider == "OpenAI":
                try:
                    response = self.current_client.chat.completions.create(
                        model=model_info["name"],
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    error_msg = str(e)
                    print(f"OpenAI API hatası: {error_msg}")
                    
                    if "rate limit" in error_msg.lower():
                        return "OpenAI API istek limiti aşıldı. Lütfen daha sonra tekrar deneyin."
                    elif "invalid api key" in error_msg.lower():
                        return "OpenAI API anahtarı geçersiz. Lütfen ayarlardan kontrol edin."
                    elif "model not found" in error_msg.lower():
                        return "Seçilen model bulunamadı. Model adını kontrol edin veya başka bir model seçin."
                    return "OpenAI API hatası: " + error_msg
                
        except Exception as e:
            error_msg = str(e)
            print(f"Yanıt üretilirken hata: {error_msg}")
            return "Beklenmeyen bir hata oluştu: " + error_msg
            
    def generate_report(self, deney_basligi: str, deneyin_yapilisi: str, referans_metin: str = "") -> Optional[str]:
        """
        Deney raporu oluşturur
        
        Args:
            deney_basligi: Deneyin başlığı
            deneyin_yapilisi: Deneyin yapılış adımları
            referans_metin: Referans metin (opsiyonel)
            
        Returns:
            Oluşturulan rapor metni veya hata durumunda None
        """
        try:
            prompt = ""
            if not referans_metin:
                # Referans metin/döküman girilmemişse
                prompt = f""""{deney_basligi}" adlı deney için bilimsel bir rapor yaz. 

Aşağıdaki bilgilere dayanarak tüm bölümleri doğrudan ve nesnel biçimde hazırla:

Deneyin yapılışı:
{deneyin_yapilisi}

Rapor şu bölümleri içermeli (TAM OLARAK AŞAĞIDAKİ BAŞLIKLARI KULLAN):
{deney_basligi}
Amaçlar
Teorik Bilgiler
Malzemeler
Deneyin Yapılışı ve Hesaplamalar
Sonuç ve Yorumlar
Kaynakça

ÖNEMLİ KURALLAR:
1. İlk başlık kesinlikle sadece "{deney_basligi}" olmalı, başında numara olmamalı.
2. Diğer başlıkların (Amaçlar, Teorik Bilgiler vb.) başına numara ekleme, numaralandırma rapor işleme sırasında yapılacak.
3. Raporu doğrudan başlıkla başlat, raporun parçası olmayan hiçbir ek giriş cümlesi ekleme.
4. Tüm metinler 12 punto boyutunda ve siyah renkte olmalıdır, başlıklar kalın olacaktır.
5. Başlıklar mutlaka kendi satırlarında olmalıdır, başlık ile içerik arasında boş satır bırak.
6. Alt başlıklar (Amaçlar, Teorik Bilgiler vb.) mutlaka KALIN ve SOLA HİZALI olmalıdır."""
            else:
                # Referans metin/döküman girilmişse
                prompt = f""""{deney_basligi}" adlı deney için bilimsel bir rapor yaz.

Aşağıdaki bilgilere dayanarak tüm bölümleri doğrudan ve nesnel biçimde hazırla:

Deneyin yapılışı:
{deneyin_yapilisi}

Referans metin:
{referans_metin}

Rapor şu bölümleri içermeli (TAM OLARAK AŞAĞIDAKİ BAŞLIKLARI KULLAN):
{deney_basligi}
Amaçlar
Teorik Bilgiler
Malzemeler
Deneyin Yapılışı ve Hesaplamalar
Sonuç ve Yorumlar
Kaynakça

ÖNEMLİ KURALLAR:
1. İlk başlık kesinlikle sadece "{deney_basligi}" olmalı, başında numara olmamalı.
2. Diğer başlıkların (Amaçlar, Teorik Bilgiler vb.) başına numara ekleme, numaralandırma rapor işleme sırasında yapılacak.
3. Raporu doğrudan başlıkla başlat, raporun parçası olmayan hiçbir ek giriş cümlesi ekleme.
4. Tüm metinler 12 punto boyutunda ve siyah renkte olmalıdır, başlıklar kalın olacaktır.
5. Başlıklar mutlaka kendi satırlarında olmalıdır, başlık ile içerik arasında boş satır bırak.
6. Alt başlıklar (Amaçlar, Teorik Bilgiler vb.) mutlaka KALIN ve SOLA HİZALI olmalıdır."""
            
            # Yanıt oluştur
            return self.generate_response(prompt)
            
        except Exception as e:
            print(f"Rapor oluşturulurken hata: {e}")
            return None
