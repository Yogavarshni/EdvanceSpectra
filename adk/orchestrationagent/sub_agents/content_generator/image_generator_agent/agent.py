import os
import json
import uuid
import vertexai
from vertexai.vision_models import ImageGenerationModel
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import firebase_admin
from firebase_admin import credentials, storage as firebase_storage
from google.cloud import storage as gcs_storage

FIREBASE_CRED_PATH = os.path.join("orchestrationagent", "edsphere-ai-firebase-adminsdk-fbsvc-30700780ed.json")
STORAGE_BUCKET = "edsphere-ai"  # Must match Firebase bucket name# Bucket must end with .appspot.com

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred, {
        'storageBucket': STORAGE_BUCKET
    })
bucket = firebase_storage.bucket()

# ========== FUNCTION TOOL FOR IMAGE GENERATION ==========
def generate_image_with_imagen(prompt: str) -> dict:
    try:
        # --- Step 1: Authenticate and initialize Vertex AI ---
        import os

        key_path = os.path.join("orchestrationagent", "sahayak-edusphere-91be737bd25c.json")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path


        with open(key_path) as f:
            project_id = json.load(f)["project_id"]

        vertexai.init(project=project_id, location="us-central1")
        print(f"[ImageGenTool] Vertex AI initialized for project: {project_id}")

        # --- Step 2: Generate image using Imagen model ---
        model = ImageGenerationModel.from_pretrained("imagegeneration@006")
        print(f"[ImageGenTool] Generating image for prompt: '{prompt}'")
        response = model.generate_images(prompt=prompt)

        # --- Step 3: Save image(s) locally ---
        saved_files = []
        for idx, img in enumerate(response.images):
            filename = f"image_{uuid.uuid4().hex[:8]}.png"
            output_path = os.path.join(os.getcwd(), filename)
            img.save(output_path)
            saved_files.append(output_path)
            print(f"[ImageGenTool] Saved image: {output_path}")

        blob_name = f"images/{filename}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(output_path)
        blob.make_public()
        firebase_url = blob.public_url            

        return {
            "status": "success",
            "message": "Image saved and uploaded to Firebase.",
            "local_filepath": output_path,
            "firebase_url": firebase_url
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save or upload Image: {str(e)}"
        }

# ========== REGISTER TOOL ==========
generate_image_tool = FunctionTool(func=generate_image_with_imagen)

# ========== IMAGE GENERATION AGENT ==========
image_generator_agent = Agent(
    name="image_generator_agent",
    model="gemini-2.5-pro",
    description="Generates educational images using Vertex AI's Imagen model.",
    tools=[generate_image_tool],
    instruction=(
        "You are a visual teaching assistant that generates educational diagrams, charts, and illustrations.\n"
        "Always use the `generate_image_with_imagen` tool to fulfill image requests.\n"
        "Convert user prompts like:\n"
        "- 'A labeled diagram of the digestive system'\n"
        "- 'A cartoon-style map of continents for kids'\n"
        "into clear prompts and generate them.\n"
        "Return the list of image file paths once generated, or an error if failed."
        "Return both the local file path and Firebase public URL, then stop."
    )
)

