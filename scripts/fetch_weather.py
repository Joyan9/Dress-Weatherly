# scripts/fetch_weather.py
"""
Weather Data Pipeline

This script fetches hourly weather forecast data from the Open-Meteo API
and loads it into DuckDB using the DLT framework.
"""

import dlt
from typing import Dict, Any, Iterator, List
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# with the help of primary key and write_disposition the table will be loaded incrementally
@dlt.resource(name="hourly_weather", primary_key="time", write_disposition="merge")
def get_hourly_weather(
    latitude: float = 52.5244,
    longitude: float = 13.4105,
    forecast_days: int = 1,
    timezone: str = "Europe/Berlin"
) -> Iterator[Dict[str, Any]]:
    """
    Resource for hourly weather data using Open-Meteo API.
    
    Args:
        latitude: Geographical latitude (default: Berlin)
        longitude: Geographical longitude (default: Berlin)
        forecast_days: Number of days to forecast
        timezone: Local timezone for data
        
    Yields:
        Dictionary containing weather data for each hour
    """
    url = "https://api.open-meteo.com/v1/forecast"
    hourly_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "apparent_temperature",
            "precipitation",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_gusts_10m",
            "cloud_cover",
            "visibility"
        ],
        "models": "icon_seamless",
        "timezone": timezone,
        "forecast_days": forecast_days
    }
    
    try:
        # Get response from API
        logger.info(f"Fetching weather data for coordinates ({latitude}, {longitude})")
        hourly_response = requests.get(url=url, params=hourly_params)
        hourly_response.raise_for_status()  # Raise exception for HTTP errors
        hourly_data = hourly_response.json()
        
        # Extract the hourly data and metadata
        hourly_variables = hourly_data["hourly"]
        hourly_units = hourly_data["hourly_units"]
        timestamps = hourly_variables["time"]
        
        # Generate records for each timestamp
        logger.info(f"Processing {len(timestamps)} hourly records")
        for i in range(len(timestamps)):
            record = {"time": timestamps[i]}
            
            # Add all weather variables with units in column name
            for key in hourly_variables:
                if key != "time":  # Skip time as we already added it
                    key_name = f"{key}_{hourly_units[key].strip()}"
                    record[key_name] = hourly_variables[key][i]
            
            yield record
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {e}")
        raise


def main():
    """Main function to execute the pipeline."""
    try:
        # Create and configure the pipeline
        pipeline = dlt.pipeline(
            pipeline_name="weather_data",
            destination="duckdb",  # Can be changed to other destinations
            dataset_name="open_meteo_weather"
        )
        
        # Run the pipeline
        logger.info("Starting weather data pipeline")
        load_info = pipeline.run(get_hourly_weather())
        logger.info(f"Pipeline run completed. Last Trace: {pipeline.last_trace}")
        logger.info(f"Load Info: {load_info}")
        
        # Display sample data
        #df = pipeline.dataset(dataset_type="default").hourly_weather.df()
        #print("\nSample data from the pipeline:")
        #print(df.head())
        
        return load_info
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    main()