import numpy as np
import pandas as pd
from typing import Optional, Tuple


class TrackBoundaryCalculator:
    def __init__(self, half_width: float = 13.5):
        self.half_width = half_width

    def compute_boundaries(self, df_center: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        x = df_center['WorldX'].to_numpy(dtype=np.float64)
        z = df_center['WorldZ'].to_numpy(dtype=np.float64)

        n_points = len(x)
        if n_points < 2:
            raise ValueError("Trajectory must have at least 2 points.")

        dx = np.zeros_like(x)
        dz = np.zeros_like(z)

        dx[1:-1] = (x[2:] - x[:-2]) / 2.0
        dz[1:-1] = (z[2:] - z[:-2]) / 2.0

        dx[0], dz[0] = x[1] - x[0], z[1] - z[0]
        dx[-1], dz[-1] = x[-1] - x[-2], z[-1] - z[-2]

        lengths = np.hypot(dx, dz)
        lengths = np.where(lengths == 0.0, 1.0, lengths)

        nx = -dz / lengths
        nz = dx / lengths

        df_left = pd.DataFrame({
            'WorldX': x + nx * self.half_width,
            'WorldZ': z + nz * self.half_width
        }, index=df_center.index)

        df_right = pd.DataFrame({
            'WorldX': x - nx * self.half_width,
            'WorldZ': z - nz * self.half_width
        }, index=df_center.index)

        return df_left, df_right

