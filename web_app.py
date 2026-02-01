from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for, session
import os
import uuid
import json
from werkzeug.utils import secure_filename
import tempfile
import shutil
from datetime import datetime

# Mevcut uygulamanın sınıflarını içe aktar
from config import Config
from file_processor import FileProcessor
from ai_service import AIService

app = Flask(__name__, 
           template_folder='templates_web',
           static_folder='static')
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'temp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB maksimum dosya boyutu

# Uygulama servisleri
config = Config(async_load=False)  # Senkron modda yükle
file_processor = FileProcessor()
ai_service = AIService(config)

# Geçici dosyaları saklayacak sözlük
user_files = {}

def get_user_id():
    """Kullanıcı oturumu için benzersiz ID döndürür"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

def get_user_temp_dir():
    """Kullanıcıya özel geçici dizin yolu döndürür"""
    user_id = get_user_id()
    temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def allowed_file(filename):
    """Dosya uzantısının kabul edilebilir olup olmadığını kontrol eder"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'docx', 'mp3', 'wav', 'mp4'}

@app.route('/')
def index():
    """Ana sayfa"""
    # Şablonları al
    templates = config.get_template_names()
    # AI modelleri
    ai_models = list(config.available_models.keys())
    
    return render_template('index.html', 
                          templates=templates, 
                          ai_models=ai_models,
                          active_template=config.active_template)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Dosya yükleme işlemi"""
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    if file and allowed_file(file.filename):
        # Güvenli dosya adı oluştur
        filename = secure_filename(file.filename)
        
        # Kullanıcıya özel temp dizini
        user_temp_dir = get_user_temp_dir()
        
        # Dosyayı kaydet
        file_path = os.path.join(user_temp_dir, filename)
        file.save(file_path)
        
        # Dosya bilgilerini sakla
        user_id = get_user_id()
        if user_id not in user_files:
            user_files[user_id] = []
        
        user_files[user_id].append({
            'path': file_path,
            'name': filename,
            'type': filename.rsplit('.', 1)[1].lower(),
            'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Dosya başarıyla yüklendi'
        })
    
    return jsonify({'error': 'İzin verilmeyen dosya türü'}), 400

@app.route('/process', methods=['POST'])
def process_file():
    """Dosya işleme ve rapor oluşturma"""
    try:
        user_id = get_user_id()
        
        if user_id not in user_files or not user_files[user_id]:
            return jsonify({'error': 'İşlenecek dosya bulunamadı'}), 400
        
        # Form verilerini al
        file_index = int(request.form.get('file_index', 0))
        ai_model = request.form.get('ai_model', config.ai_model)
        template_id = request.form.get('template_id', config.active_template)
        
        # Şablon değiştir
        config.set_active_template(template_id)
        
        # Dosya bilgilerini al
        file_info = user_files[user_id][file_index]
        file_path = file_info['path']
        
        # Dosya türüne göre işlem yap
        if file_info['type'] in ['txt', 'pdf', 'docx']:
            # Metin çıkarma
            text_content = file_processor.extract_text_from_file(file_path)
            
            # AI işleme (örnek olarak)
            if text_content:
                ai_response = ai_service.process_text(text_content, ai_model)
            else:
                return jsonify({'error': 'Dosyadan metin çıkarılamadı'}), 500
                
        elif file_info['type'] in ['mp3', 'wav', 'mp4']:
            # Ses dosyası işleme burada eklenecek
            return jsonify({'error': 'Ses dosyası işleme şu anda desteklenmiyor'}), 501
        else:
            return jsonify({'error': 'Desteklenmeyen dosya türü'}), 400
        
        # Sonucu kaydet
        output_filename = f"rapor_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
        output_path = os.path.join(get_user_temp_dir(), output_filename)
        
        # DOCX olarak kaydet
        success = file_processor.save_as_docx(ai_response, output_path, config_instance=config)
        
        if success:
            # Sonuç dosyasını da dosya listesine ekle
            user_files[user_id].append({
                'path': output_path,
                'name': output_filename,
                'type': 'docx',
                'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'is_result': True
            })
            
            return jsonify({
                'success': True,
                'file_index': len(user_files[user_id]) - 1,
                'filename': output_filename,
                'message': 'Rapor başarıyla oluşturuldu'
            })
        else:
            return jsonify({'error': 'Rapor oluşturulurken hata oluştu'}), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'İşlem sırasında hata: {str(e)}'}), 500

@app.route('/download/<int:file_index>')
def download_file(file_index):
    """Dosya indirme"""
    user_id = get_user_id()
    
    if user_id not in user_files or len(user_files[user_id]) <= file_index:
        return jsonify({'error': 'Dosya bulunamadı'}), 404
    
    file_info = user_files[user_id][file_index]
    
    return send_file(file_info['path'], 
                    download_name=file_info['name'],
                    as_attachment=True)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Ayarlar sayfası"""
    if request.method == 'POST':
        # Ayarları güncelle
        template_id = request.form.get('template')
        ai_model = request.form.get('ai_model')
        
        if template_id:
            config.set_active_template(template_id)
        
        if ai_model:
            config.ai_model = ai_model
            # Ayarları kaydet
            settings = config.load_settings_from_file()
            settings['ai_model'] = ai_model
            config.save_settings_to_file(settings)
        
        return redirect(url_for('settings'))
    
    # Şablonları ve modelleri al
    templates = config.get_template_names()
    ai_models = list(config.available_models.keys())
    
    return render_template('settings.html', 
                          templates=templates,
                          ai_models=ai_models,
                          active_template=config.active_template,
                          active_model=config.ai_model)

@app.route('/clear')
def clear_files():
    """Kullanıcının dosyalarını temizle"""
    user_id = get_user_id()
    
    if user_id in user_files:
        # Dosyaları sil
        for file_info in user_files[user_id]:
            if os.path.exists(file_info['path']):
                os.remove(file_info['path'])
        
        # Kullanıcı dizinini sil
        user_temp_dir = get_user_temp_dir()
        if os.path.exists(user_temp_dir):
            shutil.rmtree(user_temp_dir)
        
        # Listeyi temizle
        user_files[user_id] = []
    
    return redirect(url_for('index'))

@app.route('/templates')
def templates_list():
    """Şablon listesi sayfası"""
    templates = config.templates
    return render_template('templates.html', templates=templates)

@app.route('/templates/<template_id>')
def template_detail(template_id):
    """Şablon detay sayfası"""
    template = config.templates.get(template_id)
    if not template:
        return redirect(url_for('templates_list'))
    
    return render_template('template_detail.html', 
                          template_id=template_id,
                          template=template)

@app.route('/api/change_template', methods=['POST'])
def change_template():
    """API - Şablon değiştirme"""
    data = request.get_json()
    template_id = data.get('template_id')
    
    if not template_id:
        return jsonify({'error': 'Şablon ID\'si belirtilmedi'}), 400
    
    success = config.set_active_template(template_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Şablon değiştirildi'})
    else:
        return jsonify({'error': 'Şablon değiştirilemedi'}), 400

@app.route('/api/files')
def api_files():
    """API - Kullanıcının dosyalarını listele"""
    user_id = get_user_id()
    
    if user_id not in user_files:
        return jsonify({"files": []})
    
    return jsonify({"files": user_files[user_id]})

@app.route('/api/settings')
def api_settings():
    """API - Ayarları al"""
    settings = {
        'active_template': config.active_template,
        'ai_model': config.ai_model,
        'language': config.language
    }
    return jsonify(settings)

if __name__ == '__main__':
    # Gerekli klasörleri oluştur
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Debug modda çalıştır
    app.run(debug=True, host='0.0.0.0', port=5000)
