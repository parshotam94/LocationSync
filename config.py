import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = "secret"

    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "yourpassword"
    MYSQL_DB = "tracker_db"

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")