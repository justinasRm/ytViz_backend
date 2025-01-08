import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import base64

firebase_key_base64 = os.getenv('FIREBASE_KEY_BASE64')
firebase_key = json.loads(base64.b64decode(firebase_key_base64).decode('utf-8'))

cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred)

db = firestore.client()

def get_firestore_client():
    return db