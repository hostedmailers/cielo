import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    try:
        # Use the JSON file you downloaded from Firebase Console
        cred = credentials.Certificate("Cielo Firebase Admin SDK.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {str(e)}")
        return None

# Function to check database connectivity
def check_db_connectivity(db):
    try:
        # Attempt to access a collection to ensure a connection can be established
        db.collection('test').document('connectivity_check').get()
        print("Successfully connected to Firestore database.")
        return True
    except Exception as e:
        print(f"Failed to connect to Firestore database: {str(e)}")
        return False

# Initialize Firestore and check connectivity
