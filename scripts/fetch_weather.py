"""
This script fetches hourly weather forecast data from the Open-Meteo API
and loads it into DuckDB using the dlt library.
"""

import dlt
from typing import Dict, Any, Iterator, List, Optional
import requests
import logging
from dlt.extract.exceptions import ResourceExtractionError

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
        
    Raises:
        requests.exceptions.RequestException: For API request failures
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
        
        # Check for HTTP errors before parsing the response
        try:
            hourly_response.raise_for_status()  # Raise exception for HTTP errors
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}, Status code: {hourly_response.status_code}")
            logger.error(f"Response content: {hourly_response.text[:500]}")  # Log first 500 chars of response
            raise  # Re-raise the exception
            
        hourly_data = hourly_response.json()
        
        # Validate the response structure
        if "hourly" not in hourly_data or "hourly_units" not in hourly_data:
            error_msg = f"Invalid API response format: missing required fields"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Extract the hourly data and metadata
        hourly_variables = hourly_data["hourly"]
        hourly_units = hourly_data["hourly_units"]
        
        # Validate timestamps exist
        if "time" not in hourly_variables or not hourly_variables["time"]:
            error_msg = "No timestamp data found in API response"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
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
    except Exception as e:
        logger.error(f"Unexpected error in get_hourly_weather: {e}")
        raise


def main() -> Optional[Any]:
    """
    Main function to execute the pipeline.
    
    Returns:
        Load information from the pipeline run, or None if an error occurred
    """
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
        
        return load_info
        
    except ResourceExtractionError as e:
        logger.error(f"Data extraction failed: {e}")
        # You could implement retry logic or fallback here
        return None
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return None


if __name__ == "__main__":
    main()