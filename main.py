import os
import argparse
import sys
from Topology.RoadPathBuilder import RoadPathBuilder
from Topology.TrackBoundaryCalculator import TrackBoundaryCalculator
from FileOperations.TrackDataExporter import TrackDataExporter
from Visualization.TrackVisualizer import TrackVisualizer
from FileOperations import FileLoader
from Sorting.BlockSorting import BlockSorting


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for the track processing pipeline.
    """
    parser = argparse.ArgumentParser(
        description="Track Processing Pipeline: Computes centerlines and track boundaries from grid blocks."
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        default="~/TmrlData/track/track_centerline.csv",
        help="Path to the input CSV track grid file."
    )

    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="~/TmrlData",
        help="Base directory for exporting processed track boundaries."
    )

    parser.add_argument(
        "--dir", "-d",
        type=str,
        choices=["north", "south", "east", "west"],
        default="north",
        help="Initial orientation of the start block."
    )

    parser.add_argument(
        "--half-width", "-w",
        type=float,
        default=13.5,
        help="Half-width of the track in world units."
    )

    parser.add_argument(
        "--visualize", "-v",
        action="store_true",
        help="Enable Matplotlib rendering to inspect calculated track shape and boundaries."
    )

    parser.add_argument(
        "--verify-pkl",
        action="store_true",
        help="Proof of Concept: Overlay recorded verification .pkl boundaries against calculated lines (requires --visualize)."
    )

    parser.add_argument(
        "--ref-name", "-r",
        type=str,
        default="track_test-3",
        help="Reference track name used when loading verification .pkl files with --verify-pkl."
    )

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    input_path = os.path.expanduser(args.input)
    print(f"[Info] Loading track grid from: {input_path}")

    try:
        loaded_df = FileLoader.load_file(input_path)
        print(f"{len(loaded_df)}")
    except Exception as e:
        print(f"[Error] Failed to load input file: {e}", file=sys.stderr)
        sys.exit(1)

    print("[Info] Sorting track blocks topology...")
    bs = BlockSorting()
    sorted_df = bs.get_sorted_df(loaded_df)

    print(f"[Info] Building continuous centerline trajectory (Initial direction: {args.dir.upper()})...")
    road_builder = RoadPathBuilder()
    df_cont = road_builder.build_path(sorted_df, initial_dir=args.dir)

    print(f"[Info] Computing track boundaries (Half-width: {args.half_width})...")
    calc = TrackBoundaryCalculator(half_width=args.half_width)
    df_left, df_right = calc.compute_boundaries(df_cont)

    print(f"[Info] Exporting calculated CSV datasets to: {os.path.expanduser(args.output_dir)}")
    exporter = TrackDataExporter(base_dir=args.output_dir)
    exporter.save_csv_dataset(df_center=df_cont, df_left=df_left, df_right=df_right)

    print("[Success] Pipeline execution finished successfully.")

    if args.visualize:
        print("[Info] Visualization flag detected. Initializing render engine...")
        viz = TrackVisualizer(figsize=(14, 10))

        # 1. Mode 1: Render base calculated track shape and boundaries
        print("[Info] Plotting calculated trajectory and boundaries...")
        viz.plot_trajectory(df_left, label='Right boundary (Calc)', color='red', linewidth=1.5)
        viz.plot_trajectory(df_right, label='Left boundary (Calc)', color='purple', linewidth=1.5)

        # 2. Mode 2 (PoC): Validation against recorded PKL files
        if args.verify_pkl:
            print(f"[Info] [PoC] Loading verification PKL files for reference track: {args.ref_name}")
            try:
                left_bound_pkl, right_bound_pkl = exporter.load_reference_pkl(track_name=args.ref_name)
                if left_bound_pkl is not None and right_bound_pkl is not None:
                    viz.plot_raw_matrix(left_bound_pkl, x_col=0, z_col=2, label='Left boundary (Record)', color='green', linewidth=1.0)
                    viz.plot_raw_matrix(right_bound_pkl, x_col=0, z_col=2, label='Right boundary (Record)', color='blue', linewidth=1.0)
                    print("[Success] Reference PKL boundaries overlaid successfully.")
            except Exception as e:
                print(f"[Warning] Could not load reference PKL files ({e}). Skipping PoC validation lines.")

        viz.render(title=f"Track Trajectory Visualization ({args.ref_name})")

if __name__ == "__main__":
    main()