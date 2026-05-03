"""
2_opt.py

2-opt route improvement algorithm.

This improves an existing route by reversing sections of the route when
doing so reduces the total route distance.
"""

from optimisation.evaluator import calculate_route_distance


def two_opt(
    route: list[int],
    distance_matrix: list[list[float]],
    return_to_start: bool = False
) -> list[int]:
    """
    Improve a route using the 2-opt local search heuristic.

    Args:
        route: Existing route order.
        distance_matrix: Matrix containing pairwise distances.
        return_to_start: Whether the route returns to the starting point.

    Returns:
        Improved route order.
    """

    if len(route) < 4:
        return route

    best_route = route[:]
    best_distance = calculate_route_distance(
        best_route,
        distance_matrix,
        return_to_start=return_to_start
    )

    improved = True

    while improved:
        improved = False

        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route)):
                if j - i == 1:
                    continue

                new_route = best_route[:]
                new_route[i:j] = reversed(best_route[i:j])

                new_distance = calculate_route_distance(
                    new_route,
                    distance_matrix,
                    return_to_start=return_to_start
                )

                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True

    return best_route