"""
compare_algorithms.py
Runs comparison experiments between different route generation approaches.
"""
import random
import time

import joblib

from data.generator import generate_dataset
from optimisation.nearest_neighbour import nearest_neighbour
from optimisation.two_opt import two_opt
from optimisation.evaluator import calculate_route_distance
from optimisation.route_validator import is_valid_route
from model.environment import get_candidate_features


MODEL_PATH = "model/trained_route_model.joblib"


def create_random_route(number_of_locations: int, start_index: int = 0) -> list[int]:
    """
    Create a random valid route while keeping the same starting location.
    """
    locations = list(range(number_of_locations))
    locations.remove(start_index)
    random.shuffle(locations)
    return [start_index] + locations


def ml_route(model, distance_matrix, coordinates, start_index=0) -> list[int]:
    """
    Generate a route using the trained ML model.
    At each step, scores all unvisited candidates and picks the highest probability.
    """
    n = len(distance_matrix)
    visited = {start_index}
    route = [start_index]
    current = start_index

    while len(visited) < n:
        unvisited = [i for i in range(n) if i not in visited]

        candidate_features = [
            get_candidate_features(
                distance_matrix=distance_matrix,
                coordinates=coordinates,
                current_location=current,
                candidate_location=candidate,
                unvisited_locations=unvisited,
                total_locations=n
            )
            for candidate in unvisited
        ]

        probs = model.predict_proba(candidate_features)[:, 1]
        best = unvisited[probs.argmax()]

        route.append(best)
        visited.add(best)
        current = best

    return route


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

    model = joblib.load(MODEL_PATH)

    random_route = create_random_route(number_of_locations, start_index=0)
    nearest_route = nearest_neighbour(distance_matrix, start_index=0)
    nearest_two_opt_route = two_opt(nearest_route, distance_matrix)
    ml_generated_route = ml_route(model, distance_matrix, coordinates, start_index=0)
    ml_two_opt_route = two_opt(ml_generated_route, distance_matrix)

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
    start_seed: int = 1000  # use seeds not seen during training
) -> None:
    """
    Runs comparison across multiple seeds and prints averaged results.
    """
    totals = {
        "Random route": 0,
        "Nearest neighbour": 0,
        "Nearest neighbour + 2-opt": 0,
        "ML (XGBoost)": 0,
        "ML (XGBoost) + 2-opt": 0,
    }

    print(f"\nRunning {num_trials} trials with {number_of_locations} locations each...")

    for i in range(num_trials):
        seed = start_seed + i
        results = compare_algorithms(number_of_locations=number_of_locations, seed=seed)

        for result in results:
            totals[result["algorithm"]] += result["distance_km"]

        if (i + 1) % 5 == 0:
            print(f"Completed {i + 1}/{num_trials} trials...")

    print("\nAverage distances across all trials")
    print("=" * 40)

    nn_two_opt_avg = totals["Nearest neighbour + 2-opt"] / num_trials

    for algorithm, total in totals.items():
        average = total / num_trials
        diff = ((average - nn_two_opt_avg) / nn_two_opt_avg) * 100
        print(f"{algorithm}: {average:.2f} km  ({diff:+.1f}% vs NN+2opt)")


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