import os
import datetime

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
