import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

# Ana projenin bulunduğu dizini sys.path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Veritabanı bağlantısı
db = SQLAlchemy()
migrate = Migrate()

# Login yönetimi
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bu sayfaya erişmek için lütfen giriş yapın.'
login_manager.login_message_category = 'warning'

# E-posta gönderimi
mail = Mail()

# CSRF koruması
csrf = CSRFProtect()

def create_app(config_name='development'):
    """Uygulama fabrika fonksiyonu"""
    
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Konfigürasyon
    if config_name == 'production':
        app.config.from_object('web.config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('web.config.TestingConfig')
    else:
        app.config.from_object('web.config.DevelopmentConfig')
    
    # Eklentileri başlat
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    CORS(app)
    
    # Modülleri kaydet
    from web.views.main import main as main_blueprint
    from web.views.auth import auth as auth_blueprint
    from web.views.user import user as user_blueprint
    from web.views.api import api as api_blueprint
    from web.views.payment import payment as payment_blueprint
    from web.views.contact import contact as contact_blueprint
    from web.admin.views import admin as admin_blueprint
    
    # Modülleri uygulama ile ilişkilendir
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(user_blueprint, url_prefix='/dashboard')
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(payment_blueprint, url_prefix='/payment')
    app.register_blueprint(contact_blueprint, url_prefix='/contact')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    # Hata sayfaları
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    # Veritabanı tablolarını oluştur
    with app.app_context():
        db.create_all()
        
        # Admin kullanıcı kontrol et ve oluştur
        from web.models.user import User, Role
        from werkzeug.security import generate_password_hash
        
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin', description='Tam yetkili yönetici')
            db.session.add(admin_role)
        
        user_role = Role.query.filter_by(name='User').first()
        if not user_role:
            user_role = Role(name='User', description='Standart kullanıcı')
            db.session.add(user_role)
            
        admin_user = User.query.filter_by(email='admin@raporcu.com').first()
        if not admin_user:
            admin_user = User(
                name='Admin',
                email='admin@raporcu.com',
                password_hash=generate_password_hash('admin123'),
                role=admin_role,
                is_active=True,
                email_confirmed=True
            )
            db.session.add(admin_user)
            
        db.session.commit()
    
    return app

# Flask uygulamasını başlat
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
