import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_chat_ids():
    raw = os.getenv("TELEGRAM_CHAT_ID", "")
    if not raw:
        return []
    return [cid.strip() for cid in raw.split(",") if cid.strip()]

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("WARNING: Telegram credentials are not set in .env")

if not GEMINI_API_KEY:
    print("WARNING: Gemini API key is not set in .env")
