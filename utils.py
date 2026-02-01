import os
import tkinter as tk
from tkinter import messagebox
import threading
import time

def center_window(window):
    """
    Pencereyi ekranın ortasına konumlandırır
    Not: Eğer kayıtlı pencere konumu varsa bu fonksiyon çağrılmaz
    """
    # Ekranın genişliğini ve yüksekliğini al
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Pencere genişliğini ve yüksekliğini al
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    
    # Pencere boyutları çok küçükse, update etmek gerekir
    if window_width < 100 or window_height < 100:
        window.update_idletasks()  # Pencere boyutlarını güncelle
        window_width = window.winfo_width()
        window_height = window.winfo_height()
    
    # Merkez konumu hesapla
    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))
    
    # Ekranın dışına taşmadığından emin ol
    if center_x < 0:
        center_x = 0
    if center_y < 0:
        center_y = 0
    
    # Pencereyi konumlandır
    window.geometry(f"+{center_x}+{center_y}")

def show_progress_dialog(parent, title, message, task_func, on_complete=None, on_error=None):
    """İşlem sırasında ilerleme penceresi gösterir"""
    progress_window = tk.Toplevel(parent)
    progress_window.title(title)
    progress_window.geometry("300x150")
    progress_window.resizable(False, False)
    
    # Modal yapma
    progress_window.grab_set()
    progress_window.transient(parent)
    
    # Mesaj
    message_label = tk.Label(progress_window, text=message, wraplength=280)
    message_label.pack(pady=(20, 10))
    
    # İlerleme çubuğu
    progress = tk.ttk.Progressbar(progress_window, mode="indeterminate", length=280)
    progress.pack(pady=10)
    progress.start()
    
    # İlerleme penceresi kapatılmasın
    def disable_close():
        pass
    
    progress_window.protocol("WM_DELETE_WINDOW", disable_close)
    
    # Görevi arka planda çalıştır
    def run_task():
        try:
            result = task_func()
            
            # Ana thread'de tamamlama işlemi
            parent.after(0, lambda: complete_task(result))
        except Exception as e:
            # Ana thread'de hata işleme
            parent.after(0, lambda: handle_error(e))
    
    def complete_task(result):
        progress.stop()
        progress_window.destroy()
        
        if on_complete:
            on_complete(result)
    
    def handle_error(error):
        progress.stop()
        progress_window.destroy()
        
        if on_error:
            on_error(error)
        else:
            messagebox.showerror("Hata", f"İşlem sırasında bir hata oluştu: {str(error)}")
    
    # Arka plan thread'i başlat
    thread = threading.Thread(target=run_task, daemon=True)
    thread.start()
    
    # Pencereyi ortala
    center_window(progress_window)

def create_tooltip(widget, text):
    """Widget için ipucu oluşturur"""
    tooltip = None
    
    def enter(event):
        nonlocal tooltip
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Tooltip penceresi oluştur
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", "9", "normal"), padx=5, pady=2)
        label.pack()
    
    def leave(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None
    
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

def cleanup_temp_folder(temp_dir):
    """Temp klasöründeki tüm dosyaları siler"""
    try:
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                import shutil
                shutil.rmtree(item_path)
    except Exception as e:
        print(f"Temp klasörü temizlenirken hata: {e}")
