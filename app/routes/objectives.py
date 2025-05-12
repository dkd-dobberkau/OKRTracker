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