from optimisation.evaluator import calculate_route_distance
from optimisation.route_validator import is_valid_route
from optimisation.two_opt import two_opt

def test_two_opt_returns_valid_route():
    distance_matrix = [
        [0, 2, 9, 10],
        [2, 0, 6, 4],
        [9, 6, 0, 3],
        [10, 4, 3, 0],
    ]

    route = [0, 2, 1, 3]

    improved_route = two_opt(route, distance_matrix)

    assert is_valid_route(improved_route, 4) is True


def test_two_opt_does_not_make_route_worse():
    distance_matrix = [
        [0, 2, 9, 10],
        [2, 0, 6, 4],
        [9, 6, 0, 3],
        [10, 4, 3, 0],
    ]

    route = [0, 2, 1, 3]

    original_distance = calculate_route_distance(route, distance_matrix)
    improved_route = two_opt(route, distance_matrix)
    improved_distance = calculate_route_distance(improved_route, distance_matrix)

    assert improved_distance <= original_distance


def test_two_opt_keeps_short_routes_unchanged():
    distance_matrix = [
        [0, 2, 9],
        [2, 0, 6],
        [9, 6, 0],
    ]

    route = [0, 1, 2]

    assert two_opt(route, distance_matrix) == route