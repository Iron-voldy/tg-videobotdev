import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# API settings
USE_MOCK_API = os.getenv('USE_MOCK_API', 'True').lower() == 'true'
USE_REPLICATE = os.getenv('USE_REPLICATE', 'False').lower() == 'true'

# Video generation settings
DEFAULT_VIDEO_DURATION = int(os.getenv('DEFAULT_VIDEO_DURATION', '4'))
FREE_GENERATIONS = int(os.getenv('FREE_GENERATIONS', '3'))

# Database settings
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///telebot.db')

# Replicate API token
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')

# Content filter
BLOCKED_WORDS = [
    'explicit', 'nudity', 'porn', 'pornography', 'sex', 'sexual', 
    'violence', 'gore', 'blood', 'hate', 'racist', 'terrorism'
]

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(BASE_DIR, 'videos')
os.makedirs(VIDEOS_DIR, exist_ok=True)