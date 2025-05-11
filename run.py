from app.bot import setup_bot
from telegram import Update
import logging
import os
import sys

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if the environment is properly set up"""
    from config.settings import TELEGRAM_TOKEN, VIDEOS_DIR
    
    # Check if videos directory exists
    if not os.path.exists(VIDEOS_DIR):
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        logger.info(f"Created videos directory at {VIDEOS_DIR}")
    
    # Check if Telegram token is set
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN environment variable is not set")
        return False
    
    return True

def main():
    """Run the bot."""
    try:
        logger.info("Initializing bot...")
        
        # Check environment
        if not check_environment():
            logger.error("Environment not properly set up. Exiting.")
            return
        
        # Set up and start the bot
        application = setup_bot()
        
        # Start the Bot
        logger.info("Starting bot with polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
        logger.info("Bot started")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        
if __name__ == "__main__":
    main()