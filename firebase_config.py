import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
# (Make sure to set GOOGLE_APPLICATION_CREDENTIALS environment variable or pass service account key)
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

def log_agent_action(action_type: str, details: dict):
    """Writes an audit log to Firestore for hackathon tracking."""
    try:
        doc_ref = db.collection("smashx_audit_logs").document()
        doc_ref.set({
            "action_type": action_type,
            "details": details,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print(f"Firestore logging error: {e}")