import duckdb

conn = duckdb.connect("weather_data.duckdb")

print(conn.execute("SELECT * FROM open_meteo_weather.hourly_weather").fetch_df())