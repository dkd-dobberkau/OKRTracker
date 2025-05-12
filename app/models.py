from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    objectives = db.relationship('Objective', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_complete = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    key_results = db.relationship('KeyResult', backref='objective', lazy='dynamic', cascade='all, delete-orphan')
    
    def progress(self):
        key_results = self.key_results.all()
        if not key_results:
            return 0
        
        total_progress = sum(kr.progress for kr in key_results)
        return total_progress / len(key_results)
    
    def __repr__(self):
        return f'<Objective {self.title}>'

class KeyResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    target_value = db.Column(db.Float)
    current_value = db.Column(db.Float, default=0)
    unit = db.Column(db.String(32))
    objective_id = db.Column(db.Integer, db.ForeignKey('objective.id'))
    updates = db.relationship('KeyResultUpdate', backref='key_result', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def progress(self):
        if self.target_value == 0:
            return 0
        progress = (self.current_value / self.target_value) * 100
        return min(100, max(0, progress))
    
    def __repr__(self):
        return f'<KeyResult {self.title}>'

class KeyResultUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    key_result_id = db.Column(db.Integer, db.ForeignKey('key_result.id'))
    
    def __repr__(self):
        return f'<Update {self.value} at {self.timestamp}>'