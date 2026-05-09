"""
compare_algorithms.py
Runs comparison experiments between different route generation approaches.
"""
import random
import time
import json
import os

from data.generator import generate_dataset
from optimisation import distance_matrix
from optimisation.nearest_neighbour import nearest_neighbour
from optimisation.two_opt import two_opt
from optimisation.evaluator import calculate_route_distance
from optimisation.route_validator import is_valid_route
from model.model import predict_ml_route, predict_ml_two_opt_route

def create_random_route(number_of_locations: int, start_index: int = 0) -> list[int]:
    """
    Create a random valid route while keeping the same starting location.
    """
    locations = list(range(number_of_locations))
    locations.remove(start_index)
    random.shuffle(locations)
    return [start_index] + locations

def evaluate_route(
    algorithm_name: str,
    route: list[int],
    distance_matrix: list[list[float]],
) -> dict:
    """
    Evaluate a route using validity and total distance.
    """
    start_time = time.perf_counter()
    valid_route = is_valid_route(route, len(distance_matrix))
    total_distance = calculate_route_distance(route, distance_matrix)
    end_time = time.perf_counter()

    return {
        "algorithm": algorithm_name,
        "route": route,
        "valid": valid_route,
        "distance_km": total_distance,
        "runtime_seconds": round(end_time - start_time, 6),
    }


def compare_algorithms(number_of_locations: int = 25, seed: int = 42) -> list[dict]:
    """
    Generate a dataset and compare route optimisation approaches.
    """
    random.seed(seed)

    dataset = generate_dataset(
        n=number_of_locations,
        seed=seed,
        save=False,
        max_locations=50,
    )

    distance_matrix = dataset["distance_matrix"]
    coordinates = dataset["coordinates"]

    random_route = create_random_route(number_of_locations, start_index=0)
    nearest_route = nearest_neighbour(distance_matrix, start_index=0)
    nearest_two_opt_route = two_opt(nearest_route, distance_matrix)
    ml_generated_route = predict_ml_route(distance_matrix, coordinates, start_index=0)
    ml_two_opt_route = predict_ml_two_opt_route(distance_matrix, coordinates, start_index=0)

    results = [
        evaluate_route("Random route", random_route, distance_matrix),
        evaluate_route("Nearest neighbour", nearest_route, distance_matrix),
        evaluate_route("Nearest neighbour + 2-opt", nearest_two_opt_route, distance_matrix),
        evaluate_route("ML (XGBoost)", ml_generated_route, distance_matrix),
        evaluate_route("ML (XGBoost) + 2-opt", ml_two_opt_route, distance_matrix),
    ]

    return results

def compare_algorithms_average(
    number_of_locations: int = 25,
    num_trials: int = 20,
    start_seed: int = 1000
) -> None:
    totals = {
        "Random route": 0,
        "Nearest neighbour": 0,
        "Nearest neighbour + 2-opt": 0,
        "ML (XGBoost)": 0,
        "ML (XGBoost) + 2-opt": 0,
    }

    all_trials = []

    print(f"\nRunning {num_trials} trials with {number_of_locations} locations each...")

    for i in range(num_trials):
        seed = start_seed + i
        results = compare_algorithms(number_of_locations=number_of_locations, seed=seed)

        trial_row = {"seed": seed}

        for result in results:
            totals[result["algorithm"]] += result["distance_km"]
            trial_row[result["algorithm"]] = {
                "distance_km": round(result["distance_km"], 4),
                "valid": result["valid"],
                "runtime_seconds": result["runtime_seconds"],
            }

        all_trials.append(trial_row)

        if (i + 1) % 5 == 0:
            print(f"Completed {i + 1}/{num_trials} trials...")

    print("\nAverage distances across all trials")
    print("=" * 40)

    nn_two_opt_avg = totals["Nearest neighbour + 2-opt"] / num_trials
    averages = {}

    for algorithm, total in totals.items():
        average = total / num_trials
        diff = ((average - nn_two_opt_avg) / nn_two_opt_avg) * 100
        averages[algorithm] = {
            "average_distance_km": round(average, 4),
            "vs_nn_two_opt_percent": round(diff, 2),
        }
        print(f"{algorithm}: {average:.2f} km  ({diff:+.1f}% vs NN+2opt)")

    os.makedirs("experiments", exist_ok=True)

    output = {
        "num_trials": num_trials,
        "num_locations": number_of_locations,
        "start_seed": start_seed,
        "averages": averages,
        "trials": all_trials,
    }

    with open("experiments/results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults saved to experiments/results.json")


def print_results(results: list[dict]) -> None:
    """
    Print comparison results in a readable format.
    """
    print("\nRoute optimisation comparison")
    print("=" * 40)

    for result in results:
        print(f"\nAlgorithm: {result['algorithm']}")
        print(f"Valid route: {result['valid']}")
        print(f"Distance: {result['distance_km']} km")
        print(f"Runtime: {result['runtime_seconds']} seconds")
        print(f"Route: {result['route']}")


if __name__ == "__main__":
    comparison_results = compare_algorithms(
        number_of_locations=25,
        seed=42,
    )
    compare_algorithms_average(
        number_of_locations=25,
        num_trials=20,
        start_seed=1000
    )

    print_results(comparison_results)