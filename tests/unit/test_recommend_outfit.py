from unittest.mock import MagicMock, patch
import pytest
import pandas as pd
from scripts.recommend_outfit import OutfitRecommender

@pytest.fixture
def mock_duckdb_connection():
    """
    Fixture to mock the DuckDB connection and execute method.
    """
    mock_conn = MagicMock()
    mock_execute = MagicMock()
    mock_conn.execute = mock_execute
    return mock_conn

@patch('scripts.recommend_outfit.duckdb.connect')
def test_init_success(mock_connect, mock_duckdb_connection):
    """
    Test successful initialization of OutfitRecommender's __init__ method with a mocked DuckDB connection.
    """
    mock_connect.return_value = mock_duckdb_connection
    recommender = OutfitRecommender(db_path="test.duckdb")
    assert recommender.conn == mock_duckdb_connection
    mock_connect.assert_called_once_with("test.duckdb")


@patch('scripts.recommend_outfit.duckdb.connect')
def test_init_failure(mock_connect):
    """
    Test that OutfitRecommender raises an exception if the DuckDB connection fails.
    """
    mock_connect.side_effect = Exception("Connection failed")
    with pytest.raises(Exception, match="Connection failed"):
        OutfitRecommender(db_path="test.duckdb")

@patch('scripts.recommend_outfit.duckdb.connect')
def test_get_weather_data_success(mock_connect, mock_duckdb_connection):
    """
    Test successful retrieval of weather data.
    """
    mock_connect.return_value = mock_duckdb_connection
    mock_execute = mock_duckdb_connection.execute
    mock_execute.return_value.fetch_df.return_value = pd.DataFrame({
        'time': ['2025-04-26 00:00:00'],
        'temperature_2m_c': [20]
    })
    recommender = OutfitRecommender(db_path="test.duckdb")
    df = recommender.get_weather_data(date='2025-04-26')
    assert not df.empty
    assert 'temperature_2m_c' in df.columns
    mock_execute.assert_called_once()  # Check if query was executed


@patch('scripts.recommend_outfit.duckdb.connect')
def test_get_weather_data_empty(mock_connect, mock_duckdb_connection):
    """
    Test when no weather data is found.
    """
    mock_connect.return_value = mock_duckdb_connection
    mock_execute = mock_duckdb_connection.execute
    mock_execute.return_value.fetch_df.return_value = pd.DataFrame()  # Empty DataFrame

    recommender = OutfitRecommender(db_path="test.duckdb")
    df = recommender.get_weather_data(date='2025-04-26')
    assert df is None  # Expect None when DataFrame is empty


@patch('scripts.recommend_outfit.duckdb.connect')
def test_get_weather_data_error(mock_connect, mock_duckdb_connection):
    """
    Test error handling when querying weather data.
    """
    mock_connect.return_value = mock_duckdb_connection
    mock_execute = mock_duckdb_connection.execute
    mock_execute.side_effect = Exception("Query failed")  # Simulate query failure

    recommender = OutfitRecommender(db_path="test.duckdb")
    df = recommender.get_weather_data(date='2025-04-26')
    assert df is None  # Expect None when there is an error

def test_split_by_period():
    """
    Test the _split_by_period method.
    """
    data = {
        'time': pd.to_datetime(['2025-04-26 07:00:00', '2025-04-26 12:00:00', '2025-04-26 20:00:00']),
        'temperature_2m_c': [15, 20, 10]
    }
    df = pd.DataFrame(data)
    recommender = OutfitRecommender()  # No DB needed for this test
    periods = recommender._split_by_period(df)

    assert 'Morning (06–10)' in periods
    assert 'Daytime (10–18)' in periods
    assert 'Evening (18–24 & 00–06)' in periods
    assert len(periods['Morning (06–10)']) == 1
    assert len(periods['Daytime (10–18)']) == 1
    assert len(periods['Evening (18–24 & 00–06)']) == 1


@patch('scripts.recommend_outfit.OutfitRecommender.get_weather_data')
def test_get_outfit_recommendation_success(mock_get_weather_data):
    """
    Test successful generation of outfit recommendation.
    """
    # Mock data for a sunny day
    mock_df = pd.DataFrame({
        'time': pd.to_datetime(['2025-04-26 12:00:00']),
        'temperature_2m_c': [25],
        'apparent_temperature_c': [25],
        'precipitation_mm': [0],
        'wind_speed_10m_km_h': [10]
    })
    mock_get_weather_data.return_value = mock_df

    recommender = OutfitRecommender()
    recommendation = recommender.get_outfit_recommendation(date='2025-04-26')

    assert "Weather Summary" in recommendation
    assert "Short-sleeve shirt" in recommendation
    assert "Shorts or light pants" in recommendation 

@patch('scripts.recommend_outfit.OutfitRecommender.get_weather_data')
def test_get_outfit_recommendation_no_data(mock_get_weather_data):
    """
    Test handling when no weather data is available.
    """
    mock_get_weather_data.return_value = None  # Simulate no data available

    recommender = OutfitRecommender()
    recommendation = recommender.get_outfit_recommendation(date='2025-04-26')

    assert recommendation == "No weather data available for specified date"

@patch('scripts.recommend_outfit.duckdb.connect')
def test_close(mock_connect, mock_duckdb_connection):
    """
    Test that the DuckDB connection is closed properly.
    """
    mock_connect.return_value = mock_duckdb_connection
    recommender = OutfitRecommender(db_path="test.duckdb")
    recommender.close()
    mock_duckdb_connection.close.assert_called_once()
