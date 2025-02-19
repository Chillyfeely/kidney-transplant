from flask import Blueprint
from flask import render_template, session, redirect, request

website_bp = Blueprint("website", __name__, template_folder="templates")

@website_bp.route("/")
def index():
    return redirect("/matches")


@website_bp.route("/matches")
def matches():
    return render_template("matches.html")


@website_bp.route("/register-patient")
def register_patient():
    return render_template("register-patient.html")


@website_bp.route("/register-donor")
def register_donor():
    return render_template("register-donor.html")

@website_bp.route("/data-management")
def data_management():
    return render_template("data-management.html")