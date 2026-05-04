"""
route_validator.py

Checks whether a generated route is valid.
"""


def is_valid_route(route: list[int], number_of_locations: int) -> bool:
    """
    Check that a route visits every location exactly once.

    Args:
        route: List of location indexes in visit order.
        number_of_locations: Total number of locations expected.

    Returns:
        True if the route contains every location exactly once.
    """

    if len(route) != number_of_locations:
        return False

    expected_locations = list(range(number_of_locations))

    return sorted(route) == expected_locations