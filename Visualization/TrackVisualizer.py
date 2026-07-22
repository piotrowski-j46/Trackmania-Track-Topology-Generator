import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from typing import Optional, Tuple


class TrackVisualizer:
    def __init__(self, figsize: Tuple[int, int] = (14, 10)):
        self.figsize = figsize
        self.fig, self.ax = plt.subplots(figsize=self.figsize)

    def plot_trajectory(self, df: pd.DataFrame, label: str, color: str, linewidth: float = 1.0,
                        offset_x: float = 0.0, offset_z: float = 0.0) -> None:
        self.ax.plot(
            df['WorldX'].to_numpy() + offset_x,
            df['WorldZ'].to_numpy() + offset_z,
            color=color, linewidth=linewidth, label=label,
            antialiased=False, snap=True, solid_capstyle='butt'
        )

    def plot_raw_matrix(self, matrix: np.ndarray, x_col: int, z_col: int, label: str, color: str,
                        linewidth: float = 1.0) -> None:
        self.ax.plot(
            matrix[:, x_col], matrix[:, z_col],
            color=color, linewidth=linewidth, label=label,
            antialiased=False, snap=True, solid_capstyle='butt'
        )

    def plot_pivots(self, sorted_df: pd.DataFrame, grid_size: float = 32.0) -> None:
        self.ax.scatter(
            sorted_df['GridX_Mirrored'] * grid_size,
            sorted_df['GridZ'] * grid_size,
            color='gray', s=40, alpha=0.5, label='Pivots (Gridx32)', zorder=1
        )

    def render(self, title: str = "Centerline vs actual track", equal_aspect: bool = True) -> None:
        self.ax.set_title(title)
        self.ax.set_xlabel("World X")
        self.ax.set_ylabel("World Z")
        if equal_aspect:
            self.ax.axis('equal')
        self.ax.legend()
        plt.show()


