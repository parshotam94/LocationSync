from flask import Blueprint, render_template, request, redirect
import random, string
from app.models.group_model import create_group

group_bp = Blueprint("group", __name__)

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@group_bp.route("/")
def index():
    return render_template("index.html")

@group_bp.route("/create_group", methods=["POST"])
def create():
    name = request.form["name"]
    code = generate_code()
    create_group(name, code)
    return redirect(f"/group/{code}")

@group_bp.route("/group/<code>")
def group_page(code):
    return render_template("group.html", code=code)