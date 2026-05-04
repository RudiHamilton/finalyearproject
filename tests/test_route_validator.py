from optimisation.route_validator import is_valid_route


def test_valid_route_returns_true():
    route = [0, 1, 2, 3]

    assert is_valid_route(route, 4) is True


def test_route_with_duplicate_location_returns_false():
    route = [0, 1, 1, 3]

    assert is_valid_route(route, 4) is False


def test_route_with_missing_location_returns_false():
    route = [0, 1, 3]

    assert is_valid_route(route, 4) is False


def test_route_with_out_of_range_location_returns_false():
    route = [0, 1, 2, 4]

    assert is_valid_route(route, 4) is False