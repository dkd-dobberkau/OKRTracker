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