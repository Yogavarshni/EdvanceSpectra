import os
import json
import tempfile
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.vision_models import ImageGenerationModel
from google.cloud import texttospeech, speech
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr 

# ========== STEP 1: AUTHENTICATION ==========
def authenticate(json_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path
    with open(json_path) as f:
        project_id = json.load(f)["project_id"]
    vertexai.init(project=project_id, location="us-central1")
    print(f"Vertex AI initialized for project: {project_id}")

# ========== STEP 2: AGENTS ==========

class TextGenAgent:
    def __init__(self):
        self.model = GenerativeModel("gemini-2.5-pro")

    def generate_text(self, prompt: str) -> str:
        print("[TextGenAgent] Generating text...")
        response = self.model.generate_content(prompt)
        return ''.join([p.text for p in response.candidates[0].content.parts if hasattr(p, "text")])

class ImageGenAgent:
    def __init__(self):
        # Load the image generation model (ensure this is correct for your region/version)
        self.model = ImageGenerationModel.from_pretrained("imagegeneration@006")

    def generate_image(self, prompt: str):
        print(f"[ImageGenAgent] Generating image for prompt: {prompt}")
        response = self.model.generate_images(prompt=prompt)

        saved_files = []
        for idx, img in enumerate(response.images):
            filename = f"generated_image_{idx+1}.png"
            img.save(filename)  # Save using the .save() method now supported
            saved_files.append(filename)
            print(f"Saved image: {filename}")
        
        return saved_files


class TextToSpeechAgent:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()

    def speak(self, text: str):
        print("[TTSAgent] Speaking...")
        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Neural2-J")
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = self.client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out:
            out.write(response.audio_content)
            out_path = out.name
        play(AudioSegment.from_mp3(out_path))
        os.remove(out_path)

class SpeechToTextAgent:
    def __init__(self):
        self.client = speech.SpeechClient()

    def transcribe(self, file_path: str) -> str:
        print("[STTAgent] Transcribing audio...")
        with open(file_path, "rb") as f:
            audio_content = f.read()
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US"
        )
        response = self.client.recognize(config=config, audio=audio)
        return response.results[0].alternatives[0].transcript if response.results else ""

# ========== STEP 3: PLANNER (AGENTIC DECISION MAKER) ==========
class PlannerAgent:
    def __init__(self):
        self.model = GenerativeModel("gemini-2.5-pro")

    def decide_action(self, user_prompt: str) -> str:
        system_prompt = (
            "You're a routing agent in a multimodal AI system. "
            "Decide the correct tool to use based on the input: "
            "`text`, `image`, `audio_in`, or `audio_out` only. "
            "Respond with one word only."
        )
        response = self.model.generate_content([system_prompt, user_prompt])
        tool = response.text.strip().lower()
        print(f"[PlannerAgent] Selected tool: {tool}")
        return tool

# ========== STEP 4: ORCHESTRATOR ==========
class AgentOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.text_agent = TextGenAgent()
        self.image_agent = ImageGenAgent()
        self.tts_agent = TextToSpeechAgent()
        self.stt_agent = SpeechToTextAgent()

    def route(self, user_input: str, is_audio: bool = False):
        if is_audio:
            text_prompt = self.stt_agent.transcribe(user_input)
        else:
            text_prompt = user_input

        action = self.planner.decide_action(text_prompt)

        if action == "text":
            result = self.text_agent.generate_text(text_prompt)
            print("Text Output:\n", result)
        elif action == "image":
            result = self.image_agent.generate_image(text_prompt)
            print("Generated image paths:", result)
        elif action == "audio_out":
            text = self.text_agent.generate_text(text_prompt)
            self.tts_agent.speak(text)
            result = "[Audio spoken]"
        elif action == "audio_in":
            result = self.stt_agent.transcribe(text_prompt)
            print("Transcribed Audio:\n", result)
        else:
            result = "Unknown action."
        return result

# ========== STEP 5: MAIN RUN ==========
if __name__ == "__main__":
    authenticate("C:\\Users\\sanjay venkat\\Downloads\\Agents\\sahayak-edusphere.json")
    orchestrator = AgentOrchestrator()

    mode = input("Choose input type (text/audio): ").strip().lower()
    
    if mode == "audio":
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Speak now...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            print("🔁 Converting speech to text...")
            try:
                text_prompt = recognizer.recognize_google(audio)
                print(f"📝 You said: {text_prompt}")
                output = orchestrator.route(text_prompt, is_audio=False)
            except sr.UnknownValueError:
                print("❌ Could not understand the audio.")
                output = ""
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                output = ""
    else:
        user_prompt = input("Enter your prompt: ").strip()
        output = orchestrator.route(user_prompt)

    print("\n✅ Final Output:", output)





#https://us-central1-aiplatform.googleapis.com/v1/projects/sahayak-edusphere/locations/us-central1/publishers/google/models