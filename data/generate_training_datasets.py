"""
generate_training_datasets.py

Generates a large batch of synthetic route datasets for ML training.
These JSON files are temporary and can be deleted after the model has been trained.
"""

import argparse
import os
import random

from data.generator import generate_dataset, DATASETS_DIR


def wipe_existing_datasets():
    """
    Deletes existing generated dataset JSON files before creating a fresh batch.
    """
    if not os.path.exists(DATASETS_DIR):
        return

    for filename in os.listdir(DATASETS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(DATASETS_DIR, filename)
            os.remove(file_path)


def main():
    """
    Generates a configurable batch of synthetic route datasets for model training.

    The generated JSON files are temporary training data and can be deleted after
    the model is trained because they can be recreated using the same generator
    and seed values.
    """
    parser = argparse.ArgumentParser(
        description="Generate synthetic routing datasets for ML training."
    )

    parser.add_argument(
        "--count",
        type=int,
        default=800,
        help="Number of datasets to generate."
    )

    parser.add_argument(
    "--min-n",
    type=int,
    default=10,
    help="Minimum number of locations per dataset."
    )
    
    parser.add_argument(
        "--max-n",
        type=int,
        default=25,
        help="Maximum number of locations per dataset."
    )

    parser.add_argument(
        "--start-seed",
        type=int,
        default=0,
        help="Starting seed value for reproducibility."
    )   

    parser.add_argument(
        "--wipe",
        action="store_true",
        help="Delete existing generated dataset JSON files first."
    )
    
    if args.start_seed + args.count > 1000:
        print("[WARNING] Seed range overlaps with evaluation seeds (1000+)")
        args = parser.parse_args()

    if args.wipe:
        print("[training-data] Wiping existing dataset JSON files...")
        wipe_existing_datasets()

    os.makedirs(DATASETS_DIR, exist_ok=True)

    print(f"[training-data] Generating {args.count} datasets...")
    print(f"[training-data] Locations per dataset: {args.min_n}-{args.max_n}")
    print(f"[training-data] Output folder: {DATASETS_DIR}")

    
    for index in range(args.count):
        seed = args.start_seed + index
        n = random.randint(args.min_n, args.max_n)
        generate_dataset(       #UHHHHHHH THIS IS THE FUNCTION CALL TO GENERATE THE DATASET ITS  IN THE GENERATOR.PY FILE. 
            n=n,
            seed=seed,
            save=True
        )

        if (index + 1) % 50 == 0:
            print(f"[training-data] Generated {index + 1}/{args.count}")

    print("")
    print("[training-data] Finished.")
    print(f"[training-data] Total generated: {args.count}")


if __name__ == "__main__":
    main()