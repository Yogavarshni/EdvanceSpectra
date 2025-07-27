import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use correct model for google.generativeai SDK
MODEL = "gemini-1.5-pro-latest"
llm = genai.GenerativeModel(MODEL)

def generate_prompt_from_list(input_list: list[str]) -> str:
    joined_input = ", ".join(input_list)
    system_instruction = """
        You are a prompt generator. You will receive a list describing an educational resource.
        Convert the list into a clear, concise instruction prompt.

        Examples:
        Input: ["Image", "Parts of body", "Grade 2"]
        Output: Generate an image of parts of body for grade 2.

        Input: ["worksheet", "p-block elements", "10 marks", "grade 11"]
        Output: Generate a worksheet for grade 11 on p-block elements for 10 marks.

        Only return the generated prompt. Don't include explanations or extra commentary.
        """

    user_message = f"Input: [{joined_input}]"
    response = llm.generate_content([system_instruction, user_message])
    return response.text.strip()

