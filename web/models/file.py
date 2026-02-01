from datetime import datetime
import os
import uuid

from web import db

class UserFile(db.Model):
    """Kullanıcı dosyaları tablosu"""
    __tablename__ = 'user_files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    original_filename = db.Column(db.String(255))
    stored_filename = db.Column(db.String(255), unique=True)
    file_type = db.Column(db.String(20))  # txt, pdf, docx, mp3, wav, mp4
    file_size = db.Column(db.Integer)  # Byte cinsinden
    file_path = db.Column(db.String(255))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    reports = db.relationship('Report', backref='source_file', lazy='dynamic')
    
    @staticmethod
    def generate_unique_filename(original_filename):
        """Benzersiz bir dosya adı oluşturur"""
        ext = os.path.splitext(original_filename)[1]
        new_filename = f"{uuid.uuid4().hex}{ext}"
        return new_filename
    
    def __repr__(self):
        return f'<UserFile {self.original_filename}>'


class Report(db.Model):
    """Raporlar tablosu"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('user_files.id'))
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    template_id = db.Column(db.String(100))
    ai_model = db.Column(db.String(100))
    status = db.Column(db.String(20))  # processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Çıktı dosyaları
    output_docx = db.Column(db.String(255))
    output_pdf = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Report {self.title}>'


class Template(db.Model):
    """Şablonlar tablosu"""
    __tablename__ = 'templates'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    settings = db.Column(db.Text)  # JSON formatında ayarlar
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Template {self.name}>'


class ContactMessage(db.Model):
    """İletişim mesajları tablosu"""
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactMessage {self.subject}>'
