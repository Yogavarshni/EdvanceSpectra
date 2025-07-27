import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.vision_models import ImageGenerationModel
import os
import json

# ========== Step 1: Authenticate using service account ==========
def authenticate(json_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path
    with open(json_path) as f:
        project_id = json.load(f)["project_id"]
    vertexai.init(project=project_id, location="us-central1")
    print(f"Vertex AI initialized for project: {project_id}")

# ========== Step 2: Agent Definitions ==========

class ImageGenAgent:
    def __init__(self):
        self.model = ImageGenerationModel.from_pretrained("imagegeneration@006")

    def generate_image(self, prompt: str):
        print(f"[ImageGenAgent] Generating image for prompt: {prompt}")
        response = self.model.generate_images(prompt=prompt)
        
        # Access images from the response object
        images = response.images

        saved_files = []
        for idx, img in enumerate(images):
            filename = f"generated_image_{idx+1}.png"
            img.save(filename)
            saved_files.append(filename)
            print(f"Saved image: {filename}")
        
        return saved_files


class TextGenAgent:
    def __init__(self):
        self.model = GenerativeModel("gemini-2.5-pro")  # use 2.5 as in your console

    def generate_text(self, prompt: str):
        print(f"[TextGenAgent] Generating text for prompt: {prompt}")
        response = self.model.generate_content(prompt)
        return response.text.strip()

# ========== Step 3: Orchestrator ==========
class AgentOrchestrator:
    def __init__(self):
        self.image_keywords = {
            "draw", "sketch", "generate image", "illustrate",
            "paint", "visual", "show me", "image", "picture"
        }
        self.text_agent = TextGenAgent()
        self.image_agent = ImageGenAgent()

    def route(self, prompt: str):
        lower_prompt = prompt.lower()
        if any(kw in lower_prompt for kw in self.image_keywords):
            return self.image_agent.generate_image(prompt)
        else:
            return self.text_agent.generate_text(prompt)

# ========== Step 4: Run ==========
if __name__ == "__main__":
    # Provide the full path to your service account JSON file
    json_path = "C:/Users/admin/Desktop/Hackathon/adk/orchestration_agent/sahayak-edusphere-91be737bd25c.json"
    authenticate(json_path)

    orchestrator = AgentOrchestrator()

    # Prompt input
    user_prompt = input("Enter your prompt: ").strip()
    print(f"\n--- Prompt: {user_prompt}")
    output = orchestrator.route(user_prompt)
    print("Output:\n", output)
