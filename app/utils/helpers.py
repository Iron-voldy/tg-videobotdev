import datetime
from config.settings import BLOCKED_WORDS

def is_safe_prompt(prompt):
    """
    Check if a prompt is safe by filtering for blocked words
    
    Args:
        prompt (str): The prompt to check
        
    Returns:
        bool: True if the prompt is safe, False otherwise
    """
    prompt_lower = prompt.lower()
    for word in BLOCKED_WORDS:
        if word in prompt_lower:
            return False
    return True

def format_welcome_message(referral_code, free_generations):
    """
    Format the welcome message for new users
    
    Args:
        referral_code (str): User's referral code
        free_generations (int): Number of free generations
        
    Returns:
        str: Formatted welcome message
    """
    message = (
        f"🎬 Welcome to the AI Video Generator Bot! 🎬\n\n"
        f"You have {free_generations} free video generations.\n\n"
        f"Simply send me a text prompt like 'a futuristic city at night' "
        f"and I'll generate a video for you.\n\n"
        f"🔗 Your referral code: {referral_code}\n"
        f"Share it with friends and earn 1 free generation for each referral!\n\n"
        f"Commands:\n"
        f"/start - Show this message\n"
        f"/balance - Check your balance\n"
        f"/buy - Buy more generations\n"
        f"/help - Get help"
    )
    return message

def is_free_plan_active(user):
    """
    Check if user's free plan is still active
    
    Args:
        user: User object from database
        
    Returns:
        bool: True if free plan is active, False otherwise
    """
    now = datetime.datetime.utcnow()
    return user.free_plan_expires_at > now