from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from faster_whisper import WhisperModel
from transformers import pipeline
import os

# Load faster-whisper model (can use "small" or "medium" if you have GPU)
whisper_model = WhisperModel("base", compute_type="int8")

# Load Mistral or any small open-source model via HuggingFace Transformers
llm = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.1", max_new_tokens=512)

def transcribe_audio(file_path: str) -> str:
    segments, _ = whisper_model.transcribe(file_path)
    return " ".join(segment.text for segment in segments).strip()

def evaluate_reading(text: str) -> dict:
    prompt = f"""
You are a reading evaluator. Analyze this reading aloud:

"{text}"

Return a JSON with:
- pronunciation_score (out of 10)
- fluency_score (out of 10)
- pace ("Too Fast", "Too Slow", "Just Right")
- issues (if any)
- suggestions for improvement
"""
    output = llm(prompt)[0]['generated_text']
    try:
        start = output.find("{")
        end = output.rfind("}") + 1
        return eval(output[start:end])
    except Exception as e:
        return {"error": "Could not parse response", "raw_output": output}

def process_reading_audio_open(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {"error": "File not found."}
    transcript = transcribe_audio(file_path)
    report = evaluate_reading(transcript)
    return {
        "transcript": transcript,
        "assessment_report": report
    }

reading_assessment_evaluator = Agent(
    name="reading_assessment_evaluator",
    model="local-mistral",
    description="Evaluates student's reading aloud using local Whisper and Mistral",
    instruction="Transcribe audio input and evaluate pronunciation, fluency, and pace using the tool.",
    tools=[process_reading_audio_open],
)
