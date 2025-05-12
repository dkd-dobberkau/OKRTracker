from flask import Blueprint, render_template, redirect, url_for
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