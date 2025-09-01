import openmeteo_requests

import pandas as pd
import requests_cache
import requests
from retry_requests import retry

def get_forecast(long, lat, timezone):
    """_summary_

    Args:
        long (float): Longitude of the location.
        lat (float): Latitude of the location.
        timezone (timezone): Timezoen of the location - formatted like "America/Los_Angeles".

    Returns:
        DataFrame: 7 day forcast.
    """
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "timezone": timezone
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min

    daily_dataframe = pd.DataFrame(data = daily_data)
    print("\nDaily data\n", daily_dataframe)

    return daily_dataframe

def get_location(name):
    # reference: https://open-meteo.com/en/docs/geocoding-api

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": name
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['results']
    else:
        raise RuntimeError
