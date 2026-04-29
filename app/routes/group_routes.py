from flask import Blueprint, render_template, request, redirect, session, url_for, flash, jsonify
import random, string
from app.models.group_model import create_group, get_groups_for_user, get_group_by_code, add_member, remove_member
from app.models.invitation_model import create_invitation, get_pending_invitations, update_invitation_status
from app.models.ride_model import start_ride, end_ride, get_rides_for_user
from app.models.user_model import get_user_by_email
from app.utils.auth_utils import login_required
from app.services.gemini_service import get_eta

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
    rides = get_rides_for_user(user_id)
    return render_template("dashboard.html", groups=groups, invites=invites, rides=rides)

@group_bp.route("/create_group", methods=["POST"])
@login_required
def create():
    name = request.form["name"]
    dest_name = request.form.get("dest_name", "")
    dest_lat = request.form.get("dest_lat")
    dest_lng = request.form.get("dest_lng")
    
    # parse lat lng if available
    try:
        lat = float(dest_lat) if dest_lat else None
        lng = float(dest_lng) if dest_lng else None
    except ValueError:
        lat, lng = None, None

    code = generate_code()
    create_group(name, code, session['user_id'], dest_name, lat, lng)
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
        
    return render_template("group.html", code=code, group=group, user_id=session['user_id'], user_name=session['user_name'])

@group_bp.route("/leave_group", methods=["POST"])
@login_required
def leave_group():
    group_id = request.form.get("group_id")
    remove_member(group_id, session['user_id'])
    flash("You left the group.", "success")
    return redirect(url_for('group.dashboard'))

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

@group_bp.route("/api/start_ride", methods=["POST"])
@login_required
def api_start_ride():
    group_id = request.json.get("group_id")
    name = request.json.get("name", "New Ride")
    ride_id = start_ride(group_id, name)
    return jsonify({"success": True, "ride_id": ride_id})

@group_bp.route("/api/end_ride", methods=["POST"])
@login_required
def api_end_ride():
    data = request.json
    end_ride(data['ride_id'], data['total_distance'], data['duration_minutes'], data['avg_speed'], data['participant_ids'])
    return jsonify({"success": True})

@group_bp.route("/api/eta", methods=["POST"])
@login_required
def api_eta():
    distance = request.json.get("distance_km")
    speed = request.json.get("speed_kmh")
    eta = get_eta(distance, speed)
    return jsonify({"eta": eta})