import pandas as pd
import os
from typing import Tuple
import numpy as np

class TrackDataExporter:

    def __init__(self, base_dir: str = '~/TmrlData'):
        self.base_dir = os.path.expanduser(base_dir)
        self.track_info_dir = os.path.join(self.base_dir, 'track_info')
        os.makedirs(self.track_info_dir, exist_ok=True)

    def save_csv_dataset(self, df_center: pd.DataFrame, df_left: pd.DataFrame, df_right: pd.DataFrame) -> None:
        df_center.to_csv(os.path.join(self.track_info_dir, 'centerline.csv'))
        df_left.to_csv(os.path.join(self.track_info_dir, 'right_boundary.csv'))
        df_right.to_csv(os.path.join(self.track_info_dir, 'left_boundary.csv'))
        print(f"[Exporter] Successfully saved CSV to: {self.track_info_dir}")

    def load_reference_pkl(self, track_name: str = 'track_test-3') -> Tuple[np.ndarray, np.ndarray]:
        left_path = os.path.join(self.base_dir, f'{track_name}_left_.pkl')
        right_path = os.path.join(self.base_dir, f'{track_name}_right_.pkl')
        left_pkl = pd.read_pickle(left_path)
        right_pkl = pd.read_pickle(right_path)
        return left_pkl, right_pkl