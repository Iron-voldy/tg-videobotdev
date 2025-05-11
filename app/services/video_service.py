"""
Video generation service with mock mode and Replicate integration
"""
import os
import random
import time
import logging
import requests
import uuid
from config.settings import USE_MOCK_API, USE_REPLICATE, VIDEOS_DIR, REPLICATE_API_TOKEN

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_video(prompt, duration=4):
    """
    Generate a video from text prompt using Replicate API or mock videos
    
    Args:
        prompt (str): Text prompt for video generation
        duration (int): Video duration in seconds
        
    Returns:
        str or None: Path to the generated video or None if generation failed
    """
    # Check if we should use the mock API
    if USE_MOCK_API:
        return _generate_mock_video(prompt, duration)
    elif USE_REPLICATE:
        return _generate_video_with_replicate(prompt, duration)
    else:
        logger.warning("No valid video generation method configured, falling back to mock")
        return _generate_mock_video(prompt, duration)

def _generate_mock_video(prompt, duration=4):
    """Generate a mock video (for testing only)"""
    logger.info(f"Mock API: Generating video for prompt: '{prompt}'")
    
    # Simulate API processing time
    time.sleep(2)
    
    # List of sample video URLs (publicly available test videos)
    sample_videos = [
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
    ]
    
    # Randomly select a video URL
    video_url = random.choice(sample_videos)
    logger.info(f"Mock API returned video URL: {video_url}")
    
    # Generate a unique filename
    unique_id = str(uuid.uuid4())
    video_filename = f"mock_video_{unique_id}.mp4"
    local_path = os.path.join(VIDEOS_DIR, video_filename)
    
    # Download the video
    try:
        # Create videos directory if it doesn't exist
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        
        # Download the video
        logger.info(f"Downloading video from {video_url} to {local_path}")
        response = requests.get(video_url, stream=True)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Video downloaded successfully to {local_path}")
        return local_path
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        # Fall back to URL if download fails
        return video_url

def _generate_video_with_replicate(prompt, duration=4):
    """
    Generate a video using Replicate's Stable Video Diffusion model
    
    Args:
        prompt (str): Text prompt for video generation
        duration (int): Desired duration in seconds (approximate)
        
    Returns:
        str: Path to the generated video file, or None if generation failed
    """
    if not REPLICATE_API_TOKEN:
        logger.error("Replicate API token not set in environment variables")
        return None
        
    try:
        # Ensure videos directory exists
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        
        # Generate a unique filename
        unique_id = str(uuid.uuid4())
        video_filename = f"replicate_video_{unique_id}.mp4"
        local_path = os.path.join(VIDEOS_DIR, video_filename)
        
        logger.info(f"Generating video with Replicate for prompt: '{prompt}'")
        
        # Replicate API endpoint
        api_url = "https://api.replicate.com/v1/predictions"
        
        # Headers with API token
        headers = {
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Model configuration - using Stable Video Diffusion
        # This is the basic stable-video-diffusion model
        payload = {
            "version": "3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
            "input": {
                "prompt": prompt,
                "video_length": "14_frames_with_svd",  # ~2 seconds
                "sizing_strategy": "maintain_aspect_ratio",
                "frames_per_second": 7,
                "motion_bucket_id": 40,  # Higher values = more motion
                "cond_aug": 0.02,
                "decoding_t": 7
            }
        }
        
        # Start the prediction
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code != 201:
            logger.error(f"Failed to start Replicate prediction: {response.text}")
            return None
        
        prediction = response.json()
        prediction_id = prediction.get("id")
        
        if not prediction_id:
            logger.error("No prediction ID in Replicate response")
            return None
            
        logger.info(f"Prediction started with ID: {prediction_id}")
        
        # Poll for prediction completion
        prediction_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
        
        max_attempts = 60
        for attempt in range(max_attempts):
            # Get prediction status
            status_response = requests.get(prediction_url, headers=headers)
            
            if status_response.status_code != 200:
                logger.error(f"Failed to get prediction status: {status_response.text}")
                time.sleep(2)
                continue
                
            prediction_status = status_response.json()
            status = prediction_status.get("status")
            
            if status == "succeeded":
                # Get the output video URL
                output = prediction_status.get("output")
                
                if output and isinstance(output, list) and len(output) > 0:
                    video_url = output[0]  # First item is the video URL
                    
                    logger.info(f"Video generated successfully. URL: {video_url}")
                    
                    # Download the video
                    video_response = requests.get(video_url)
                    
                    if video_response.status_code == 200:
                        with open(local_path, 'wb') as f:
                            f.write(video_response.content)
                        
                        logger.info(f"Video downloaded to {local_path}")
                        return local_path
                    else:
                        logger.error(f"Failed to download video: {video_response.status_code}")
                        return video_url  # Return URL as fallback
                else:
                    logger.error("No output URL in prediction response")
                    return None
            
            elif status == "failed":
                error = prediction_status.get("error")
                logger.error(f"Prediction failed: {error}")
                return None
                
            elif status in ["starting", "processing"]:
                logger.info(f"Prediction in progress... (attempt {attempt+1}/{max_attempts})")
                time.sleep(2)
                continue
                
            else:
                logger.error(f"Unknown prediction status: {status}")
                return None
                
        logger.error("Prediction timed out")
        return None
        
    except Exception as e:
        logger.error(f"Error generating video with Replicate: {e}")
        return None