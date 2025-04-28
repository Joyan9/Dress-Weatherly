#!/usr/bin/env python3
"""
Main orchestrator script for the Dress-Weatherly pipeline.

This script coordinates the execution of the complete pipeline:
1. Fetch weather data
2. Generate outfit recommendations
3. Send email notifications

It handles errors properly and ensures all resources are cleaned up.
"""

import logging
import sys
import os
import time
from datetime import datetime

# Import pipeline components
import fetch_weather
from recommend_outfit import OutfitRecommender
from send_notification import send_email_notification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_pipeline():
    """Run the complete weather and outfit recommendation pipeline."""
    start_time = time.time()
    logger.info(f"Starting Dress-Weatherly pipeline at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check for required environment variables
    required_env_vars = ["SENDER_EMAIL", "SENDER_APP_PASSWORD"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Step 1: Fetch weather data
    logger.info("Step 1: Fetching weather data")
    try:
        load_info = fetch_weather.main()
        logger.info(f"Weather data successfully fetched and stored: {load_info}")
    except Exception as e:
        logger.error(f"Error in fetch_weather step: {e}")
        return False
    
    # Step 2: Generate outfit recommendation
    logger.info("Step 2: Generating outfit recommendation")
    recommender = OutfitRecommender()
    try:
        # Get outfit recommendation
        outfit_recommendation = recommender.get_outfit_recommendation()
        logger.info("Outfit recommendation generated successfully")
    except Exception as e:
        logger.error(f"Error in recommend_outfit step: {e}")
        recommender.close()
        return False
    finally:
        # Ensure we close the recommender connection
        recommender.close()
    
    # Step 3: Send notification
    logger.info("Step 3: Sending notification")
    try:
        # Get recipient email from environment or use sender email as default
        recipient_email = os.environ.get("RECIPIENT_EMAIL", os.environ.get("SENDER_EMAIL"))
        
        # Send notification
        notification_sent = send_email_notification(
            outfit_recommendation, 
            recipient_email
        )
        
        if notification_sent:
            logger.info("Notification sent successfully")
        else:
            logger.error("Failed to send notification")
            return False
    except Exception as e:
        logger.error(f"Error in send_notification step: {e}")
        return False
    
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"Pipeline completed successfully in {execution_time:.2f} seconds")
    return True

if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
