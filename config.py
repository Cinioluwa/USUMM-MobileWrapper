import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # A strong, random key used by Flask to secure sessions (required for OAuth)
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_fallback_key_for_dev') 
    
    # YouTube OAuth Credentials (for accessing the user's feed)
    GOOGLE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
    
    # Public API Key (Still useful for non-authenticated searches if needed)
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY') 
    
    # Your Gemini API Key
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')