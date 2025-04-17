from flask import Blueprint
from flask import render_template, session, redirect, request
from flask_login import login_required, current_user

website_bp = Blueprint("website", __name__, template_folder="templates")

@website_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/register-tuple")
    else:
        return redirect("/login")

@website_bp.route("/login")
def login():
    return render_template("login.html")

@website_bp.route("/register")
@login_required
def register():
    session.clear()
    return render_template("register.html", username=current_user.username)

@website_bp.route("/matches")
@login_required
def matches():
    return render_template("matches.html",username=current_user.username)

@website_bp.route("/register-tuple")
@login_required
def register_tuple():
    return render_template("register-tuple.html",username=current_user.username)

@website_bp.route("/data-management")
@login_required
def data_management():
    return render_template("data-management.html",username=current_user.username)

@website_bp.route("/update-tuple/<string:pair_id>")
@login_required
def update_tuple(pair_id):
    return render_template("update-tuple.html", pair_id=pair_id)