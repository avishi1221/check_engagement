from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

app = Flask(__name__)

# ✅ Firebase Setup
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ✅ Add Homepage Route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Customer Engagement API!"})

# ✅ Test Firebase Connection
@app.route('/test', methods=['GET'])
def test_connection():
    try:
        doc_ref = db.collection("test").document("hello")
        doc_ref.set({"message": "Firebase is working!"})
        return jsonify({"status": "success", "message": "Firebase is connected!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ✅ Get Inactive Users
@app.route('/inactive_users', methods=['GET'])
def get_inactive_users():
    try:
        inactive_users = []
        users_ref = db.collection("users").stream()

        for user in users_ref:
            data = user.to_dict()
            last_visit = datetime.strptime(data["last_visit"], "%Y-%m-%d")
            days_since_last = (datetime.today() - last_visit).days

            if days_since_last > 30 or data.get("interaction_score", 1) < 0.5:
                inactive_users.append({"user_id": data["user_id"], "score": data["interaction_score"]})

        return jsonify({"inactive_users": inactive_users}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
