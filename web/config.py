import os
import secrets

class Config:
    """Temel konfigürasyon sınıfı"""
    
    # Uygulama ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'mp3', 'wav', 'mp4'}
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB
    
    # Veritabanı ayarları
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # E-posta ayarları
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@raporcu.com')
    
    # Ödeme sistemi ayarları
    IYZICO_API_KEY = os.environ.get('IYZICO_API_KEY')
    IYZICO_SECRET_KEY = os.environ.get('IYZICO_SECRET_KEY')
    IYZICO_BASE_URL = os.environ.get('IYZICO_BASE_URL', 'https://sandbox-api.iyzipay.com')
    
    # Admin panel ayarları
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@raporcu.com')
    
    # Başlatma metodu
    @staticmethod
    def init_app(app):
        """Uygulama konfigürasyonu başlatma"""
        # Yükleme dizinini oluştur
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class DevelopmentConfig(Config):
    """Geliştirme ortamı konfigürasyonu"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raporcu_dev.db')


class TestingConfig(Config):
    """Test ortamı konfigürasyonu"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raporcu_test.db')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Üretim ortamı konfigürasyonu"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost/raporcu'
    
    @classmethod
    def init_app(cls, app):
        """Üretim ortamı için ek ayarlar"""
        Config.init_app(app)
        
        # Log ayarları
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Dosya günlükleyici
        file_handler = RotatingFileHandler('raporcu.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Raporcu web uygulaması başlatıldı')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
