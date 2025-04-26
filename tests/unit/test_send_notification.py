import os
import smtplib
from unittest.mock import patch, MagicMock
import pytest
from scripts.send_notification import send_email_notification
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


@pytest.fixture(autouse=True)
def set_env_vars():
    """
    Fixture to set environment variables before each test and reset after.
    """
    original_env = os.environ.copy()
    os.environ["SENDER_EMAIL"] = "test@example.com"
    os.environ["SENDER_APP_PASSWORD"] = "test_password"
    yield
    os.environ.clear()
    os.environ.update(original_env)


@patch("scripts.send_notification.smtplib.SMTP")
def test_send_email_notification_success(mock_smtp):
    """
    Test successful email sending.
    """
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    mock_server.starttls.return_value = None
    mock_server.login.return_value = None
    mock_server.send_message.return_value = None

    content = "Test email content"
    result = send_email_notification(content)
    assert result is True
    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("test@example.com", "test_password")
    mock_server.send_message.assert_called_once()


@patch("scripts.send_notification.smtplib.SMTP")
def test_send_email_notification_failure(mock_smtp):
    """
    Test email sending failure.
    """
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    mock_server.starttls.return_value = None
    mock_server.login.side_effect = Exception("Login failed")

    content = "Test email content"
    result = send_email_notification(content)
    assert result is False
    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("test@example.com", "test_password")
    mock_server.send_message.assert_not_called()


@patch("scripts.send_notification.smtplib.SMTP")
def test_send_email_notification_missing_env_vars(mock_smtp):
    """
    Test email sending failure with missing environment variables.
    """
    # Clear environment variables
    os.environ.pop("SENDER_EMAIL", None)
    os.environ.pop("SENDER_APP_PASSWORD", None)

    content = "Test email content"
    result = send_email_notification(content)
    assert result is False
    mock_smtp.assert_not_called()


@patch("scripts.send_notification.smtplib.SMTP")
def test_send_email_notification_recipient(mock_smtp):
    """
    Test email sending to a specific recipient.
    """
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    mock_server.starttls.return_value = None
    mock_server.login.return_value = None
    mock_server.send_message.return_value = None

    content = "Test email content"
    recipient_email = "recipient@example.com"
    result = send_email_notification(content, recipient_email)
    assert result is True
    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("test@example.com", "test_password")
    mock_server.send_message.assert_called_once()
    args, kwargs = mock_server.send_message.call_args
    message = args[0]
    assert message["To"] == "recipient@example.com"


def test_email_content_format():
    """
    Test email content format and structure
    """
    content = "Outfit recommendation: Wear a jacket."
    recipient_email = "recipient@example.com"

    # Call function with test parameters
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.starttls.return_value = None
        mock_server.login.return_value = None
        mock_server.send_message.return_value = None
        result = send_email_notification(content, recipient_email)

        # Retrieve email content
        args, kwargs = mock_server.send_message.call_args
        message = args[0]
        email_body = message.get_payload()[0].get_payload()

        expected_content = f"""Hello from Dress-Weatherly!

Here's your daily weather and outfit recommendation:

{content}

Stay comfortable!"""

        # Assert email content
        assert expected_content in email_body

