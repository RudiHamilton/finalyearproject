"""
generator.py
Synthetic dataset generator for delivery route optimisation.
Generates random geographic coordinates and computes pairwise distance matrices.
"""

import json
import math
import random
import os
from datetime import datetime , timezone
from optimisation.distance_matrix import build_distance_matrix


# --- Bounding box: Northern Ireland / UK region ---
DEFAULT_BOUNDS = {
    "lat_min": 54.0,
    "lat_max": 55.3,
    "lng_min": -8.2,
    "lng_max": -5.4,
}

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "datasets")

def generate_coordinates(n: int, bounds: dict, seed: int = None) -> list:
    """
    Generate n random geographic coordinate pairs within a bounding box.

    Args:
        n:      Number of locations to generate
        bounds: Dict with lat_min, lat_max, lng_min, lng_max
        seed:   Random seed for reproducibility (optional)

    Returns:
        List of dicts: [{"id": 0, "lat": ..., "lng": ...}, ...]
    """
    if seed is not None:
        random.seed(seed)

    coordinates = []
    for i in range(n):
        lat = round(random.uniform(bounds["lat_min"], bounds["lat_max"]), 6)
        lng = round(random.uniform(bounds["lng_min"], bounds["lng_max"]), 6)
        coordinates.append({"id": i, "lat": lat, "lng": lng})

    return coordinates


def generate_dataset(
    n: int = 10,
    seed: int = None,
    bounds: dict = None,
    save: bool = True,
    filename: str = None,
) -> dict:
    """
    Generate a complete routing dataset including coordinates and distance matrix.

    Args:
        n:        Number of delivery locations (5–25 recommended)
        seed:     Random seed for reproducibility
        bounds:   Geographic bounding box (defaults to Northern Ireland / UK)
        save:     Whether to write the dataset to data/datasets/ as JSON
        filename: Custom filename (auto-generated if None)

    Returns:
        Dataset dict with keys: num_locations, seed, coordinates, distance_matrix, generated_at
    """
    if n < 2:
        raise ValueError("Need at least 2 locations to generate a routing dataset.")
    if n > 25:
        raise ValueError("Maximum supported locations is 25 (API and model constraints).")

    if bounds is None:
        bounds = DEFAULT_BOUNDS

    # Use a random seed if none provided, but store it so the dataset is reproducible
    if seed is None:
        seed = random.randint(0, 999999)

    coordinates = generate_coordinates(n, bounds, seed)
    distance_matrix = build_distance_matrix(coordinates)

    dataset = {
        "num_locations": n,
        "seed": seed,
        "bounds": bounds,
        "coordinates": coordinates,
        "distance_matrix": distance_matrix,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if save:
        _save_dataset(dataset, filename)

    return dataset


def _save_dataset(dataset: dict, filename: str = None) -> str:
    """
    Save a dataset to data/datasets/ as a JSON file.

    Args:
        dataset:  The dataset dict to save
        filename: Optional custom filename (without extension)

    Returns:
        Full path to the saved file
    """
    os.makedirs(DATASETS_DIR, exist_ok=True)

    if filename is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"dataset_n{dataset['num_locations']}_seed{dataset['seed']}_{timestamp}"

    filepath = os.path.join(DATASETS_DIR, f"{filename}.json")

    with open(filepath, "w") as f:
        json.dump(dataset, f, indent=2)

    print(f"[generator] Saved dataset → {filepath}")
    return filepath


def load_dataset(filepath: str) -> dict:
    """
    Load a previously saved dataset from a JSON file.

    Args:
        filepath: Path to the JSON dataset file

    Returns:
        Dataset dict
    """
    with open(filepath, "r") as f:
        return json.load(f)


def batch_generate(sizes: list, seeds: list = None, save: bool = True) -> list:
    """
    Generate multiple datasets at once — useful for creating a training corpus.

    Args:
        sizes: List of n values, e.g. [5, 10, 15, 20, 25]
        seeds: Optional list of seeds (one per size). Random if not provided.
        save:  Whether to save each dataset to disk

    Returns:
        List of dataset dicts
    """
    datasets = []
    for i, n in enumerate(sizes):
        seed = seeds[i] if seeds and i < len(seeds) else None
        dataset = generate_dataset(n=n, seed=seed, save=save)
        datasets.append(dataset)
        print(f"[generator] Generated dataset {i + 1}/{len(sizes)}: n={n}, seed={dataset['seed']}")

    return datasets


# --- CLI usage ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic routing datasets.")
    parser.add_argument("--n", type=int, default=10, help="Number of locations (2–25)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--no-save", action="store_true", help="Don't save to disk")
    parser.add_argument("--batch", action="store_true", help="Generate a standard training batch")
    args = parser.parse_args()

    if args.batch:
        print("[generator] Generating standard training batch...")
        batch_generate(sizes=[5, 10, 10, 15, 15, 20, 25], save=not args.no_save)
    else:
        dataset = generate_dataset(n=args.n, seed=args.seed, save=not args.no_save)
        print(f"\n[generator] Dataset preview:")
        print(f"  Locations : {dataset['num_locations']}")
        print(f"  Seed      : {dataset['seed']}")
        print(f"  Generated : {dataset['generated_at']}")
        print(f"  Coords[0] : {dataset['coordinates'][0]}")
        print(f"  Dist[0][1]: {dataset['distance_matrix'][0][1]} km")