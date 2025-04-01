# services/gemini_service.py

import google.generativeai as genai
from flask import current_app
from functools import lru_cache
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=50)
def get_ai_recommendation(prompt_text):
    """
    Send prompt to Gemini API and retrieve structured recommendation.
    Cached for 1 hour to avoid excessive API calls.
    """
    api_key = current_app.config["GEMINI_API_KEY"]
    if not api_key:
        logger.error("GEMINI_API_KEY is not configured")
        raise ValueError("GEMINI_API_KEY is not configured")
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        logger.info("Gemini API configured successfully")
        
        # Create a model instance
        model = genai.GenerativeModel('gemini-pro')
        logger.info("Gemini model initialized")
        
        # Generate content
        response = model.generate_content(prompt_text)
        logger.info("Content generated successfully")
        
        if not response or not response.text:
            logger.error("Empty response from Gemini API")
            raise ValueError("Empty response from Gemini API")
        
        return {
            "text": response.text,
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        return {
            "text": f"AI recommendation service error: {str(e)}",
            "timestamp": int(time.time())
        }
