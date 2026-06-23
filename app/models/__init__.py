from app.models.google_gemini import Gemini
from app.models.github_openai import GPT

def get_model(provider: str):
    if provider == "google":
        gemini = Gemini()
        return gemini

    if provider == "openai":
        gpt = GPT()
        return gpt

    raise ValueError(f"Invalid agent type: {provider}")
