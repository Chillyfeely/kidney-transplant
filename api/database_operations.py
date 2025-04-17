from flask import Blueprint, request, jsonify, url_for
from flask_login import login_user, logout_user, login_required, current_user
from extensions import mongo
import uuid
import os
from utils import *
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError
from extensions import db, mongo
from models.user import User

db_bp = Blueprint("db", __name__, url_prefix="/db")



@db_bp.route("/loginuser", methods=["POST"])
def loginuser():
    """
    Handles user login by validating credentials and logging in the user.
    """
    # Access JSON data
    data = request.get_json()
    if not data:
        return jsonify({"status": False, "message": "Invalid JSON data"}), 400

    username = data.get("username")
    password = data.get("password")
    remember = data.get("remember", False)

    # Validate input
    if not username or not password:
        return (
            jsonify({"status": False, "message": "Missing username or password"}),
            400,
        )

    try:
        # Fetch user from the database
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"status": False, "message": "User does not exist"}), 404

        # Check if the password is valid
        if not check_password(password, user.password_hash):
            return jsonify({"status": False, "message": "Invalid password"}), 401

        # Log in the user
        login_user(user, remember=remember)

        # Determine redirect URL
        redirect_url = url_for("website.index")
        return (
            jsonify(
                {
                    "status": True,
                    "message": "Login successful",
                    "redirect": redirect_url,
                }
            ),
            200,
        )

    except SQLAlchemyError as e:
        # Handle database errors
        return (
            jsonify({"status": False, "message": "Database error", "error": str(e)}),
            500,
        )

    except Exception as e:
        # Handle unexpected errors
        return (
            jsonify({"status": False, "message": "Unexpected error", "error": str(e)}),
            500,
        )


@db_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"status": True, "message": "Logged out successfully"}), 200


@db_bp.route("/registeruser", methods=["POST"])
@login_required
def register():
    if current_user.username != "admin":
        return jsonify({"status": "error", "message": "Admin access required"}), 403
    username = request.form.get("username")
    password = request.form.get("password")
    password_again = request.form.get("password_again")

    if not username or not password or not password_again:
        return (
            jsonify({"status": False, "message": "Missing username or password"}),
            400,
        )

    if password != password_again:
        return jsonify({"status": False, "message": "Passwords do not match"}), 400

    try:
        if User.query.filter_by(username=username).first():
            return jsonify({"status": False, "message": "Username already exists"}), 400

        new_user = User(
            user_id=str(uuid.uuid4()),
            username=username,
            password_hash=hash_password(password),
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return jsonify({"status": True, "message": "Registration successful"}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": False, "message": "Database error occurred"}), 500
    except Exception as e:
        return jsonify({"status": False, "message": "Registration failed"}), 500



@db_bp.route("/register-donor", methods=["POST"])
@login_required
def register_donor():
    try:
        data = request.json
        mongo.db.donors.insert_one(data)
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
    return jsonify({"status": True, "message": "Donör başarıyla kaydedildi"})


@db_bp.route("/register-patient", methods=["POST"])
@login_required
def register_patient():
    try:
        data = request.json
        mongo.db.patients.insert_one(data)
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
    return jsonify({"status": True, "message": "Hasta başarıyla kaydedildi"})


@db_bp.route("/get-donors", methods=["GET"])
@login_required
def get_donors():
    try:
        donors = list(mongo.db.donors.find({}, {"_id": 0}))
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
    return jsonify({"status": True, "donors": donors})


@db_bp.route("/get-patients", methods=["GET"])
@login_required
def get_patients():
    try:
        patients = list(mongo.db.patients.find({}, {"_id": 0}))
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
    return jsonify({"status": True, "patients": patients})


@db_bp.route("/get-all-registers", methods=["GET"])
@login_required
def get_all_registers():
    try:
        donors = list(mongo.db.donors.find({}, {"_id": 0}))
        patients = list(mongo.db.patients.find({}, {"_id": 0}))
        all_registers = {"donors": donors, "patients": patients}
        return jsonify({"status": True, "all_registers": all_registers})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@db_bp.route("/delete-register", methods=["POST"])
@login_required
def delete_register():
    try:
        data = request.json
        collection = mongo.db.donors if data["type"] == "Donor" else mongo.db.patients
        collection.delete_one(
            {
                "name": data["name"],
                "surname": data["surname"],
                "birthdate": data["birthdate"],
            }
        )
        return jsonify({"status": True, "message": "Register deleted successfully"})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@db_bp.route("/get-tuple", methods=["POST"])
@login_required
def get_tuple():
    try:
        pair_id = request.json.get("pair_id")
        donor = mongo.db.donors.find_one({"pair_id": pair_id}, {"_id": 0})
        patient = mongo.db.patients.find_one({"pair_id": pair_id}, {"_id": 0})
        return jsonify({"status": True, "donor": donor, "patient": patient})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@db_bp.route("/update-tuple", methods=["POST"])
@login_required
def update_tuple():
    """Update both donor and patient in a single transaction,
    ensuring fields not in the request are cleared."""
    try:
        data = request.json
        pair_id = data.get("pair_id")
        donor_data = data.get("donor")
        patient_data = data.get("patient")

        if not pair_id or not donor_data or not patient_data:
            return jsonify(
                {
                    "status": False,
                    "message": "pair_id, donor and patient data are required",
                }
            )

        # Add pair_id to both records
        donor_data["pair_id"] = pair_id
        patient_data["pair_id"] = pair_id

        # Get existing records to compare with new data
        existing_donor = mongo.db.donors.find_one({"pair_id": pair_id}, {"_id": 0})
        existing_patient = mongo.db.patients.find_one({"pair_id": pair_id}, {"_id": 0})

        if not existing_donor or not existing_patient:
            return jsonify(
                {
                    "status": False,
                    "message": "Donor or patient record not found",
                }
            )

        # Create update documents that explicitly unset fields not in the new data
        donor_update = {"$set": donor_data}
        patient_update = {"$set": patient_data}

        # Find fields to unset (present in existing but not in new data)
        donor_unset = {}
        for key in existing_donor:
            if key != "pair_id" and key != "_id" and key not in donor_data:
                donor_unset[key] = ""

        patient_unset = {}
        for key in existing_patient:
            if key != "pair_id" and key != "_id" and key not in patient_data:
                patient_unset[key] = ""

        # Add unset operations if needed
        if donor_unset:
            donor_update["$set"].update(donor_unset)

        if patient_unset:
            patient_update["$set"].update(patient_unset)

        # Update donor
        donor_result = mongo.db.donors.update_one(
            {"pair_id": pair_id}, donor_update, upsert=False
        )

        # Update patient
        patient_result = mongo.db.patients.update_one(
            {"pair_id": pair_id}, patient_update, upsert=False
        )

        # Check results
        if donor_result.matched_count > 0 and patient_result.matched_count > 0:
            return jsonify(
                {
                    "status": True,
                    "message": "Donör ve hasta bilgileri başarıyla güncellendi",
                }
            )
        else:
            return jsonify(
                {"status": False, "message": "Update failed - records may not exist"}
            )

    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
