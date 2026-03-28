import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # Safely get API_ID as an integer, default to 0 if not a number or empty
    _api_id = os.getenv("API_ID", "0")
    API_ID = int(_api_id) if _api_id.isdigit() else 0
    
    API_HASH = os.getenv("API_HASH", "")
    CAPTION_TEXT = os.getenv("CAPTION_TEXT", "Join @omnix_Empire")
    CAPTION_POSITION = os.getenv("CAPTION_POSITION", "bottom").lower()
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "omnixmain")