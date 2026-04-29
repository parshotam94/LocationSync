import google.generativeai as genai
from app.config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

def get_eta(distance, speed):
    if float(speed) <= 0:
        return "N/A"
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"Calculate the estimated time of arrival. Only return a very short human-readable time string (e.g. '15 mins', '2 hrs'). Distance: {distance} km, Speed: {speed} km/h."
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "N/A"