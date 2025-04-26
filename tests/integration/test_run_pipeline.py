"""
THIS TEST IS NOT COMPLETE YET
"""
import duckdb
import pandas as pd
import os
import pytest
from unittest.mock import patch, MagicMock
from scripts import run_pipeline
from scripts import fetch_weather
from scripts import send_notification

@pytest.fixture(scope="module")  # run once per test module
def setup_test_db():
    """Sets up a test DuckDB database with sample weather data."""
    db_path = "test_weather_data.duckdb"  # Temporary test DB

    # Clean up the database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = duckdb.connect(db_path)

    conn.execute("SET SCHEMA = open_meteo_weather")

    # Create a sample weather table
    conn.execute(
        """
        CREATE TABLE open_meteo_weather.hourly_weather AS
        SELECT * FROM (VALUES
            ('2025-04-27 06:00:00', 15.0, 14.0, 0.0, 70, 10, 15, 50, 10000),
            ('2025-04-27 12:00:00', 22.0, 21.0, 0.1, 60, 12, 18, 40, 10000),
            ('2025-04-27 18:00:00', 18.0, 17.0, 0.0, 75, 8, 12, 60, 9000)
        ) AS t (time, temperature_2m_c, apparent_temperature_c, precipitation_mm, relative_humidity_2m, wind_speed_10m_km_h, wind_gusts_10m_km_h, cloud_cover, visibility)
    """
    )
    conn.close()
    yield db_path  # Provide the database path to the tests
    # Clean up the database after the test
    if os.path.exists(db_path):
        os.remove(db_path)

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

def test_run_pipeline_success(setup_test_db, set_env_vars):
    """
    Integration test for successful pipeline run.
    """
    # Patch fetch_weather.main to simulate successful data loading
    with patch("fetch_weather.main") as mock_fetch_weather, \
         patch("send_notification.send_email_notification") as mock_send_email:

        # Mock the behavior of fetch_weather.main to return successful load info
        mock_fetch_weather.return_value = "LoadInfoMock"

        # Mock the send_email_notification function to avoid sending real emails
        mock_send_email.return_value = True

        # Run the pipeline
        result = run_pipeline.run_pipeline()

        # Assert that the pipeline ran successfully
        assert result is True

        # Assert that fetch_weather.main was called
        mock_fetch_weather.assert_called_once()

        # Assert that send_email_notification was called with some content
        mock_send_email.assert_called_once()
        email_content = mock_send_email.call_args[0][0]
        assert "Weather Summary" in email_content

def test_run_pipeline_fetch_weather_failure(setup_test_db, set_env_vars):
    """
    Integration test for pipeline failure in fetch_weather step.
    """
    with patch("fetch_weather.main") as mock_fetch_weather, \
         patch("send_notification.send_email_notification") as mock_send_email:

        # Mock fetch_weather.main to raise an exception
        mock_fetch_weather.side_effect = Exception("Failed to fetch weather data")

        # Run the pipeline
        result = run_pipeline.run_pipeline()

        # Assert that the pipeline failed
        assert result is False

        # Assert that fetch_weather.main was called
        mock_fetch_weather.assert_called_once()

        # Assert that send_email_notification was not called
        mock_send_email.assert_not_called()


def test_run_pipeline_send_notification_failure(setup_test_db, set_env_vars):
    """
    Integration test for pipeline failure in send_notification step.
    """
    # Patch fetch_weather.main to simulate successful data loading
    with patch("fetch_weather.main") as mock_fetch_weather, \
         patch("send_notification.send_email_notification") as mock_send_email:

        # Mock the behavior of fetch_weather.main to return successful load info
        mock_fetch_weather.return_value = "LoadInfoMock"

        # Mock the send_email_notification function to raise an exception
        mock_send_email.side_effect = Exception("Failed to send email")

        # Run the pipeline
        result = run_pipeline.run_pipeline()

        # Assert that the pipeline failed
        assert result is False

        # Assert that fetch_weather.main was called
        mock_fetch_weather.assert_called_once()

        # Assert that send_email_notification was called with some content
        mock_send_email.assert_called_once()
