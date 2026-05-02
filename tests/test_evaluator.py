import pytest

from optimisation.evaluator import calculate_route_distance


def test_calculate_route_distance_without_return_to_start():
    distance_matrix = [
        [0, 2, 9, 10],
        [2, 0, 6, 4],
        [9, 6, 0, 3],
        [10, 4, 3, 0],
    ]

    route = [0, 1, 3, 2]

    distance = calculate_route_distance(route, distance_matrix)

    assert distance == 9


def test_calculate_route_distance_with_return_to_start():
    distance_matrix = [
        [0, 2, 9, 10],
        [2, 0, 6, 4],
        [9, 6, 0, 3],
        [10, 4, 3, 0],
    ]

    route = [0, 1, 3, 2]

    distance = calculate_route_distance(
        route,
        distance_matrix,
        return_to_start=True
    )

    assert distance == 18


def test_calculate_route_distance_empty_route_raises_error():
    distance_matrix = [
        [0, 2],
        [2, 0],
    ]

    with pytest.raises(ValueError):
        calculate_route_distance([], distance_matrix)