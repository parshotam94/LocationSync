import google.generativeai as genai
from app.config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

def get_eta(distance, speed):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Distance {distance} km, Speed {speed} km/h. Give ETA."
    return model.generate_content(prompt).text