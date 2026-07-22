import numpy as np
import pandas as pd
from typing import Dict, Tuple, List


class RoadPathBuilder:

    _DIAGONAL_LEN: Dict[str, float] = {
        'RoadTechCurve1': 0.68,
        'RoadTechCurve2': 2.125,
        'RoadTechCurve3': 3.52
    }

    _MULTIPLIER: Dict[str, int] = {
        'RoadTechCurve1': 3,
        'RoadTechCurve2': 4,
        'RoadTechCurve3': 5
    }

    _BEZIER_LUT: Dict[str, Dict[str, Dict[Tuple[int, int], List[float]]]] = {
        'RoadTechCurve1': {
            'north': {(0, 2): [np.pi / 4, np.pi / 2, 0, 7], (3, 1): [3 * np.pi / 4, np.pi / 2, np.pi, 7],
                      (0, 1): [3 * np.pi / 4, np.pi / 2, np.pi, 7], (3, 2): [np.pi / 4, np.pi / 2, 0, 7]},
            'west': {(1, 2): [5 * np.pi / 4, np.pi, 3 * np.pi / 2, 7], (0, 3): [3 * np.pi / 4, np.pi, np.pi / 2, 7],
                     (1, 3): [3 * np.pi / 4, np.pi, np.pi / 2, 7]},
            'south': {(2, 0): [5 * np.pi / 4, 3 * np.pi / 2, np.pi, 7], (1, 3): [7 * np.pi / 4, 3 * np.pi / 2, 0, 7],
                      (1, 0): [5 * np.pi / 4, 3 * np.pi / 2, np.pi, 7]},
            'east': {(2, 1): [7 * np.pi / 4, 0, 3 * np.pi / 2, 7], (3, 1): [7 * np.pi / 4, 0, 3 * np.pi / 2, 7],
                     (2, 0): [np.pi / 4, 0, np.pi / 2, 7]}
        },
        'RoadTechCurve2': {
            'north': {(3, 1): [3 * np.pi / 4, np.pi / 2, np.pi, 24]},
            'west': {(1, 3): [3 * np.pi / 4, np.pi, np.pi / 2, 24], (3, 2): [5 * np.pi / 4, np.pi, 3 * np.pi / 2, 24]},
            'south': {(1, 3): [7 * np.pi / 4, 3 * np.pi / 2, 0, 24]},
            'east': {(3, 1): [7 * np.pi / 4, 0, 3 * np.pi / 2, 24], (3, 0): [np.pi / 4, 0, np.pi / 2, 24]}
        },
        'RoadTechCurve3': {
            'north': {(0, 1): [3 * np.pi / 4, np.pi / 2, np.pi, 44], (3, 1): [3 * np.pi / 4, np.pi / 2, np.pi, 44]},
            'west': {(0, 3): [3 * np.pi / 4, np.pi, np.pi / 2, 44]},
            'south': {(1, 3): [7 * np.pi / 4, 3 * np.pi / 2, 0, 44], (2, 3): [7 * np.pi / 4, 3 * np.pi / 2, 0, 44],
                      (0, 0): [5 * np.pi / 4, 3 * np.pi / 2, np.pi, 44]},
            'east': {(3, 0): [np.pi / 4, 0, np.pi / 2, 44], (2, 3): [3 * np.pi / 2, 3 * np.pi / 2, np.pi, 44]}
        }
    }

    _DIR_LUT: Dict[str, Dict[Tuple[int, int], str]] = {
        'north': {(0, 2): 'east', (0, 1): 'west', (3, 1): 'west', (3, 2): 'east'},
        'west': {(1, 3): 'north', (1, 2): 'south', (0, 3): 'north', (3, 2): 'south'},
        'south': {(1, 3): 'east', (2, 0): 'west', (2, 3): 'east', (0, 0): 'west', (1, 0): 'west'},
        'east': {(2, 1): 'south', (3, 1): 'south', (1, 3): 'west', (3, 0): 'north', (2, 0): 'north'}
    }

    def __init__(self, grid_size: float = 32.0, straight_points: int = 64):
        self.grid_size = grid_size
        self.straight_points = straight_points
        self.pos = np.zeros(2, dtype=np.float64)  # [WorldX, WorldZ]
        self.heading = 0.0
        self.current_dir = 'north'
        self.dir_in = 0

    @staticmethod
    def _eval_cubic_bezier(P0: np.ndarray, P1: np.ndarray, P2: np.ndarray, P3: np.ndarray,
                           num_points: int) -> np.ndarray:
        t = np.linspace(0.0, 1.0, num_points, dtype=np.float64)[:, np.newaxis]  # Kształt: (N, 1)
        u = 1.0 - t
        return (u ** 3) * P0 + (3 * u ** 2 * t) * P1 + (3 * u * t ** 2) * P2 + (t ** 3) * P3

    @staticmethod
    def _eval_straight_line(start_pos: np.ndarray, heading: float, length: float, num_points: int) -> np.ndarray:
        t = np.linspace(0.0, length, num_points, endpoint=False, dtype=np.float64)[:, np.newaxis]
        direction = np.array([np.cos(heading), np.sin(heading)], dtype=np.float64)
        return start_pos + t * direction

    def _init_state(self, df: pd.DataFrame) -> None:
        if len(df) > 1:
            dx = df.iloc[1]['GridX_Mirrored'] - df.iloc[0]['GridX_Mirrored']
            dz = df.iloc[1]['GridZ'] - df.iloc[0]['GridZ']
            self.heading = np.round(np.arctan2(dz, dx) / (np.pi / 2)) * (np.pi / 2)
        else:
            self.heading = np.pi / 2

        start_cx = (df.iloc[0]['GridX_Mirrored'] * self.grid_size) + 14.5
        start_cz = (df.iloc[0]['GridZ'] * self.grid_size) + 20.0

        self.pos[0] = start_cx - (self.grid_size / 2.0) * np.cos(self.heading)
        self.pos[1] = start_cz - (self.grid_size / 2.0) * np.sin(self.heading)
        self.dir_in = df.iloc[0]['Dir']

    def build_path(self, sorted_df: pd.DataFrame, initial_dir: str = 'north') -> pd.DataFrame:
        self.current_dir = initial_dir
        self._init_state(sorted_df)

        path_chunks: List[np.ndarray] = []

        for row in sorted_df.itertuples(index=False):
            block_name = row.BlockName

            if block_name in ('RoadTechStart', 'RoadTechStraight', 'RoadTechFinish'):
                points = self._eval_straight_line(self.pos, self.heading, self.grid_size, self.straight_points)
                path_chunks.append(points)

                self.pos += self.grid_size * np.array([np.cos(self.heading), np.sin(self.heading)])

            elif block_name.startswith('RoadTechCurve'):
                dir_out = row.Dir
                params = self._BEZIER_LUT[block_name][self.current_dir][(self.dir_in, dir_out)]
                diag_heading, heading_in, heading_out, w = params
                diag_len = self._DIAGONAL_LEN[block_name]

                P0 = self.pos.copy()
                P3 = P0 + self.grid_size * diag_len * np.array([np.cos(diag_heading), np.sin(diag_heading)])
                P1 = P0 + w * np.array([np.cos(heading_in), np.sin(heading_in)])
                P2 = P3 - w * np.array([np.cos(heading_out), np.sin(heading_out)])

                num_pts = int(self.grid_size * self._MULTIPLIER[block_name])
                curve_points = self._eval_cubic_bezier(P0, P1, P2, P3, num_pts)
                path_chunks.append(curve_points)

                self.pos = P3
                self.heading = heading_out
                self.current_dir = self._DIR_LUT[self.current_dir][(self.dir_in, dir_out)]

            self.dir_in = row.Dir

        full_mesh = np.vstack(path_chunks)
        return pd.DataFrame(full_mesh, columns=['WorldX', 'WorldZ'])
