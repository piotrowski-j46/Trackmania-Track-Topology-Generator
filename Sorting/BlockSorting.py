from typing import List,Tuple, Optional
from Sorting.GridGeometryLUT import GridGeometryLUT
import pandas as pd

class BlockSorting:

    CURVE_RADIUS = {
        'RoadTechCurve1': 1,
        'RoadTechCurve2': 2,
        'RoadTechCurve3': 3
    }

    @staticmethod
    def get_valid_target_positions(curr_x: float, curr_z: float, shifts: List[float]) -> List[Tuple[float, float]]:
        return [
            (curr_x + shifts[i], curr_z + shifts[i + 1])
            for i in range(0, len(shifts), 2)
        ]

    def evaluate_connection(self, curr_block: pd.Series, cand_block: pd.Series) -> bool:
        curr_name, curr_dir = curr_block['BlockName'], curr_block['Dir']
        cand_name, cand_dir = cand_block['BlockName'], cand_block['Dir']

        curr_pos = (curr_block['GridX'], curr_block['GridZ'])
        cand_pos = (cand_block['GridX'], cand_block['GridZ'])

        if curr_name in ('RoadTechStart', 'RoadTechStraight'):
            if cand_name == 'RoadTechStraight':
                if cand_dir in GridGeometryLUT.STRAIGHT_DIRS.get(curr_dir, set()):
                    shifts = GridGeometryLUT.STRAIGHT_SHIFT[curr_dir]
                    return cand_pos in self.get_valid_target_positions(*curr_pos, shifts)

            elif cand_name in self.CURVE_RADIUS:
                active_dir = curr_dir
                if curr_name == 'RoadTechStraight':
                    shifted_dir = list(GridGeometryLUT.SHIFTED_DIRS.get(curr_dir, {curr_dir}))[0]
                    if cand_dir in GridGeometryLUT.CURVE_DIRS.get(shifted_dir, set()):
                        active_dir = shifted_dir
                        curr_block['Dir'] = shifted_dir

                if cand_dir in GridGeometryLUT.CURVE_DIRS.get(active_dir, set()):
                    r = self.CURVE_RADIUS[cand_name]
                    shifts = GridGeometryLUT.CURVE_SHIFT[r][active_dir] if r == 1 else \
                        GridGeometryLUT.CURVE_SHIFT[r][active_dir][cand_dir]
                    return cand_pos in self.get_valid_target_positions(*curr_pos, shifts)

        elif curr_name in self.CURVE_RADIUS:
            from_r = self.CURVE_RADIUS[curr_name]

            if cand_name == 'RoadTechStraight':
                shifts = GridGeometryLUT.CURVE_TO_STRAIGHT[from_r][curr_dir][cand_dir]
                return cand_pos in self.get_valid_target_positions(*curr_pos, shifts)

            elif cand_name in self.CURVE_RADIUS:
                if cand_dir in GridGeometryLUT.CURVE_TO_CURVE_DIRS.get(curr_dir, set()):
                    to_r = self.CURVE_RADIUS[cand_name]
                    shifts = GridGeometryLUT.CURVE_TO_CURVE[from_r][to_r][curr_dir][cand_dir]
                    return cand_pos in self.get_valid_target_positions(*curr_pos, shifts)

        return False

    def get_sorted_df(self, df):
        center_x, center_z = df.loc[0, 'GridX'], df.loc[0, 'GridZ']
        df['GridX_Mirrored'] = center_x - (df['GridX'] - center_x)

        start_idx = df[df["BlockName"] == "RoadTechStart"].index[0]
        sorted_indices = [start_idx]

        remaining_df = df.drop(index=start_idx)
        current_block = df.loc[start_idx].copy()
        counter = 0

        while not remaining_df.empty:
            best_candidate_idx = None

            for idx, row in remaining_df.iterrows():
                if self.evaluate_connection(current_block, row.copy()):
                    best_candidate_idx = idx
                    break

            if best_candidate_idx is None:
                break

            sorted_indices.append(best_candidate_idx)
            current_block = remaining_df.loc[best_candidate_idx].copy()

            remaining_df.drop(index=best_candidate_idx, inplace=True)
            counter += 1

        sorted_df = df.loc[sorted_indices].reset_index(drop=True)

        finish_block = df[df['BlockName'] == 'RoadTechFinish']
        if not finish_block.empty:
            sorted_df.loc[len(sorted_df)] = finish_block.iloc[0]

        return sorted_df
