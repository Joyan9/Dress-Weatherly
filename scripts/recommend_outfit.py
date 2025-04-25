# scripts/recommend_outfit.py
#!/usr/bin/env python3
import duckdb
import pandas as pd
import logging
from datetime import datetime


class OutfitRecommender:
    def __init__(self, db_path: str = "weather_data.duckdb"):
        # Configure logger for this module
        self.logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Connect to DuckDB
        try:
            self.conn = duckdb.connect(db_path)
            self.logger.info(f"Connected to DuckDB at {db_path}")
        except Exception as e:
            self.logger.error("Failed to connect to DuckDB", exc_info=True)
            raise

    def get_weather_data(self, date: str = None) -> pd.DataFrame:
        """
        Retrieves hourly weather data for a given date (YYYY-MM-DD).
        If no date is provided, defaults to today.
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        query = f"""
            SELECT *
            FROM open_meteo_weather.hourly_weather
            WHERE time >= '{date} 00:00:00'
              AND time <  '{date} 23:59:59'
            ORDER BY time
        """
        try:
            df = self.conn.execute(query).fetch_df()
        except Exception as e:
            self.logger.error(f"Error querying weather data for {date}", exc_info=True)
            return None

        if df.empty:
            self.logger.warning(f"No weather data found for {date}")
            return None

        # Ensuring 'time' is datetime
        df['time'] = pd.to_datetime(df['time'])
        return df

    def _split_by_period(self, df: pd.DataFrame) -> dict:
        """
        Splits the day's DataFrame into three periods:
        - Morning:   6–10
        - Daytime:  10–18
        - Evening:  18–24 and early morning 0–6
        Returns a dict mapping period names to DataFrames.
        """
        df = df.copy()
        df['hour'] = df['time'].dt.hour
        periods = {
            'Morning (06–10)': df[(df.hour >= 6) & (df.hour < 10)],
            'Daytime (10–18)': df[(df.hour >= 10) & (df.hour < 18)],
            'Evening (18–24 & 00–06)': df[
                ((df.hour >= 18) & (df.hour < 24)) |
                ((df.hour >= 0) & (df.hour < 6))
            ],
        }
        return periods

    def get_outfit_recommendation(self, date: str = None) -> str:
        """
        Generates a weather summary and outfit recommendation broken down by time-of-day periods.
        If weather data cannot be fetched, returns the error message.
        """
        df = self.get_weather_data(date)
        
        if df is None:
          return "No weather data available for specified date"
          
        # Overall weather summary
        header_date = df['time'].dt.date.max().isoformat()
        overall_max_temp = df['temperature_2m_c'].max()
        overall_min_temp = df['temperature_2m_c'].min()
        overall_max_app = df['apparent_temperature_c'].max()
        overall_min_app = df['apparent_temperature_c'].min()
        will_rain = (df['precipitation_mm'] > 0.2).any()
        strong_wind = df['wind_speed_10m_km_h'].max() > 30

        summary_lines = [
            f"Weather Summary for {header_date}:",
            f" - Temperature range: {overall_min_temp:.1f}°C to {overall_max_temp:.1f}°C",
            f" - Feels like: {overall_min_app:.1f}°C to {overall_max_app:.1f}°C",
            f" - {'Rain expected' if will_rain else 'No rain expected'}",
            f" - {'Strong winds' if strong_wind else 'Mild winds'}"
        ]
        summary = "\n".join(summary_lines)

        # Time-of-day recommendations
        periods = self._split_by_period(df)
        recommendations = [summary, ""]
        for period_name, subdf in periods.items():
            if subdf.empty:
                self.logger.info(f"Skipping {period_name}: no data")
                recommendations.append(f"{period_name}: No data available")
            else:
                rec = self._build_recommendation(subdf)
                recommendations.append(f"{period_name}:\n{rec}")

        return "\n\n".join(recommendations)

    def _build_recommendation(self, weather_df: pd.DataFrame) -> str:
        """
        Builds a recommendation string for a given subset of hourly weather data.
        """
        # Calculate weather stats
        max_temp = weather_df['temperature_2m_c'].max()
        min_temp = weather_df['temperature_2m_c'].min()
        avg_temp = weather_df['temperature_2m_c'].mean()
        max_app = weather_df['apparent_temperature_c'].max()
        min_app = weather_df['apparent_temperature_c'].min()
        will_rain = (weather_df['precipitation_mm'] > 0.2).any()
        heavy_rain = (weather_df['precipitation_mm'] > 5).any()
        max_wind = weather_df['wind_speed_10m_km_h'].max()
        strong_wind = max_wind > 30

        # Layer recommendations
        base = self._recommend_base_layer(max_temp, min_temp)
        mid = self._recommend_mid_layer(avg_temp)
        outer = self._recommend_outer_layer(min_app, strong_wind)
        lower = self._recommend_lower_body(min_temp)
        accessories = self._recommend_accessories(
            will_rain, heavy_rain, max_temp, min_temp, strong_wind
        )

        # Format output
        lines = [
            f"• Temp: {min_temp:.1f}–{max_temp:.1f}°C (feels like {min_app:.1f}–{max_app:.1f}°C)",
            f"• Base layer: {base}",
        ]
        if mid:
            lines.append(f"• Mid layer: {mid}")
        if outer:
            lines.append(f"• Outer layer: {outer}")
        lines.append(f"• Lower body: {lower}")
        if accessories:
            lines.append(f"• Accessories: {accessories}")

        return "\n".join(lines)

    def _recommend_base_layer(self, max_temp: float, min_temp: float) -> str:
        """
        Recommend a base layer (first layer) based on temperature extremes.
        """
        if max_temp >= 30:
            return "Light, breathable tee or tank"
        if max_temp >= 25:
            return "Short-sleeve shirt"
        if max_temp >= 20:
            return "Long-sleeve shirt or light tee"
        if max_temp >= 15:
            return "Light sweater or thermal top"
        if max_temp >= 10:
            return "Sweater or fleece top"
        return "Thermal base layer"

    def _recommend_mid_layer(self, avg_temp: float) -> str:
        """
        Recommend a mid layer (e.g., sweater) when average temperature is cool.
        """
        if avg_temp >= 20:
            return None
        if avg_temp >= 15:
            return "Light sweater or fleece"
        if avg_temp >= 10:
            return "Medium sweater or hoodie"
        return "Heavy sweater or insulated mid-layer"

    def _recommend_outer_layer(self, min_apparent_temp: float, strong_wind: bool) -> str:
        """
        Recommend an outer layer (jacket/coating) based on feels-like temp & wind.
        """
        needs_wind = " with wind protection" if strong_wind else ""
        if min_apparent_temp >= 20:
            return None
        if min_apparent_temp >= 15:
            return f"Light jacket{needs_wind}"
        if min_apparent_temp >= 10:
            return f"Medium jacket or windbreaker{needs_wind}"
        if min_apparent_temp >= 5:
            return f"Heavy coat or insulated jacket{needs_wind}"
        return f"Winter coat with insulation and windproof shell{needs_wind}"

    def _recommend_lower_body(self, min_temp: float) -> str:
        """
        Recommend lower body wear based on minimum temperature.
        """
        if min_temp >= 25:
            return "Shorts or breathable pants"
        if min_temp >= 20:
            return "Light pants or skirt"
        if min_temp >= 15:
            return "Jeans or chinos"
        if min_temp >= 5:
            return "Thick pants or jeans with thermal lining"
        return "Thermal leggings under pants or insulated trousers"

    def _recommend_accessories(
        self,
        will_rain: bool,
        heavy_rain: bool,
        max_temp: float,
        min_temp: float,
        strong_wind: bool
    ) -> str:
        """
        Recommend accessories like umbrella, hat, gloves, etc.
        """
        items = []
        if will_rain:
            items.append(
                "Waterproof rain jacket and umbrella" if heavy_rain else "Umbrella or light raincoat"
            )
        if min_temp < 10:
            items.append("Hat")
        if min_temp < 5:
            items.append("Gloves")
        if min_temp < 0:
            items.append("Scarf")
        if max_temp > 25 and not will_rain:
            items.append("Sunglasses and sunscreen")
        if strong_wind and not will_rain:
            items.append("Wind-resistant layer")
        return ", ".join(items) if items else None

    def close(self):
        """Close the DuckDB connection."""
        try:
            self.conn.close()
            self.logger.info("DuckDB connection closed")
        except Exception:
            self.logger.warning("Error closing DuckDB connection", exc_info=True)


if __name__ == "__main__":
    # Configure root logger
    logging.basicConfig(level=logging.INFO)

    recommender = OutfitRecommender()
    try:
        print(recommender.get_outfit_recommendation())
    finally:
        recommender.close()