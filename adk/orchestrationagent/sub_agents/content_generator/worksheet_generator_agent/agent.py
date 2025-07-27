# from google.adk.agents import Agent
# from google.adk.tools import FunctionTool
# from dotenv import load_dotenv

# from fpdf import FPDF
# import os
# import uuid

# load_dotenv()

# MODEL = "gemini-2.5-pro"

# def save_text_as_pdf(text: str) -> dict:
#     try:
#         pdf = FPDF()
#         pdf.set_auto_page_break(auto=True, margin=15)
#         pdf.add_page()
#         pdf.set_font("Arial", size=12)
#         for line in text.split("\n"):
#             pdf.multi_cell(0, 10, line)

#         filename = f"worksheet_{uuid.uuid4().hex[:8]}.pdf"
#         output_dir = "generated_materials/worksheet"
#         os.makedirs(output_dir, exist_ok=True)
#         filepath = os.path.join(output_dir, filename)
#         pdf.output(filepath)

#         return {
#             "status": "success",
#             "message": "PDF saved successfully.",
#             "filepath": filepath
#         }

#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"Failed to save PDF: {str(e)}"
#         }

# save_pdf_tool = FunctionTool(func=save_text_as_pdf)

# worksheet_generator_agent = Agent(
#     name="worksheet_generator_agent",
#     model=MODEL,
#     description="Generates printable worksheets and saves them as PDFs.",
#     instruction=(
#         "You are an educational assistant who creates printable worksheets for school students.\n\n"
#         "When given a topic and grade, generate a worksheet with exactly 10 questions in plain text.\n"
#         "Use a mix of: short answer, MCQs, fill-in-the-blanks, and true/false.\n"
#         "Number all questions. For MCQs, show options a) b) c) d).\n\n"
#         "Format example:\n"
#         "Title: Water Pollution - Grade 3\n\n"
#         "1. What is water pollution?\n"
#         "2. True or False: Water from rivers is always clean.\n"
#         "3. Which of the following pollutes water?\n   a) Oil   b) Books   c) Air   d) Trees\n"
#         "...\n\n"
#         "After generating the worksheet, immediately call the `save_pdf_tool` with the generated worksheet text to save it as a PDF file.\n"
#         "Do NOT explain or generate any additional output after that.\n"
#         "Return the PDF path and stop."
#     ),
#     tools=[save_pdf_tool]
# )

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

from fpdf import FPDF
import os
import uuid
import firebase_admin
from firebase_admin import credentials, storage as firebase_storage
from google.cloud import storage as gcs_storage

# Load environment variables
load_dotenv()

MODEL = "gemini-2.5-pro"

# === FIREBASE CONFIGURATION ===
FIREBASE_CRED_PATH = os.path.join("orchestrationagent", "edsphere-ai-firebase-adminsdk-fbsvc-30700780ed.json")
STORAGE_BUCKET = "edsphere-ai"  # Must match Firebase bucket name  # Bucket must end with .appspot.com

# === INITIALIZE FIREBASE ===
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred, {
        'storageBucket': STORAGE_BUCKET
    })
bucket = firebase_storage.bucket()

# === SAVE PDF AND UPLOAD TO FIREBASE ===
def save_text_as_pdf(text: str) -> dict:
    try:
        # Generate PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in text.split("\n"):
            pdf.multi_cell(0, 10, line)

        filename = f"worksheet_{uuid.uuid4().hex[:8]}.pdf"
        output_dir = "generated_materials/worksheet"
        os.makedirs(output_dir, exist_ok=True)
        local_path = os.path.join(output_dir, filename)
        pdf.output(local_path)

        # Upload to Firebase Storage
        blob_name = f"worksheets/{filename}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)
        blob.make_public()
        firebase_url = blob.public_url

        return {
            "status": "success",
            "message": "PDF saved and uploaded to Firebase.",
            "local_filepath": local_path,
            "firebase_url": firebase_url
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save or upload PDF: {str(e)}"
        }

# === REGISTER TOOL AND AGENT ===
save_pdf_tool = FunctionTool(func=save_text_as_pdf)

worksheet_generator_agent = Agent(
    name="worksheet_generator_agent",
    model=MODEL,
    description="Generates printable worksheets and saves them as PDFs.",
    instruction=(
        "You are an educational assistant who creates printable worksheets for school students.\n\n"
        "When given a topic and grade, generate a worksheet with exactly 10 questions in plain text.\n"
        "Use a mix of: short answer, MCQs, fill-in-the-blanks, and true/false.\n"
        "Number all questions. For MCQs, show options a) b) c) d).\n\n"
        "Format example:\n"
        "Title: Water Pollution - Grade 3\n\n"
        "1. What is water pollution?\n"
        "2. True or False: Water from rivers is always clean.\n"
        "3. Which of the following pollutes water?\n   a) Oil   b) Books   c) Air   d) Trees\n"
        "...\n\n"
        "After generating the worksheet, immediately call the `save_pdf_tool` with the generated worksheet text to save it as a PDF file and upload it to Firebase.\n"
        "Do NOT explain or generate any additional output after that.\n"
        "Return both the local file path and Firebase public URL, then stop."
    ),
    tools=[save_pdf_tool]
)


