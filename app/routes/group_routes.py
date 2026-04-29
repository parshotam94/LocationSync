from flask import Blueprint, render_template, request, redirect, session, url_for, flash
import random, string
from app.models.group_model import create_group, get_groups_for_user, get_group_by_code, add_member
from app.models.invitation_model import create_invitation, get_pending_invitations, update_invitation_status
from app.models.user_model import get_user_by_email
from app.utils.auth_utils import login_required

group_bp = Blueprint("group", __name__)

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@group_bp.route("/")
def index():
    if 'user_id' in session:
        return redirect(url_for('group.dashboard'))
    return redirect(url_for('auth.login'))

@group_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session['user_id']
    groups = get_groups_for_user(user_id)
    invites = get_pending_invitations(user_id)
    return render_template("dashboard.html", groups=groups, invites=invites)

@group_bp.route("/create_group", methods=["POST"])
@login_required
def create():
    name = request.form["name"]
    code = generate_code()
    create_group(name, code, session['user_id'])
    return redirect(f"/group/{code}")

@group_bp.route("/group/<code>")
@login_required
def group_page(code):
    group = get_group_by_code(code)
    if not group:
        flash("Group not found", "error")
        return redirect(url_for('group.dashboard'))
    
    # Check if user is a member
    groups = get_groups_for_user(session['user_id'])
    if not any(g['id'] == group['id'] for g in groups):
        flash("You are not a member of this group", "error")
        return redirect(url_for('group.dashboard'))
        
    return render_template("group.html", code=code, group_id=group['id'], user_id=session['user_id'], user_name=session['user_name'])

@group_bp.route("/invite", methods=["POST"])
@login_required
def invite():
    email = request.form.get("email")
    group_id = request.form.get("group_id")
    user = get_user_by_email(email)
    
    if user:
        create_invitation(group_id, session['user_id'], user['id'])
        flash(f"Invitation sent to {email}", "success")
    else:
        flash("User not found", "error")
        
    group_code = request.form.get("group_code")
    return redirect(f"/group/{group_code}")

@group_bp.route("/accept_invite/<int:invite_id>", methods=["POST"])
@login_required
def accept_invite(invite_id):
    invite = update_invitation_status(invite_id, 'accepted')
    if invite:
        add_member(invite['group_id'], session['user_id'])
        flash("Invitation accepted", "success")
    return redirect(url_for('group.dashboard'))