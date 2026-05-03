"""
compare_algorithms.py

Runs comparison experiments between different route generation approaches.
"""

import random
import time

from data.generator import generate_dataset
from optimisation.nearest_neighbour import nearest_neighbour
from optimisation.two_opt import two_opt
from optimisation.evaluator import calculate_route_distance
from optimisation.route_validator import is_valid_route


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


def compare_algorithms(number_of_locations: int = 10, seed: int = 42) -> list[dict]:
    """
    Generate a dataset and compare route optimisation approaches.
    """

    random.seed(seed)

    dataset = generate_dataset(n=number_of_locations, seed=seed, save=False)
    distance_matrix = dataset["distance_matrix"]

    random_route = create_random_route(number_of_locations, start_index=0)

    nearest_route = nearest_neighbour(distance_matrix, start_index=0)

    nearest_two_opt_route = two_opt(nearest_route, distance_matrix)

    results = [
        evaluate_route(
            "Random route",
            random_route,
            distance_matrix,
        ),
        evaluate_route(
            "Nearest neighbour",
            nearest_route,
            distance_matrix,
        ),
        evaluate_route(
            "Nearest neighbour + 2-opt",
            nearest_two_opt_route,
            distance_matrix,
        ),
    ]

    return results


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
        number_of_locations=10,
        seed=42,
    )

    print_results(comparison_results)