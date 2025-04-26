# tests/test_fetch_weather.py

from unittest.mock import patch, MagicMock
import pytest
from scripts.fetch_weather import get_hourly_weather
from dlt.extract.exceptions import ResourceExtractionError
from requests.exceptions import HTTPError

@patch('scripts.fetch_weather.requests.get')
def test_get_hourly_weather_api_error(mock_get):
    """
    Test that API errors are properly wrapped in ResourceExtractionError
    and contain the original HTTPError as the cause
    """
    # Setup mock to raise HTTPError
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("API error")
    mock_get.return_value = mock_response

    # Should expect the dlt wrapper exception
    with pytest.raises(ResourceExtractionError) as exc_info:
        list(get_hourly_weather())

    # Verify the original error is preserved as the cause
    assert isinstance(exc_info.value.__cause__, HTTPError)
    assert "API error" in str(exc_info.value.__cause__)



@patch('scripts.fetch_weather.requests.get')
def test_hourly_weather_record_schema(mock_get):
    """
    This test check whether all the keys are present in the yielded dictionaries and that types are as expected
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "hourly": {
            "time": ["2025-04-26T12:00"],
            "temperature_2m": [20],
            "apparent_temperature": [19],
            "precipitation": [0],
            "relative_humidity_2m": [60],
            "wind_speed_10m": [5],
            "wind_gusts_10m": [10],
            "cloud_cover": [50],
            "visibility": [10000]
        },
        "hourly_units": {
            "time": "",
            "temperature_2m": "°C",
            "apparent_temperature": "°C",
            "precipitation": "mm",
            "relative_humidity_2m": "%",
            "wind_speed_10m": "km/h",
            "wind_gusts_10m": "km/h",
            "cloud_cover": "%",
            "visibility": "m"
        }
    }
    
    mock_get.return_value = mock_response

    result = list(get_hourly_weather())[0]
    expected_keys = {
        "time", "temperature_2m_°C", "apparent_temperature_°C", "precipitation_mm",
        "relative_humidity_2m_%", "wind_speed_10m_km/h", "wind_gusts_10m_km/h",
        "cloud_cover_%", "visibility_m"
    }
    assert set(result.keys()) == expected_keys


# get_hourly_weather is a generator therefore we convert it's output into a list for easier testing
@patch('scripts.fetch_weather.requests.get')
def test_get_hourly_weather_success(mock_get):
    """
    This test checks that the generator yields the expected records and that the API call is made as expected.
    """
    # mock API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "hourly": {
            "time": ["2025-04-26T12:00", "2025-04-26T13:00"],
            "temperature_2m": [20, 21],
            "apparent_temperature": [19, 20],
            "precipitation": [0, 0],
            "relative_humidity_2m": [60, 65],
            "wind_speed_10m": [5, 6],
            "wind_gusts_10m": [10, 12],
            "cloud_cover": [50, 60],
            "visibility": [10000, 10000]
        },
        "hourly_units": {
            "time": "",
            "temperature_2m": "°C",
            "apparent_temperature": "°C",
            "precipitation": "mm",
            "relative_humidity_2m": "%",
            "wind_speed_10m": "km/h",
            "wind_gusts_10m": "km/h",
            "cloud_cover": "%",
            "visibility": "m"
        }
    }
    mock_get.return_value = mock_response
    mock_get.return_value = mock_response

    # Call the generator and collect results
    results = list(get_hourly_weather())

    assert len(results) == 2
    assert results[0]["time"] == "2025-04-26T12:00"
    assert results[0]["temperature_2m_°C"] == 20
    assert results[1]["cloud_cover_%"] == 60
    mock_get.assert_called_once()

@patch('scripts.fetch_weather.dlt.pipeline')
@patch('scripts.fetch_weather.get_hourly_weather')
def test_main_pipeline(mock_get_weather, mock_pipeline):
    """"
    This test creates a mock dlt pipeline and its methods
    """
    # Mock weather data
    mock_get_weather.return_value = iter([{"time": "2025-04-26T12:00", "temperature_2m_°C": 20}])
    # Mock pipeline
    mock_pipeline_instance = MagicMock()
    mock_pipeline.return_value = mock_pipeline_instance
    mock_pipeline_instance.run.return_value = "load_info"
    mock_pipeline_instance.last_trace = "trace"

    from scripts.fetch_weather import main
    result = main()
    assert result == "load_info"
    mock_pipeline_instance.run.assert_called_once()
