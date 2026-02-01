import os
import time
import wave
import threading
import tempfile
import shutil
from datetime import datetime
from pydub import AudioSegment
import pyaudio
import speech_recognition as sr

# Whisper modülünü isteğe bağlı olarak içe aktarma
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Whisper modülü bulunamadı. Ses tanıma için alternatif yöntemler kullanılacak.")

class AudioProcessor:
    """Ses işleme ve konuşma tanıma sınıfı"""
    def __init__(self, parent):
        self.parent = parent
        self.config = parent.config
        
        # Kayıt değişkenleri
        self.recording = False
        self.paused = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.temp_file_path = None
        self.recording_thread = None
        
        # Kayıt formatı ayarları
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        
        # Whisper modeli
        self.whisper_model = None
        
        # Speech Recognition optimizasyonları
        self.recognizer = sr.Recognizer()
        self.recognizer.operation_timeout = 60
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 3000
        self.recognizer.pause_threshold = 1
    
    def start_recording(self):
        """Ses kaydını başlatır"""
        self.recording = True
        self.paused = False
        self.frames = []
        
        # Zaman dampalı geçici dosya oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_file_path = os.path.join(self.config.temp_dir, f"recording_{timestamp}.wav")
        
        # Ses akışını başlat
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        print("Kayıt başladı.")
        
        # Kayıt döngüsü
        while self.recording:
            if not self.paused:
                try:
                    data = self.stream.read(self.chunk)
                    self.frames.append(data)
                except Exception as e:
                    print(f"Kayıt hatası: {e}")
                    break
            else:
                # Duraklatıldığında kısa bekle
                time.sleep(0.1)
        
        # Kayıt bitti, ses akışını kapat
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        # Kaydedilen ses dosyasını kaydet
        if self.frames:
            self._save_recording()
        
        print("Kayıt durduruldu.")
    
    def pause_recording(self):
        """Ses kaydını duraklatır"""
        self.paused = True
    
    def resume_recording(self):
        """Duraklatılmış ses kaydını devam ettirir"""
        self.paused = False
    
    def stop_recording(self):
        """Ses kaydını durdurur"""
        self.recording = False
        
        try:
            # Kayıt thread'i bekleme
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join()
            
            # Kayıt durumunu güncelle - ProgressIndicator kullanılarak
            self.parent.audio_progress.set_status("Ses Dosyası Hazır")
            self.parent.process_audio_btn.configure(state="normal")
                
        except Exception as e:
            print(f"Kayıt durdurulurken hata: {e}")
            # Hata durumunda ilerleme göstergesini güncelle
            self.parent.audio_progress.set_error("Hata!")
    
    def _save_recording(self):
        """Kaydedilen ses verilerini dosyaya kaydeder"""
        try:
            with wave.open(self.temp_file_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
            
            print(f"Kayıt dosyaya kaydedildi: {self.temp_file_path}")
            return True
        except Exception as e:
            print(f"Kayıt dosyası kaydedilirken hata: {e}")
            return False
    
    def _optimize_audio(self, file_path):
        """Ses dosyasını Speech Recognition için optimize eder"""
        try:
            ses = AudioSegment.from_file(file_path)
            
            # Ses özelliklerini yazdır (debug)
            print(f"Orijinal ses: {len(ses)/1000} sn, {ses.frame_rate} Hz, {ses.channels} kanal, {ses.frame_width*8} bit")
            
            # Normalize et - ses seviyesini standartlaştır
            # headroom=1.0 ile aşırı yükseltmeyi önle
            normalized = ses.normalize(headroom=1.0)
            
            # 16000 Hz'e dönüştür (speech recognition için optimal)
            normalized = normalized.set_frame_rate(16000)
            
            # Mono kanala dönüştür
            normalized = normalized.set_channels(1)
            
            # 16-bit derinliğe dönüştür
            normalized = normalized.set_sample_width(2)
            
            # Sessizlik kaldırma (başta ve sonda)
            silence_threshold = -40  # dB cinsinden, daha düşük = daha hassas
            normalized = normalized.strip_silence(silence_thresh=silence_threshold, silence_len=500)
            
            # Geçici optimize edilmiş dosya oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            optimize_dosya = os.path.join(
                self.config.temp_dir, 
                f"optimize_{timestamp}.wav"
            )
            
            # Optimize edilmiş sesi kaydet
            normalized.export(optimize_dosya, format="wav", parameters=["-ar", "16000", "-sample_fmt", "s16"])
            print(f"Ses dosyası optimize edildi: {optimize_dosya}")
            
            # Optimize edilmiş dosya özelliklerini kontrol et
            optimized = AudioSegment.from_file(optimize_dosya)
            print(f"Optimize ses: {len(optimized)/1000} sn, {optimized.frame_rate} Hz, {optimized.channels} kanal, {optimized.frame_width*8} bit")
            
            return optimize_dosya
            
        except Exception as e:
            print(f"Ses optimizasyonu hatası: {e}")
            return file_path
    
    def process_audio_file(self, file_path):
        """Ses dosyasını metne dönüştürür"""
        try:
            # Önce ses dosyasını optimize et
            print("Ses dosyası optimize ediliyor...")
            optimized_file = self._optimize_audio(file_path)
            
            # Ses dosyasını parçalara ayır
            print("Ses dosyası parçalara ayrılıyor...")
            segments = self._split_audio(optimized_file)
            
            if not segments:
                raise Exception("Ses dosyası parçalanamadı!")
            
            # Her bir parçayı işle ve metinleri birleştir
            transcribed_text = []
            total_segments = len(segments)
            
            for i, segment in enumerate(segments, 1):
                print(f"\nParça {i}/{total_segments} işleniyor...")
                
                # İlk olarak seçilen motor ile dene
                segment_text = None
                
                # Seçilen motora göre ses tanıma
                if self.config.speech_recognition_engine == "Whisper" and WHISPER_AVAILABLE:
                    segment_text = self._transcribe_with_whisper(segment)
                    print("Whisper ile ses tanıma denendi")
                else:
                    # Whisper mevcut değilse veya başka bir motor seçilmişse Google kullan
                    if self.config.speech_recognition_engine == "Whisper" and not WHISPER_AVAILABLE:
                        print("Whisper modülü bulunamadığı için Google Speech API kullanılıyor.")
                    segment_text = self._transcribe_with_google(segment)
                    print("Google Speech API ile ses tanıma denendi")
                
                # İlk yöntem başarısız olduysa, alternatif yöntemi dene
                if segment_text is None:
                    print("İlk tanıma yöntemi başarısız oldu, alternatif yöntem deneniyor...")
                    
                    # Eğer Whisper başarısız olduysa, Google dene
                    if self.config.speech_recognition_engine == "Whisper" and WHISPER_AVAILABLE:
                        segment_text = self._transcribe_with_google(segment)
                        print("Alternatif olarak Google Speech API denendi")
                    # Eğer Google başarısız olduysa ve Whisper mevcutsa, Whisper dene
                    elif WHISPER_AVAILABLE:
                        segment_text = self._transcribe_with_whisper(segment)
                        print("Alternatif olarak Whisper denendi")
                
                if segment_text:
                    transcribed_text.append(segment_text)
                    print(f"Parça {i} metni: {segment_text}")
                else:
                    print(f"Parça {i} için ses tanıma başarısız oldu!")
                
                # Geçici dosyayı temizle
                if os.path.exists(segment):
                    os.remove(segment)
            
            # Optimize edilmiş dosyayı temizle
            if os.path.exists(optimized_file) and optimized_file != file_path:
                os.remove(optimized_file)
            
            # Eğer hiç metin çıkarılamadıysa hata ver
            if not transcribed_text:
                raise Exception("Ses tanıma başarısız oldu! Hiçbir metin çıkarılamadı.")
                
            return " ".join(transcribed_text)
            
        except Exception as e:
            print(f"Ses dosyası işlenirken hata: {e}")
            return None
        
    def _convert_to_wav(self, file_path):
        """Ses dosyasını wav formatına dönüştürür"""
        try:
            # Dosya uzantısını kontrol et
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.wav':
                # Zaten wav ise aynısını döndür
                return file_path
            
            # Geçici wav dosyası oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.config.temp_dir, f"converted_{timestamp}.wav")
            
            # Dönüştürme işlemi
            audio = AudioSegment.from_file(file_path)
            audio.export(output_path, format="wav")
            
            print(f"Ses dosyası wav formatına dönüştürüldü: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Ses dosyası dönüştürülürken hata: {e}")
            return file_path  # Hata durumunda orijinal dosyayı döndür
    
    def _split_audio(self, file_path, chunk_length=30000):
        """Ses dosyasını 30 saniyelik parçalara böler"""
        try:
            ses = AudioSegment.from_file(file_path)
            parcalar = []
            
            # Sesi parçalara böl
            for i in range(0, len(ses), chunk_length):
                parca = ses[i:i + chunk_length]
                parca_adi = os.path.join(
                    self.config.temp_dir,
                    f"parca_{i//chunk_length}.wav"
                )
                parca.export(parca_adi, format="wav")
                parcalar.append(parca_adi)
            
            return parcalar
            
        except Exception as e:
            print(f"Ses parçalama hatası: {e}")
            return []
    
    def _transcribe_with_whisper(self, file_path):
        """Whisper modelini kullanarak ses dosyasını metne dönüştürür - lazy loading uygulanmış"""
        try:
            # Whisper mevcut değilse çalışmaz
            if not WHISPER_AVAILABLE:
                print("Whisper modülü bulunamadığı için bu fonksiyon kullanılamaz.")
                return None
                
            # Lazy loading - Modeli yalnızca ilk kullanımda yükle 
            if not hasattr(self, 'whisper_model') or self.whisper_model is None:
                print("Whisper modeli yükleniyor... (ilk kullanım)")
                # Modelin kaydedilip kaydedilmediğini kontrol et
                model_size = "base"  # Hız ve bellek dengesini sağlar
                whisper_cache_dir = os.path.join(self.config.base_dir, "models", "whisper")
                os.makedirs(whisper_cache_dir, exist_ok=True)
                
                try:
                    # Özel önbellek dizini ile modeli yükle
                    self.whisper_model = whisper.load_model(model_size, download_root=whisper_cache_dir)
                    print("Whisper modeli yüklendi")
                except Exception as e:
                    print(f"Whisper modeli yüklenirken hata: {e}")
                    # Hata durumunda varsayılan konumdan yüklemeyi dene
                    self.whisper_model = whisper.load_model(model_size)
                    print("Whisper modeli varsayılan konumdan yüklendi")
            
            # Ses dosyasını tanı
            lang_code = self.config.get_language_code().split('-')[0]  # tr-TR -> tr
            
            # Daha iyi performans için CPU sabit özellikleri belirle
            # fp16 kullanmama ve optimize edilmiş düşük kaynak kullanımı
            result = self.whisper_model.transcribe(
                file_path, 
                language=lang_code,
                fp16=False,     # CPU'da daha stabil çalışır
                temperature=0,  # Deterministik çıktı
                best_of=1,      # Daha hızlı çalışır
                beam_size=1     # Daha az bellek kullanımı
            )
            
            return result["text"]
            
        except Exception as e:
            print(f"Whisper ile ses tanıma hatası: {e}")
            return None
    
    def _transcribe_with_google(self, file_path):
        """Google Speech API ile ses tanıma"""
        try:
            # Tanıma işlemi için ayarlar
            self.recognizer.energy_threshold = 300  # Daha düşük değer = daha hassas
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8  # Konuşma arasındaki duraksamalar için tolerans
            self.recognizer.phrase_threshold = 0.3  # Daha düşük değer = daha uzun cümleler
            
            # Dosyayı yükle ve işle
            with sr.AudioFile(file_path) as source:
                # Gürültü düzeyini ayarla
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Ses verisini kaydet
                audio_data = self.recognizer.record(source)
                
                # Farklı dil kodları deneme listesi oluştur
                main_lang_code = self.config.get_language_code()
                lang_codes = [main_lang_code]
                
                # Türkçe için alternatif dil kodları
                if main_lang_code.startswith("tr"):
                    lang_codes.extend(["tr", "tr-TR"])
                # İngilizce için alternatif dil kodları
                elif main_lang_code.startswith("en"):
                    lang_codes.extend(["en", "en-US", "en-GB"])
                
                # Her dil kodu için dene
                for lang_code in lang_codes:
                    try:
                        text = self.recognizer.recognize_google(
                            audio_data,
                            language=lang_code
                        )
                        print(f"Tanıma başarılı (dil: {lang_code}): {text}")
                        return text
                    except sr.UnknownValueError:
                        print(f"{lang_code} ile ses tanınamadı, alternatif deneniyor...")
                        continue
                    except sr.RequestError as e:
                        print(f"Google Speech Recognition servis hatası ({lang_code}): {e}")
                        break
                
                # Tüm dil kodları denendi ama sonuç alınamadı
                print("Hiçbir dil kodu ile ses tanınamadı")
                return None
                
        except sr.UnknownValueError:
            print("Google Speech Recognition ses tanıyamadı")
            return None
        except sr.RequestError as e:
            print(f"Google Speech Recognition servis hatası: {e}")
            return None
        except Exception as e:
            print(f"Google Speech Recognition hatası: {e}")
            return None
    
    def process_last_recording(self):
        """Son kaydedilen ses dosyasını işler ve metne dönüştürür"""
        try:
            if not self.temp_file_path or not os.path.exists(self.temp_file_path):
                raise Exception("İşlenecek ses dosyası bulunamadı!")
            
            # Ses dosyasını işle
            text = self.process_audio_file(self.temp_file_path)
            if not text:
                raise Exception("Ses dosyası metne dönüştürülemedi!")
                
            return text
            
        except Exception as e:
            print(f"Son kayıt işlenirken hata: {e}")
            return None
        
    def cleanup_temp_files(self, older_than_hours=24):
        """Belirli bir süreden daha eski geçici dosyaları temizler"""
        try:
            import time
            from datetime import datetime, timedelta
            
            # Şu andan belirtilen saat kadar öncesini hesapla
            cutoff_time = time.time() - (older_than_hours * 3600)
            temp_dir = self.config.temp_dir
            
            # Temp dizinini kontrol et
            if not os.path.exists(temp_dir):
                return
                
            print(f"{older_than_hours} saatten eski geçici dosyalar temizleniyor...")
            deleted_count = 0
            
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                
                # Sadece dosyaları kontrol et
                if os.path.isfile(file_path):
                    # Dosya oluşturma zamanını kontrol et
                    file_time = os.path.getctime(file_path)
                    if file_time < cutoff_time:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except Exception as e:
                            print(f"Dosya silinirken hata: {e}")
            
            print(f"{deleted_count} geçici dosya temizlendi.")
            
        except Exception as e:
            print(f"Geçici dosyalar temizlenirken hata: {e}")