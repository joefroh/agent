import os
import datetime
import weather_utils


def list_files(path):
    """
    Lists all files and directories in the specified path.

    Args:
        path (str): The directory path to list contents from.

    Returns:
        list: A list of names of the entries in the given directory.

    Raises:
        FileNotFoundError: If the specified path does not exist.
        NotADirectoryError: If the specified path is not a directory.
        PermissionError: If there is no permission to access the specified path.
    """
    return os.listdir(path)


def get_now():
    """_summary_
    Gets the current machine time.

    Returns:
        string: the current machine time.
    """
    return datetime.datetime.now().__str__()


def get_forecast(long, lat, timezone):
    """_summary_

    Args:
        long (float): Longitude of the location.
        lat (float): Latitude of the location.
        timezone (timezone): Timezoen of the location - formatted like "America/Los_Angeles".

    Returns:
        DataFrame: 7 day forcast.
    """
    return weather_utils.get_forecast(long, lat, timezone)


def get_location(name):
    """_summary_
    Function that gets a list of locations for a given search name. The list includes longitude and latitude as well as other useful information.

    Args:
        name (string): The name of the location to find.

    Returns:
        list: A list of objects containing longitude, latitude, and other important information. In general, the first result is likely what people are searching for.
    """
    return weather_utils.get_location(name)
