import os
from datetime import datetime
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, storage as firebase_storage
from google.cloud import storage as gcs_storage

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# ---------- Load environment ----------
load_dotenv()
MODEL = "gemini-2.5-pro"

# ---------- Firebase Setup ----------
import os

FIREBASE_CRED_PATH = os.path.join("orchestrationagent", "edsphere-ai-firebase-adminsdk-fbsvc-30700780ed.json")
STORAGE_BUCKET = "edsphere-ai"  # Must match Firebase bucket name

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred, {
        'storageBucket': STORAGE_BUCKET
    })
bucket = firebase_storage.bucket()

# ---------- Save HTML Tool ----------
def save_html_file(content: str, topic: str, output_dir: str = "generated_games") -> dict:
    try:
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename
        filename = f"{topic.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        file_path = os.path.join(output_dir, filename)

        # Write file locally
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Upload to Firebase Storage
        blob_name = f"games/{filename}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        blob.make_public()

        return {
            "status": "success",
            "message": "Game HTML saved and uploaded to Firebase.",
            "local_filepath": file_path,
            "firebase_url": blob.public_url
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save or upload HTML: {str(e)}"
        }

save_html_tool = FunctionTool(
    save_html_file
)

# ---------- Agent Setup ----------
game_generator_agent = Agent(
    name="game_generator_agent",
    model=MODEL,
    description="Creates interactive learning games for students like flashcards, riddles, and quizzes as HTML/CSS/JS code.",
    instruction=(
        """You are a creative educational game master for kids.

        When a user provides a topic and grade level, generate 3 sets of interactive learning content:

        1. **Flashcards**  
           Generate HTML/CSS/JS for a flashcard game with 5 question-answer cards on the topic.  
           Flip-style cards. Click to reveal the answer.  
           Keep the code self-contained.

        2. **Riddles**  
           Create a fun HTML layout of 5 riddles where clicking on a riddle reveals the answer below it.  
           Use basic JS toggle for show/hide.

        3. **Quiz Game**  
           Create a 5-question multiple-choice quiz on the topic.  
           Provide 4 options per question and show score at the end using JavaScript.  
           The user should be able to click and answer each question in sequence.

        Keep the UI clean, kid-friendly, and responsive. Use simple colors, rounded corners, and readable fonts.

        Use only plain HTML, CSS, and JS (no external frameworks). Output full code blocks for each game type.
        Then call the `save_html_file` tool to save the file to disk and Firebase.
        Return both the local file path and Firebase public URL, then stop.
        """
    ),
    tools=[save_html_tool]
)
