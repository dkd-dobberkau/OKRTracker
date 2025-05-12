# Flask OKR Web Application
# Directory Structure:
# - app.py (main application file)
# - config.py (configuration settings)
# - models.py (database models)
# - routes/ (blueprint routes)
#   - auth.py (authentication routes)
#   - objectives.py (objective routes)
#   - keyresults.py (key results routes)
# - templates/ (HTML templates)
# - static/ (CSS, JS, images)
# - requirements.txt (dependencies)

# requirements.txt
"""
flask==3.1.2
flask-sqlalchemy==3.1.1
flask-login==0.6.2
flask-wtf==1.2.1
werkzeug==3.0.1
email-validator==2.0.0
flask-migrate==4.0.5
python-dotenv==1.0.0
"""

# config.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///okr.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
"""

# models.py
"""
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
"""

# routes/auth.py
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.models import User, db
from app.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)
"""

# routes/objectives.py
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import Objective, KeyResult, db
from app.forms import ObjectiveForm, KeyResultForm
from datetime import datetime

objectives_bp = Blueprint('objectives', __name__)

@objectives_bp.route('/objectives')
@login_required
def list_objectives():
    objectives = Objective.query.filter_by(user_id=current_user.id).all()
    return render_template('objectives/list.html', objectives=objectives)

@objectives_bp.route('/objectives/new', methods=['GET', 'POST'])
@login_required
def new_objective():
    form = ObjectiveForm()
    if form.validate_on_submit():
        objective = Objective(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            user_id=current_user.id
        )
        db.session.add(objective)
        db.session.commit()
        flash('Objective created successfully.')
        return redirect(url_for('objectives.view_objective', id=objective.id))
    
    return render_template('objectives/new.html', form=form)

@objectives_bp.route('/objectives/<int:id>')
@login_required
def view_objective(id):
    objective = Objective.query.get_or_404(id)
    if objective.user_id != current_user.id:
        abort(403)
    return render_template('objectives/view.html', objective=objective)

@objectives_bp.route('/objectives/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_objective(id):
    objective = Objective.query.get_or_404(id)
    if objective.user_id != current_user.id:
        abort(403)
    
    form = ObjectiveForm(obj=objective)
    if form.validate_on_submit():
        objective.title = form.title.data
        objective.description = form.description.data
        objective.start_date = form.start_date.data
        objective.end_date = form.end_date.data
        db.session.commit()
        flash('Objective updated successfully.')
        return redirect(url_for('objectives.view_objective', id=objective.id))
    
    return render_template('objectives/edit.html', form=form, objective=objective)

@objectives_bp.route('/objectives/<int:id>/delete', methods=['POST'])
@login_required
def delete_objective(id):
    objective = Objective.query.get_or_404(id)
    if objective.user_id != current_user.id:
        abort(403)
    
    db.session.delete(objective)
    db.session.commit()
    flash('Objective deleted successfully.')
    return redirect(url_for('objectives.list_objectives'))
"""

# routes/keyresults.py
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import Objective, KeyResult, KeyResultUpdate, db
from app.forms import KeyResultForm, KeyResultUpdateForm

keyresults_bp = Blueprint('keyresults', __name__)

@keyresults_bp.route('/objectives/<int:objective_id>/keyresults/new', methods=['GET', 'POST'])
@login_required
def new_key_result(objective_id):
    objective = Objective.query.get_or_404(objective_id)
    if objective.user_id != current_user.id:
        abort(403)
    
    form = KeyResultForm()
    if form.validate_on_submit():
        key_result = KeyResult(
            title=form.title.data,
            description=form.description.data,
            target_value=form.target_value.data,
            current_value=form.current_value.data,
            unit=form.unit.data,
            objective_id=objective.id
        )
        db.session.add(key_result)
        db.session.commit()
        flash('Key Result added successfully.')
        return redirect(url_for('objectives.view_objective', id=objective.id))
    
    return render_template('keyresults/new.html', form=form, objective=objective)

@keyresults_bp.route('/keyresults/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_key_result(id):
    key_result = KeyResult.query.get_or_404(id)
    objective = key_result.objective
    if objective.user_id != current_user.id:
        abort(403)
    
    form = KeyResultForm(obj=key_result)
    if form.validate_on_submit():
        key_result.title = form.title.data
        key_result.description = form.description.data
        key_result.target_value = form.target_value.data
        key_result.current_value = form.current_value.data
        key_result.unit = form.unit.data
        db.session.commit()
        flash('Key Result updated successfully.')
        return redirect(url_for('objectives.view_objective', id=objective.id))
    
    return render_template('keyresults/edit.html', form=form, key_result=key_result)

@keyresults_bp.route('/keyresults/<int:id>/delete', methods=['POST'])
@login_required
def delete_key_result(id):
    key_result = KeyResult.query.get_or_404(id)
    objective = key_result.objective
    if objective.user_id != current_user.id:
        abort(403)
    
    db.session.delete(key_result)
    db.session.commit()
    flash('Key Result deleted successfully.')
    return redirect(url_for('objectives.view_objective', id=objective.id))

@keyresults_bp.route('/keyresults/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_key_result(id):
    key_result = KeyResult.query.get_or_404(id)
    objective = key_result.objective
    if objective.user_id != current_user.id:
        abort(403)
    
    form = KeyResultUpdateForm()
    if form.validate_on_submit():
        update = KeyResultUpdate(
            value=form.value.data,
            comment=form.comment.data,
            key_result_id=key_result.id
        )
        key_result.current_value = form.value.data
        db.session.add(update)
        db.session.commit()
        flash('Key Result progress updated.')
        return redirect(url_for('objectives.view_objective', id=objective.id))
    
    form.value.data = key_result.current_value
    return render_template('keyresults/update.html', form=form, key_result=key_result)
"""

# routes/main.py
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Objective, KeyResult
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    objectives = Objective.query.filter_by(user_id=current_user.id).all()
    
    # Calculate overall progress
    total_progress = 0
    completed = 0
    
    if objectives:
        for obj in objectives:
            total_progress += obj.progress()
            if obj.is_complete:
                completed += 1
        
        overall_progress = total_progress / len(objectives)
    else:
        overall_progress = 0
    
    # Get upcoming objectives
    upcoming = Objective.query.filter_by(user_id=current_user.id)\
        .filter(Objective.end_date >= datetime.utcnow())\
        .filter(Objective.is_complete == False)\
        .order_by(Objective.end_date).limit(5).all()
    
    return render_template('dashboard.html', 
                          objectives=objectives, 
                          overall_progress=overall_progress,
                          completed=completed,
                          upcoming=upcoming)
"""

# forms.py
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, FloatField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ObjectiveForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Save')

class KeyResultForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    target_value = FloatField('Target Value', validators=[DataRequired()])
    current_value = FloatField('Current Value', default=0)
    unit = StringField('Unit (e.g., %, count)', validators=[DataRequired()])
    submit = SubmitField('Save')

class KeyResultUpdateForm(FlaskForm):
    value = FloatField('Current Value', validators=[DataRequired()])
    comment = TextAreaField('Comment')
    submit = SubmitField('Update Progress')
"""

# app.py (Main application file)
"""
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from models import db, User

# Import blueprints
from routes.auth import auth_bp
from routes.objectives import objectives_bp
from routes.keyresults import keyresults_bp
from routes.main import main_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Setup login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(objectives_bp)
    app.register_blueprint(keyresults_bp)
    app.register_blueprint(main_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Create all database tables
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
"""

# Template Examples (Basic HTML structure for key pages)

# templates/base.html
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}OKR Tracker{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('main.index') }}">OKR Tracker</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    {% if current_user.is_authenticated %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.dashboard') }}">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('objectives.list_objectives') }}">Objectives</a>
                    </li>
                    {% endif %}
                </ul>
                <ul class="navbar-nav ms-auto">
                    {% if current_user.is_authenticated %}
                    <li class="nav-item">
                        <span class="nav-link">{{ current_user.username }}</span>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                    </li>
                    {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.register') }}">Register</a>
                    </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <div class="row">
            <div class="col-md-12">
                {% for message in messages %}
                <div class="alert alert-info">{{ message }}</div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <footer class="mt-5 py-3 bg-light text-center">
        <div class="container">
            <p class="mb-0">OKR Tracker &copy; {{ now.year }}</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""

# templates/dashboard.html
"""
{% extends "base.html" %}

{% block title %}Dashboard - OKR Tracker{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1>Dashboard</h1>
        <p>Welcome, {{ current_user.username }}!</p>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <h5 class="card-title">Overall Progress</h5>
                <div class="progress mt-3">
                    <div class="progress-bar" role="progressbar" style="width: {{ overall_progress }}%;"
                        aria-valuenow="{{ overall_progress }}" aria-valuemin="0" aria-valuemax="100">
                        {{ overall_progress|round }}%
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <h5 class="card-title">Objectives</h5>
                <div class="display-4">{{ objectives|length }}</div>
                <p class="text-muted">Total Objectives</p>
            </div>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <h5 class="card-title">Completed</h5>
                <div class="display-4">{{ completed }}</div>
                <p class="text-muted">Completed Objectives</p>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Upcoming Objectives</h5>
                <a href="{{ url_for('objectives.new_objective') }}" class="btn btn-primary btn-sm">
                    Add New Objective
                </a>
            </div>
            <div class="card-body">
                {% if upcoming %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Due Date</th>
                                <th>Progress</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for objective in upcoming %}
                            <tr>
                                <td>{{ objective.title }}</td>
                                <td>{{ objective.end_date.strftime('%Y-%m-%d') }}</td>
                                <td>
                                    <div class="progress">
                                        <div class="progress-bar" role="progressbar" 
                                             style="width: {{ objective.progress()|round }}%;"
                                             aria-valuenow="{{ objective.progress()|round }}" 
                                             aria-valuemin="0" aria-valuemax="100">
                                            {{ objective.progress()|round }}%
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <a href="{{ url_for('objectives.view_objective', id=objective.id) }}" 
                                       class="btn btn-sm btn-outline-primary">View</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-center mt-3">No upcoming objectives. 
                    <a href="{{ url_for('objectives.new_objective') }}">Create your first objective</a>
                </p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# templates/objectives/view.html
"""
{% extends "base.html" %}

{% block title %}{{ objective.title }} - OKR Tracker{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="{{ url_for('main.dashboard') }}">Dashboard</a></li>
                <li class="breadcrumb-item"><a href="{{ url_for('objectives.list_objectives') }}">Objectives</a></li>
                <li class="breadcrumb-item active" aria-current="page">{{ objective.title }}</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h3 class="mb-0">{{ objective.title }}</h3>
                <div>
                    <a href="{{ url_for('objectives.edit_objective', id=objective.id) }}" 
                       class="btn btn-outline-primary btn-sm">Edit</a>
                    <a href="#" class="btn btn-outline-danger btn-sm" 
                       data-bs-toggle="modal" data-bs-target="#deleteModal">Delete</a>
                </div>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Description:</strong> {{ objective.description }}</p>
                        <p><strong>Start Date:</strong> {{ objective.start_date.strftime('%Y-%m-%d') }}</p>
                        <p><strong>End Date:</strong> {{ objective.end_date.strftime('%Y-%m-%d') }}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Progress:</strong></p>
                        <div class="progress mb-3">
                            <div class="progress-bar" role="progressbar" 
                                 style="width: {{ objective.progress()|round }}%;"
                                 aria-valuenow="{{ objective.progress()|round }}" 
                                 aria-valuemin="0" aria-valuemax="100">
                                {{ objective.progress()|round }}%
                            </div>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="completeCheckbox"
                                   {% if objective.is_complete %}checked{% endif %}
                                   data-objective-id="{{ objective.id }}">
                            <label class="form-check-label" for="completeCheckbox">
                                Mark as Complete
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h4 class="mb-0">Key Results</h4>
                <a href="{{ url_for('keyresults.new_key_result', objective_id=objective.id) }}" 
                   class="btn btn-primary btn-sm">Add Key Result</a>
            </div>
            <div class="card-body">
                {% if objective.key_results.count() > 0 %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Target</th>
                                <th>Current</th>
                                <th>Progress</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for kr in objective.key_results %}
                            <tr>
                                <td>{{ kr.title }}</td>
                                <td>{{ kr.target_value }} {{ kr.unit }}</td>
                                <td>{{ kr.current_value }} {{ kr.unit }}</td>
                                <td>
                                    <div class="progress">
                                        <div class="progress-bar" role="progressbar" 
                                             style="width: {{ kr.progress|round }}%;"
                                             aria-valuenow="{{ kr.progress|round }}" 
                                             aria-valuemin="0" aria-valuemax="100">
                                            {{ kr.progress|round }}%
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <a href="{{ url_for('keyresults.update_key_result', id=kr.id) }}" 
                                           class="btn btn-outline-primary">Update</a>
                                        <a href="{{ url_for('keyresults.edit_key_result', id=kr.id) }}" 
                                           class="btn btn-outline-secondary">Edit</a>
                                        <a href="#" class="btn btn-outline-danger"
                                           data-bs-toggle="modal" 
                                           data-bs-target="#deleteKRModal{{ kr.id }}">Delete</a>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-center mt-3">No key results yet. 
                   <a href="{{ url_for('keyresults.new_key_result', objective_id=objective.id) }}">
                      Add your first key result
                   </a>
                </p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Delete Objective Modal -->
<div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="deleteModalLabel">Confirm Delete</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                Are you sure you want to delete this objective? This action cannot be undone.
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <form action="{{ url_for('objectives.delete_objective', id=objective.id) }}" method="post">
                    <button type="submit" class="btn btn-danger">Delete</button>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Delete Key Result Modals -->
{% for kr in objective.key_results %}
<div class="modal fade" id="deleteKRModal{{ kr.id }}" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Confirm Delete</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                Are you sure you want to delete this key result? This action cannot be undone.
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <form action="{{ url_for('keyresults.delete_key_result', id=kr.id) }}" method="post">
                    <button type="submit" class="btn btn-danger">Delete</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endfor %}
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const completeCheckbox = document.getElementById('completeCheckbox');
    if (completeCheckbox) {
        completeCheckbox.addEventListener('change', function() {
            const objectiveId = this.dataset.objectiveId;
            const isComplete = this.checked;
            
            fetch(`/api/objectives/${objectiveId}/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ is_complete: isComplete })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Optionally show a notification
                    console.log('Objective updated successfully');
                }
            })
            .catch(error => {
                console.error('Error updating objective:', error);
                // Reset the checkbox to its previous state
                this.checked = !isComplete;
            });
        });
    }
});
</script>
{% endblock %}
"""

# static/css/style.css
"""
/* Custom styles for OKR Tracker */

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
}

.navbar-brand {
    font-weight: bold;
}

.card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    border: none;
    margin-bottom: 1.5rem;
}

.card-header {
    background-color: #fff;
    border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.progress {
    height: 1.2rem;
    font-size: 0.75rem;
    font-weight: bold;
    background-color: #e9ecef;
}

.progress-bar {
    background-color: #007bff;
}

.table th {
    border-top: none;
    background-color: #f8f9fa;
}

footer {
    color: #6c757d;
    font-size: 0.9rem;
}

.btn-primary {
    background-color: #3f51b5;
    border-color: #3f51b5;
}

.btn-primary:hover {
    background-color: #303f9f;
    border-color: #303f9f;
}

.btn-outline-primary {
    color: #3f51b5;
    border-color: #3f51b5;
}

.btn-outline-primary:hover {
    background-color: #3f51b5;
    border-color: #3f51b5;
}
"""

# static/js/main.js
"""
// Main JavaScript for OKR Tracker

// Set active nav item based on current page
document.addEventListener('DOMContentLoaded', function() {
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav a.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentLocation === linkPath || 
            (linkPath !== '/' && currentLocation.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Function to format dates
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Format all date elements
document.addEventListener('DOMContentLoaded', function() {
    const dateElements = document.querySelectorAll('.format-date');
    dateElements.forEach(element => {
        const originalDate = element.textContent.trim();
        if (originalDate) {
            element.textContent = formatDate(originalDate);
        }
    });
});
"""
