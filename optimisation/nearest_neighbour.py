"""
nearest_neighbour.py

Greedy nearest-neighbour route optimisation algorithm.

The algorithm starts at a chosen location, then repeatedly visits the
closest unvisited location until all locations have been visited.
"""


def nearest_neighbour(distance_matrix: list[list[float]], start_index: int = 0) -> list[int]:
    """
    Generate a route using the nearest-neighbour heuristic.

    Args:
        distance_matrix: A square matrix where distance_matrix[i][j]
                         is the distance from location i to location j.
        start_index: The location index where the route should begin.

    Returns:
        A list of location indexes representing the visit order.

    Example:
        [0, 3, 1, 2, 4]
    """

    if not distance_matrix:
        raise ValueError("Distance matrix cannot be empty.")

    number_of_locations = len(distance_matrix)

    if start_index < 0 or start_index >= number_of_locations:
        raise ValueError("Start index is outside the valid location range.")

    unvisited = set(range(number_of_locations))
    route = [start_index]

    unvisited.remove(start_index)
    current_location = start_index

    while unvisited:
        nearest_location = min(
            unvisited,
            key=lambda location: distance_matrix[current_location][location]
        )

        route.append(nearest_location)
        unvisited.remove(nearest_location)
        current_location = nearest_location

    return route