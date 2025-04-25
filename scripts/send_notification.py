#!/usr/bin/env python3
"""
Email notification module for the Dress-Weatherly application.
Sends weather and outfit recommendations via email.
"""

import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def send_email_notification(content, recipient_email=None):
    """
    Send an email notification with the given content.
    
    Args:
        content (str): The content to include in the email body
        recipient_email (str, optional): The recipient's email address. 
                                         If None, uses sender_email.
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Get credentials from environment variables
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    
    # If recipient email is not provided, send to self
    if not recipient_email:
        recipient_email = sender_email
    
    # Validate required environment variables
    if not sender_email or not sender_password:
        logger.error("Missing required environment variables: SENDER_EMAIL or SENDER_APP_PASSWORD")
        return False
    
    # Format the current date
    date = datetime.now().strftime("%Y-%m-%d")
    subject = f"Dress-Weatherly: Weather & Outfit Report for {date}"
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    
    # Format the email content with monospace formatting for recommendations
    formatted_content = f"""
Hello from Dress-Weatherly!

Here's your daily weather and outfit recommendation:

{content}

Stay comfortable!
""".strip()
    
    # Add text content
    message.attach(MIMEText(formatted_content, "plain"))
    
    # Send email
    try:
        logger.info(f"Attempting to send email to {recipient_email}")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        logger.info("Email sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


if __name__ == "__main__":
    # This allows the script to be run directly for testing
    try:
        from recommend_outfit import OutfitRecommender
        
        logger.info("Running send_notification directly for testing")
        recommender = OutfitRecommender()
        try:
            content = recommender.get_outfit_recommendation()
            # Get recipient email from environment or use sender email
            recipient = os.environ.get("RECIPIENT_EMAIL", os.environ.get("SENDER_EMAIL"))
            
            # Send the email
            if send_email_notification(content, recipient):
                logger.info("Notification sent successfully")
            else:
                logger.error("Failed to send notification")
        finally:
            recommender.close()
    except Exception as e:
        logger.error(f"Error in send_notification script: {e}")