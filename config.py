# config.py
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"

def get_youtube_client():
    """
    Initialize the YouTube API client using the API key stored in the .env file.
    """

    return build("youtube", "v3", developerKey=API_KEY)
