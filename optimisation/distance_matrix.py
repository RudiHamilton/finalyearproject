"""
distance_matrix.py
Geographic distance calculations for delivery route optimisation.
Provides Haversine distance and pairwise distance matrix construction.
"""

import math


def haversine(coord1: dict, coord2: dict) -> float:
    """
    Calculate the great-circle distance (km) between two coordinates
    using the Haversine formula.

    Args:
        coord1: dict with 'lat' and 'lng'
        coord2: dict with 'lat' and 'lng'

    Returns:
        Distance in kilometres (float)
    """
    R = 6371.0  # Earth's radius in km

    lat1 = math.radians(coord1["lat"])
    lat2 = math.radians(coord2["lat"])
    dlat = math.radians(coord2["lat"] - coord1["lat"])
    dlng = math.radians(coord2["lng"] - coord1["lng"])

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 4)


def build_distance_matrix(coordinates: list) -> list:
    """
    Build a symmetric NxN distance matrix from a list of coordinates.

    Args:
        coordinates: list of dicts with 'id', 'lat', 'lng'

    Returns:
        2D list (NxN) of distances in km
    """
    n = len(coordinates)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            dist = haversine(coordinates[i], coordinates[j])
            matrix[i][j] = dist
            matrix[j][i] = dist  # symmetric

    return matrix


def route_total_distance(route: list, distance_matrix: list) -> float:
    """
    Calculate the total distance of a route including return to start.

    Args:
        route:           Ordered list of location indices e.g. [0, 3, 1, 2]
        distance_matrix: 2D list of pairwise distances

    Returns:
        Total route distance in km (float)
    """
    total = 0.0
    n = len(route)

    for i in range(n):
        from_idx = route[i]
        to_idx = route[(i + 1) % n]  # wraps back to start
        total += distance_matrix[from_idx][to_idx]

    return round(total, 4)


if __name__ == "__main__":
    # Quick sanity check
    test_coords = [
        {"id": 0, "lat": 54.3, "lng": -6.2},
        {"id": 1, "lat": 54.6, "lng": -5.9},
        {"id": 2, "lat": 54.1, "lng": -7.1},
    ]

    matrix = build_distance_matrix(test_coords)
    print("Distance matrix:")
    for row in matrix:
        print([f"{d:.2f}" for d in row])

    route = [0, 1, 2]
    total = route_total_distance(route, matrix)
    print(f"\nTotal distance for route {route}: {total} km")