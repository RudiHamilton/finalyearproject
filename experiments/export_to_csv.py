"""
export_to_csv.py
Converts experiment JSON result files into CSV format for reporting.
"""

import csv
import json
import os


EXPERIMENTS_DIR = os.path.dirname(__file__)


def load_json(filename):
    """
    Loads a JSON file from the experiments directory.
    """
    path = os.path.join(EXPERIMENTS_DIR, filename)

    if not os.path.exists(path):
        print(f"[export] Skipping {filename} — file not found.")
        return None

    with open(path, "r") as f:
        return json.load(f)


def export_training_summary():
    """
    Exports training_summary.json to training_summary.csv.
    """
    data = load_json("training_summary.json")

    if not data:
        return

    path = os.path.join(EXPERIMENTS_DIR, "training_summary.csv")

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        for key, value in data.items():
            writer.writerow([key, value])

    print(f"[export] Saved training_summary.csv")


def export_feature_importance():
    """
    Exports feature_importance.json to feature_importance.csv.
    """
    data = load_json("feature_importance.json")

    if not data:
        return

    path = os.path.join(EXPERIMENTS_DIR, "feature_importance.csv")

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Feature", "Importance"])
        for row in data:
            writer.writerow([row["name"], row["importance"]])

    print(f"[export] Saved feature_importance.csv")


def export_results_averages():
    """
    Exports averaged algorithm results from results.json to results_averages.csv.
    """
    data = load_json("results.json")

    if not data:
        return

    path = os.path.join(EXPERIMENTS_DIR, "results_averages.csv")

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Algorithm", "Average Distance (km)", "vs NN+2opt (%)"])
        for algorithm, values in data["averages"].items():
            writer.writerow([
                algorithm,
                values["average_distance_km"],
                values["vs_nn_two_opt_percent"],
            ])

    print(f"[export] Saved results_averages.csv")


def export_results_trials():
    """
    Exports per-trial raw data from results.json to results_trials.csv.
    """
    data = load_json("results.json")

    if not data:
        return

    trials = data["trials"]

    if not trials:
        print("[export] No trial data found in results.json.")
        return

    algorithms = [key for key in trials[0].keys() if key != "seed"]

    path = os.path.join(EXPERIMENTS_DIR, "results_trials.csv")

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)

        header = ["Seed"] + [f"{algo} (km)" for algo in algorithms]
        writer.writerow(header)

        for trial in trials:
            row = [trial["seed"]] + [
                trial[algo]["distance_km"] for algo in algorithms
            ]
            writer.writerow(row)

    print(f"[export] Saved results_trials.csv")


def main():
    print("[export] Exporting experiment results to CSV...\n")

    export_training_summary()
    export_feature_importance()
    export_results_averages()
    export_results_trials()

    print("\n[export] Done.")


if __name__ == "__main__":
    main()