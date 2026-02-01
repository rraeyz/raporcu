from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import time
from flask import current_app

from web import db, login_manager

class Role(db.Model):
    """Kullanıcı rolleri tablosu"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    """Kullanıcılar tablosu"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_active = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Kullanıcı profili
    profile_image = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    bio = db.Column(db.Text)
    
    # Abonelik ilişkisi
    subscription = db.relationship('Subscription', backref='user', uselist=False)
    
    # İlişkiler
    files = db.relationship('UserFile', backref='user', lazy='dynamic')
    reports = db.relationship('Report', backref='user', lazy='dynamic')
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    
    @property
    def password(self):
        """Şifre özelliği - salt okunur"""
        raise AttributeError('Şifre salt okunurdur.')
    
    @password.setter
    def password(self, password):
        """Şifre ayarlama - hash oluşturur"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Şifre doğrulama"""
        return check_password_hash(self.password_hash, password)
    
    def generate_confirmation_token(self, expiration=3600):
        """E-posta onay token'ı oluşturur"""
        payload = {
            'confirm': self.id,
            'exp': time.time() + expiration
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    def confirm_email(self, token):
        """E-posta onay token'ını doğrular"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
        except:
            return False
        
        if payload.get('confirm') != self.id:
            return False
        
        self.email_confirmed = True
        db.session.add(self)
        return True
    
    def generate_reset_token(self, expiration=3600):
        """Şifre sıfırlama token'ı oluşturur"""
        payload = {
            'reset': self.id,
            'exp': time.time() + expiration
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def reset_password(token, new_password):
        """Şifre sıfırlama token'ını doğrular ve şifreyi değiştirir"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
        except:
            return False
        
        user = User.query.get(payload.get('reset'))
        if user is None:
            return False
        
        user.password = new_password
        db.session.add(user)
        return True
    
    def get_subscription_status(self):
        """Kullanıcının abonelik durumunu döndürür"""
        if not self.subscription:
            return "inactive"
        
        if self.subscription.is_active and self.subscription.end_date > datetime.utcnow():
            return "active"
        
        return "expired"
    
    def can_use_service(self):
        """Kullanıcının hizmeti kullanıp kullanamayacağını kontrol eder"""
        # Admin her zaman kullanabilir
        if self.role.name == 'Admin':
            return True
            
        # Aktif abonelik kontrolü
        if self.get_subscription_status() == "active":
            # Kullanım limiti kontrolü
            if self.subscription.plan.type == 'unlimited':
                return True
            
            # Aylık/haftalık kullanım kontrolü
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_reports = self.reports.filter(Report.created_at >= month_start).count()
            
            return month_reports < self.subscription.plan.monthly_limit
        
        return False
    
    def __repr__(self):
        return f'<User {self.email}>'


class Subscription(db.Model):
    """Kullanıcı abonelikleri tablosu"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    auto_renew = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    plan = db.relationship('Plan', backref='subscriptions')
    
    def __repr__(self):
        return f'<Subscription {self.id}>'


class Plan(db.Model):
    """Abonelik planları tablosu"""
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    currency = db.Column(db.String(3), default='TRY')
    duration_days = db.Column(db.Integer)  # Abonelik süresi (gün)
    type = db.Column(db.String(20))  # weekly, monthly, yearly, unlimited
    monthly_limit = db.Column(db.Integer, default=0)  # 0 = unlimited
    features = db.Column(db.Text)  # JSON formatında özellikler
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Plan {self.name}>'


class Payment(db.Model):
    """Ödeme kayıtları tablosu"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'))
    amount = db.Column(db.Float)
    currency = db.Column(db.String(3), default='TRY')
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(255))
    status = db.Column(db.String(20))  # pending, completed, failed, refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    plan = db.relationship('Plan')
    
    def __repr__(self):
        return f'<Payment {self.id}>'


@login_manager.user_loader
def load_user(user_id):
    """Kullanıcı yükleyici"""
    return User.query.get(int(user_id))
