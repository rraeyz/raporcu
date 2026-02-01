import tkinter as tk
import customtkinter as ctk

class ProgressIndicator(ctk.CTkFrame):
    """Gelişmiş ilerleme göstergesi bileşeni"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Varsayılan değerler
        self.current_step = 0
        self.total_steps = 100
        self.status_text = "Hazırlanıyor..."
        self.is_indeterminate = False
        self.is_running = False
        self.is_error = False
        self._animation_step = 0
        self._after_id = None
        
        # Grid yapısı
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Durum metni
        self.grid_rowconfigure(1, weight=0)  # İlerleme çubuğu
        self.grid_rowconfigure(2, weight=0)  # Adım göstergesi (isteğe bağlı)
        
        # Durum metni
        self.status_label = ctk.CTkLabel(
            self,
            text=self.status_text,
            font=("Arial", 12)
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        
        # İlerleme çubuğu
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.progress_bar.set(0)
        
        # Adım göstergesi (isteğe bağlı gösterilir)
        self.step_label = ctk.CTkLabel(
            self,
            text=f"Adım {self.current_step}/{self.total_steps}",
            font=("Arial", 10)
        )
        self.step_label.grid(row=2, column=0, sticky="e", padx=5, pady=(0, 5))
        self.step_label.grid_remove()  # Başlangıçta gizli
    
    def set_total_steps(self, total):
        """Toplam adım sayısını ayarla"""
        self.total_steps = max(1, total)
        self.update_step_label()
    
    def set_current_step(self, step):
        """Mevcut adımı ayarla"""
        self.current_step = min(max(0, step), self.total_steps)
        self.progress_bar.set(self.current_step / self.total_steps)
        self.update_step_label()
        
        # Adım göstergesini görünür yap
        if not self.is_indeterminate and self.total_steps > 1:
            self.step_label.grid()
    
    def set_status(self, text):
        """Durum metnini güncelle"""
        self.status_text = text
        self.status_label.configure(text=text)
    
    def update_step_label(self):
        """Adım göstergesini güncelle"""
        self.step_label.configure(text=f"Adım {self.current_step}/{self.total_steps}")
    
    def start_indeterminate(self):
        """Belirsiz ilerleme animasyonunu başlat"""
        self.is_indeterminate = True
        self.is_running = True
        self.is_error = False
        self._animation_step = 0
        self.step_label.grid_remove()  # Adım göstergesini gizle
        
        # Mevcut animasyon varsa iptal et
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
            
        self._animate_indeterminate()
    
    def _animate_indeterminate(self):
        """Belirsiz ilerleme animasyonunu güncelle"""
        if not self.is_running:
            return
            
        # Animasyon adımını artır (0-100 arası)
        self._animation_step = (self._animation_step + 3) % 200
        
        # 0-100 arası yükselir, 100-200 arası düşer
        if self._animation_step <= 100:
            value = self._animation_step / 100
        else:
            value = 2 - (self._animation_step / 100)
            
        try:
            self.progress_bar.set(value)
            # Animasyonu devam ettir - try bloğu içinde güvenli şekilde zamanla
            self._after_id = self.after(30, self._animate_indeterminate)
        except Exception as e:
            print(f"İlerleme animasyonu hatası: {e}")
            self._after_id = None
            
    def stop(self):
        """İlerleme animasyonunu durdur"""
        self.is_running = False
        
        # Mevcut animasyonu iptal et
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
    
    def reset(self):
        """İlerleme göstergesini sıfırla"""
        self.stop()
        self.current_step = 0
        self.is_error = False
        self.progress_bar.set(0)
        self.set_status("Hazırlanıyor...")
        self.step_label.grid_remove()
    
    def set_error(self, error_text="Hata oluştu!"):
        """Hata durumunu göster"""
        self.stop()
        self.is_error = True
        self.set_status(error_text)
        # Hata durumunda çubuğu kırmızı yapabiliriz (CustomTkinter'da destekleniyorsa)
        self.progress_bar.configure(progress_color="red")
    
    def set_success(self, success_text="Tamamlandı!"):
        """Başarı durumunu göster"""
        self.stop()
        self.is_error = False
        self.set_status(success_text)
        # Başarı durumunda çubuğu yeşil yapabiliriz
        self.progress_bar.configure(progress_color="green")
        # Çubuğu tamamen doldur
        self.progress_bar.set(1.0)
        
    def start_determinate(self, steps=None):
        """Belirli adımlı ilerleme modunu başlat"""
        self.stop()  # Önceki animasyonu durdur
        
        if steps is not None:
            self.set_total_steps(steps)
            
        self.is_indeterminate = False
        self.is_running = True
        self.is_error = False
        self.current_step = 0
        self.progress_bar.set(0)
        
        # İlerleme çubuğunu normal renk yap
        self.progress_bar.configure(progress_color=None)  # Varsayılan renk
        
        # Adım göstergesini göster
        if self.total_steps > 1:
            self.step_label.grid()
            
        return self
        self.is_error = False
        self.set_status(success_text)
        self.progress_bar.set(1)  # Tam dolu göster
        # Başarı durumunda çubuğu yeşil yapabiliriz
        self.progress_bar.configure(progress_color="green")
