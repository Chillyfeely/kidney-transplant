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
    return jsonify({"status": True, "message": "Donör başarıyla kaydedildi"})


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
        donors = list(mongo.db.donors.find({}, {"_id": 0}))
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
    return jsonify({"status": True, "donors": donors})


@db_bp.route("/get-patients", methods=["GET"])
def get_patients():
    try:
        patients = list(mongo.db.patients.find({}, {"_id": 0}))
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})
    return jsonify({"status": True, "patients": patients})


@db_bp.route("/get-all-registers", methods=["GET"])
def get_all_registers():
    try:
        donors = list(mongo.db.donors.find({}, {"_id": 0}))
        patients = list(mongo.db.patients.find({}, {"_id": 0}))
        all_registers = {"donors": donors, "patients": patients}
        return jsonify({"status": True, "all_registers": all_registers})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@db_bp.route("/delete-register", methods=["POST"])
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
def get_tuple():
    try:
        pair_id = request.json.get("pair_id")
        donor = mongo.db.donors.find_one({"pair_id": pair_id}, {"_id": 0})
        patient = mongo.db.patients.find_one({"pair_id": pair_id}, {"_id": 0})
        return jsonify({"status": True, "donor": donor, "patient": patient})
    except Exception as e:
        return jsonify({"status": False, "message": str(e)})


@db_bp.route("/update-tuple", methods=["POST"])
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
