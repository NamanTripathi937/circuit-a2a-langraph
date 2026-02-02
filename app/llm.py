import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Load the API Key from environment variables
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
# You can choose "gemini-1.5-flash" or "gemini-1.5-pro"
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-1.5-flash")

def get_llm():
    """
    Returns a Gemini LLM instance using the Google API Key.
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        streaming=True
    )