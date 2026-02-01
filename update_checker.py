"""
Otomatik Güncelleme Kontrolü
"""

import requests
import threading
from tkinter import messagebox
import webbrowser
from version import __version__, VERSION_CHECK_URL, GITHUB_RELEASES_URL


class UpdateChecker:
    """Uygulamanın güncellemelerini kontrol eder"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.current_version = __version__
        self.latest_version = None
        self.update_info = None
        
    def check_for_updates(self, show_if_current=False):
        """
        Güncellemeleri kontrol eder
        
        Args:
            show_if_current (bool): Güncel sürümdeyse de bildirim göster
        """
        def check():
            try:
                # GitHub'dan version.json al (timeout: 5 saniye)
                response = requests.get(VERSION_CHECK_URL, timeout=5)
                response.raise_for_status()
                
                self.update_info = response.json()
                self.latest_version = self.update_info.get('version', '0.0.0')
                
                # Versiyon karşılaştır
                if self._is_newer_version(self.latest_version, self.current_version):
                    self._show_update_dialog()
                elif show_if_current:
                    self._show_current_message()
                    
            except requests.exceptions.Timeout:
                if show_if_current:
                    messagebox.showwarning(
                        "Güncelleme Kontrolü",
                        "Güncelleme kontrolü zaman aşımına uğradı.\n"
                        "İnternet bağlantınızı kontrol edin."
                    )
            except requests.exceptions.RequestException as e:
                # Ağ hatası - sessizce geç (opsiyonel bildirimi gösterme)
                if show_if_current:
                    messagebox.showerror(
                        "Güncelleme Kontrolü",
                        f"Güncelleme kontrolü başarısız:\n{str(e)}"
                    )
            except Exception as e:
                if show_if_current:
                    messagebox.showerror(
                        "Güncelleme Kontrolü",
                        f"Beklenmeyen hata:\n{str(e)}"
                    )
        
        # Arka planda kontrol et (UI bloklamasın)
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
    
    def _is_newer_version(self, latest, current):
        """Versiyon numaralarını karşılaştırır (semantic versioning)"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Major, minor, patch karşılaştır
            for i in range(3):
                if latest_parts[i] > current_parts[i]:
                    return True
                elif latest_parts[i] < current_parts[i]:
                    return False
            
            return False  # Eşit
        except:
            return False
    
    def _show_update_dialog(self):
        """Yeni güncelleme bildirimi göster"""
        changes = self.update_info.get('changes', [])
        changes_text = '\n'.join([f"  • {change}" for change in changes])
        
        release_notes = self.update_info.get('release_notes', 'Yeni sürüm mevcut!')
        
        message = (
            f"🎉 Yeni Sürüm Mevcut!\n\n"
            f"Mevcut Sürüm: v{self.current_version}\n"
            f"Yeni Sürüm: v{self.latest_version}\n\n"
            f"📝 Yenilikler:\n{changes_text}\n\n"
            f"İndirmek ister misiniz?"
        )
        
        result = messagebox.askyesno(
            "Güncelleme Mevcut",
            message,
            icon='info'
        )
        
        if result:
            # Releases sayfasını aç
            webbrowser.open(GITHUB_RELEASES_URL)
    
    def _show_current_message(self):
        """Güncel sürüm mesajı"""
        messagebox.showinfo(
            "Güncelleme Kontrolü",
            f"✅ Güncel sürümü kullanıyorsunuz!\n\n"
            f"Mevcut Sürüm: v{self.current_version}"
        )
