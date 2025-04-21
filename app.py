# app.py
import os
from flask import Flask, request, jsonify
from bson.objectid import ObjectId
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

from database import init_db

# Load environment variables
load_dotenv()

app = Flask(__name__)
mongo = init_db(app)

# Grab the DB name from config and get the Database object
DB_NAME = app.config["MONGO_DBNAME"]
db = mongo.cx[DB_NAME]   # mongo.cx is the raw pymongo.MongoClient

# -- Helper: SendGrid Email --
def send_email(to_email, subject, content):
    msg = Mail(
        from_email=os.getenv("SENDGRID_FROM_EMAIL"),
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    resp = sg.send(msg)
    return resp.status_code

# ----------------------------------------------------------------
# 1) Teacher: Post Assignment
# ----------------------------------------------------------------
@app.route("/assignments", methods=["POST"])
def create_assignment():
    """
    JSON body: { "title","description","deadline" }
    """
    data = request.get_json() or {}
    doc = {
        "title": data.get("title"),
        "description": data.get("description"),
        "deadline": data.get("deadline"),
        "submissions": []
    }
    result = db.assignments.insert_one(doc)
    return jsonify({"id": str(result.inserted_id)}), 201

# ----------------------------------------------------------------
# 2) Student: Get All Assignments
# ----------------------------------------------------------------
@app.route("/assignments", methods=["GET"])
def list_assignments():
    docs = list(db.assignments.find())
    for d in docs:
        d["_id"] = str(d["_id"])
    return jsonify(docs), 200

# ----------------------------------------------------------------
# 2b) Student: Submit Assignment
# ----------------------------------------------------------------
@app.route("/assignments/<assignment_id>/submit", methods=["PUT"])
def submit_assignment(assignment_id):
    """
    JSON body: { "student_name","submission_link","submitted_at" }
    """
    data = request.get_json() or {}
    sub = {
        "student_name": data.get("student_name"),
        "submission_link": data.get("submission_link"),
        "submitted_at": data.get("submitted_at")
    }
    res = db.assignments.update_one(
        {"_id": ObjectId(assignment_id)},
        {"$push": {"submissions": sub}}
    )
    if res.modified_count:
        return jsonify({"message": "submitted"}), 200
    return jsonify({"error": "not found"}), 404

# ----------------------------------------------------------------
# 3) Send Reminder Email (manual trigger)
# ----------------------------------------------------------------
@app.route("/send-reminder", methods=["POST"])
def send_reminder():
    """
    JSON body: { "to_email","subject","content" }
    """
    data = request.get_json() or {}
    status = send_email(
        data.get("to_email"),
        data.get("subject"),
        data.get("content")
    )
    return jsonify({"status": status}), 200

# ----------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
