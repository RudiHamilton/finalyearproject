"""
evaluator.py

Functions for evaluating generated routes.
"""


def calculate_route_distance(
    route: list[int],
    distance_matrix: list[list[float]],
    return_to_start: bool = False
) -> float:
    """
    Calculate the total distance of a route.

    Args:
        route: List of location indexes in visit order.
        distance_matrix: Matrix containing pairwise distances.
        return_to_start: If True, adds the distance from the final location back to the start.

    Returns:
        Total route distance.
    """

    if not route:
        raise ValueError("Route cannot be empty.")

    total_distance = 0.0

    for index in range(len(route) - 1):
        current_location = route[index]
        next_location = route[index + 1]

        total_distance += distance_matrix[current_location][next_location]

    if return_to_start and len(route) > 1:
        total_distance += distance_matrix[route[-1]][route[0]]

    return round(total_distance, 4)