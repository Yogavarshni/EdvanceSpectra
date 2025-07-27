import firebase_admin
from firebase_admin import credentials, storage as firebase_storage, firestore
from google.cloud import storage as gcs_storage
import os

# === CONFIG ===
FIREBASE_CRED_PATH = "C:\\Users\\sanjay venkat\\Downloads\\sahayak-edusphere-df930.json"
STORAGE_BUCKET = "sahayak-edusphere-df930"  # Full bucket name must end with .appspot.com

# === INITIALIZE FIREBASE ===
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': STORAGE_BUCKET
        })

    db = firestore.client()
    bucket = firebase_storage.bucket()
    return db, bucket

# === UPLOAD PDF TO GCS ===
def upload_pdf(grade, pdf_path):
    # Load credentials
    creds = gcs_storage.Client.from_service_account_json(FIREBASE_CRED_PATH)
    bucket = creds.bucket(STORAGE_BUCKET)

    # Create blob path inside the bucket
    blob_name = f"{grade}/{os.path.basename(pdf_path)}"
    blob = bucket.blob(blob_name)

    # Optional: smaller chunks for large files (e.g., 5 MB)
    blob.chunk_size = 5 * 1024 * 1024  # 5MB

    # Upload the file
    blob.upload_from_filename(pdf_path)
    print(f"✅ Uploaded {pdf_path} to gs://{STORAGE_BUCKET}/{blob_name}")

# === MAIN ===
if __name__ == "__main__":
    initialize_firebase()

    upload_pdf(
        grade="Grade_7",
        pdf_path="C:\\Users\\sanjay venkat\\Downloads\\7th Eng Science Part-1 2024-25.pdf"
    )

    upload_pdf(
        grade="Grade_8",
        pdf_path="C:\\Users\\sanjay venkat\\Downloads\\media_to_upload1717418193.pdf"
    )
