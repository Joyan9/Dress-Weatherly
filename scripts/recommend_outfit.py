# scripts/recommend_outfit.py

import duckdb
import pandas as pd
from datetime import datetime

class OutfitRecommender:
    def __init__(self, db_path="weather_data.duckdb"):
        self.conn = duckdb.connect(db_path)
    
    def get_weather_data(self, date=None):
        """
        Retreives the weather data for specified date or for today by default
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

            query = f""" 
                    SELECT * FROM open_meteo_weather.hourly_weather
                    WHERE time >= '{date} 00:00:00' AND time < '{date} 23:00:00'
                    ORDER BY time
                    """
            
            try:
                weather_data_df = self.conn.execute(query).fetch_df()
                if weather_data_df.empty:
                    return None # no data available
                
                return weather_data_df
            
            except Exception as e:
                print(f"Error fetching data due to error: {e}")
                return None
            

    def get_outfit_recommendation(self, date=None):
        weather_data = self.get_weather_data(date)

        if weather_data is None:
            return "No Weather data available for specified date"
        
        date = weather_data["time"].max().strftime('%Y-%m-%d')
        max_temp = weather_data["temperature_2m_c"].max()
        min_temp = weather_data["temperature_2m_c"].min()
        
        avg_temp = weather_data["temperature_2m_c"].mean()

        max_apparent_temp  = weather_data["apparent_temperature_c"].max()
        min_apparent_temp  = weather_data["apparent_temperature_c"].min()
        
        # Precipitation analysis
        will_rain = (weather_data['precipitation_mm'] > 0.2).any()
        heavy_rain = (weather_data['precipitation_mm'] > 5).any()
        
        # Wind analysis
        max_wind = weather_data['wind_speed_10m_km_h'].max()
        strong_wind = max_wind > 30
    
        # Generate recommendations
        upper_body = self._recommend_upper_body(max_temp, min_temp, max_apparent_temp)
        lower_body = self._recommend_lower_body(min_temp)
        outerwear = self._recommend_outerwear(min_apparent_temp, strong_wind)
        accessories = self._recommend_accessories(will_rain, heavy_rain, max_temp, min_temp, strong_wind)
        
        # Format recommendations
        recommendation = f"""
                Weather Summary for {date}:
            - Temperature range: {min_temp:.1f}°C to {max_temp:.1f}°C
            - Feels like: {min_apparent_temp:.1f}°C to {max_apparent_temp:.1f}°C
            - {'Rain expected' if will_rain else 'No rain expected'}
            - {'Strong winds' if strong_wind else 'Mild winds'}

            Outfit Recommendation:
            - Upper body: {upper_body}
            {f'- Outerwear & Jackets: {outerwear}' if outerwear else ''}
            - Lower body: {lower_body}
            {f'- Accessories: {accessories}' if accessories else ''}
                """
    
        return recommendation.strip()
    
    def _recommend_upper_body(self, max_temp, min_temp, max_apparent_temp):
            """Recommend first layer of upper body clothing based on temperature"""
            if max_temp >= 30:
                return "Light, breathable t-shirt or tank top"
            elif max_temp >= 25:
                return "T-shirt or short-sleeve shirt"
            elif max_temp >= 20:
                return "T-shirt or light long-sleeve shirt"
            elif max_temp >= 15:
                return "Long-sleeve shirt or light sweater"
            elif max_temp >= 10:
                return "Sweater or light thermal top"
            else:
                return "Thermal top with sweater layering"
        
    def _recommend_lower_body(self, min_temp):
        """Recommend lower body clothing based on temperature"""
        if min_temp >= 25:
            return "Shorts/skirt, breathable pants"
        elif min_temp >= 20:
            return "Shorts/skirt, or light pants"
        elif min_temp >= 15:
            return "Light pants or jeans"
        elif min_temp >= 5:
            return "Jeans or any thick pants with a thermal inner"
        else:
            return "Warm pants or thermal layer under pants"
        
    def _recommend_outerwear(self, min_apparent_temp, strong_wind):
        """Recommend second layer of upper body clothing based on apparent temperature and wind"""
        if min_apparent_temp >= 25:
            return None  # No outerwear needed
        elif min_apparent_temp >= 20: 
            return "Light cardigan or thin jacket" + (" (wind resistant preferred)" if strong_wind else "")
        elif min_apparent_temp >= 15:
            return "Light jacket" + (" with wind protection" if strong_wind else "")
        elif min_apparent_temp >= 10:
            return "Medium-weight jacket" + (" with good wind protection" if strong_wind else "")
        elif min_apparent_temp >= 5:
            return "Heavy jacket or coat, multiple layers advisable"
        else:
            return "Heavy winter coat with proper insulation, multiple layers advisable"
    
    def _recommend_accessories(self, will_rain, heavy_rain, max_temp, min_temp, strong_wind):
        """Recommend accessories such as umbrella, raincoat etc. based on weather conditions"""
        accessories = []
        
        if will_rain:
            if heavy_rain:
                accessories.append("Waterproof rain jacket and umbrella")
            else:
                accessories.append("Umbrella or light raincoat")
        
        if min_temp < 10:
            accessories.append("Hat")
        
        if min_temp < 5:
            accessories.append("Gloves")
            
        if min_temp < 0:
            accessories.append("Scarf")
            
        if max_temp > 25 and not will_rain:
            accessories.append("Sunglasses and sunscreen")
            
        if strong_wind and not will_rain:
            accessories.append("Wind-resistant layer")
            
        return ", ".join(accessories) if accessories else None
    

    def close(self):
        """Close the database connection"""
        self.conn.close()


if __name__ == "__main__":
    recommender = OutfitRecommender()
    # Get recommendation for today
    today_recommendation = recommender.get_outfit_recommendation()
    print(today_recommendation)
    
    recommender.close()

    
        