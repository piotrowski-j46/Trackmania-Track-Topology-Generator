import os
import pandas as pd

def load_file(file_path):
    """
    Loads track from passed csv and returns pandas dataframe
    :param file_path:
    :return:
    loaded_df
    """
    path = os.path.expanduser(file_path)
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return None
    except pd.errors.ParserError as e:
        print(f"CSV parsing error: {e}")
        return None
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding = 'cp1250')

    return df