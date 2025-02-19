from flask import Blueprint, request, jsonify
from extensions import mongo

db_bp = Blueprint("db", __name__, url_prefix="/db")

@db_bp.route("/register-donor", methods=["POST"])
def register_donor():
    try:
        data = request.json
        mongo.db.donors.insert_one(data)
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
    return jsonify({"status": True,"message": "Donör başarıyla kaydedildi"})

@db_bp.route("/register-patient", methods=["POST"])
def register_patient():
    try:
        data = request.json
        mongo.db.patients.insert_one(data)
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
    return jsonify({"status": True, "message": "Hasta başarıyla kaydedildi"})


@db_bp.route("/get-donors", methods=["GET"])
def get_donors():
    try:
        donors = list(mongo.db.donors.find({}, {'_id': 0})) 
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
    return jsonify({"status": True, "donors": donors})

@db_bp.route("/get-patients", methods=["GET"])
def get_patients():
    try:
        patients = list(mongo.db.patients.find({}, {'_id': 0})) 
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
    return jsonify({"status": True, "patients": patients})

@db_bp.route("/get-all-registers", methods=["GET"])
def get_all_registers():
    try:
        donors = list(mongo.db.donors.find({}, {'_id': 0}))  
        patients = list(mongo.db.patients.find({}, {'_id': 0}))  
        all_registers = {"donors": donors, "patients": patients}
        return jsonify({"status": True, "all_registers": all_registers})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})

@db_bp.route("/delete-register", methods=["POST"])
def delete_register():
    try:
        data = request.json
        collection = mongo.db.donors if data["type"] == "Donor" else mongo.db.patients
        collection.delete_one({"name": data["name"], "surname": data["surname"], "birthdate": data["birthdate"]})
        return jsonify({"status": True, "message": "Register deleted successfully"})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})