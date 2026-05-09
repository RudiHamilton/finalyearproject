import time

from optimisation.distance_matrix import build_distance_matrix
from optimisation.evaluator import calculate_route_distance
from optimisation.nearest_neighbour import nearest_neighbour
from optimisation.two_opt import two_opt
from model.model import predict_ml_route, predict_ml_two_opt_route


def prepare_coordinates(deliveries):
    """
    Converts selected delivery records into coordinate dictionaries expected
    by the distance matrix and ML feature code.
    """
    coordinates = []

    for index, delivery in enumerate(deliveries):
        latitude = delivery.get("latitude")
        longitude = delivery.get("longitude")

        if latitude is None or longitude is None:
            raise ValueError(
                f"Delivery {delivery.get('id')} is missing latitude or longitude."
            )

        coordinates.append({
            "id": index,
            "lat": float(latitude),
            "lng": float(longitude),
        })

    return coordinates


def order_deliveries_by_route(deliveries, route):
    """
    Converts a route index list into ordered delivery objects.
    """
    ordered_deliveries = []

    for route_position, delivery_index in enumerate(route, start=1):
        delivery = deliveries[delivery_index].copy()
        delivery["route_position"] = route_position
        ordered_deliveries.append(delivery)

    return 


def build_nn_two_opt_route(distance_matrix, start_index=0):
    """
    Builds a route using nearest neighbour, then improves it with 2-opt.
    """
    nn_route = nearest_neighbour(
        distance_matrix=distance_matrix,
        start_index=start_index,
    )

    improved_route = two_opt(
        route=nn_route,
        distance_matrix=distance_matrix,
        return_to_start=False,
    )

    return improved_route


def optimise_deliveries(deliveries, method="auto"):
    """
    Optimises selected scanned deliveries using the chosen route method.

    Supported methods:
    - ml
    - ml_two_opt
    - nn_two_opt
    - auto
    """
    if not deliveries:
        raise ValueError("No deliveries provided for optimisation.")

    if len(deliveries) == 1:
        single_delivery = deliveries[0].copy()
        single_delivery["route_position"] = 1

        return {
            "requested_method": method,
            "selected_method": "single_stop",
            "total_distance_km": 0,
            "runtime_ms": 0,
            "comparison": {},
            "route": [single_delivery],
        }

    start_time = time.perf_counter()

    coordinates = prepare_coordinates(deliveries)
    distance_matrix = build_distance_matrix(coordinates)

    comparison = {}

    if method == "ml":
        route = predict_ml_route(
            distance_matrix=distance_matrix,
            coordinates=coordinates,
            start_index=0,
        )
        selected_method = "ml"

    elif method == "ml_two_opt":
        route = predict_ml_two_opt_route(
            distance_matrix=distance_matrix,
            coordinates=coordinates,
            start_index=0,
        )
        selected_method = "ml_two_opt"

    elif method == "nn_two_opt":
        route = build_nn_two_opt_route(
            distance_matrix=distance_matrix,
            start_index=0,
        )
        selected_method = "nn_two_opt"

    elif method == "auto":
        nn_two_opt_route = build_nn_two_opt_route(
            distance_matrix=distance_matrix,
            start_index=0,
        )

        ml_two_opt_route = predict_ml_two_opt_route(
            distance_matrix=distance_matrix,
            coordinates=coordinates,
            start_index=0,
        )

        nn_two_opt_distance = calculate_route_distance(
            route=nn_two_opt_route,
            distance_matrix=distance_matrix,
            return_to_start=False,
        )

        ml_two_opt_distance = calculate_route_distance(
            route=ml_two_opt_route,
            distance_matrix=distance_matrix,
            return_to_start=False,
        )

        comparison = {
            "nn_two_opt_distance_km": nn_two_opt_distance,
            "ml_two_opt_distance_km": ml_two_opt_distance,
        }

        if ml_two_opt_distance < nn_two_opt_distance:
            route = ml_two_opt_route
            selected_method = "ml_two_opt"
        else:
            route = nn_two_opt_route
            selected_method = "nn_two_opt"

    else:
        raise ValueError(f"Unsupported optimisation method: {method}")

    total_distance = calculate_route_distance(
        route=route,
        distance_matrix=distance_matrix,
        return_to_start=False,
    )

    runtime_ms = round((time.perf_counter() - start_time) * 1000, 2)

    ordered_deliveries = order_deliveries_by_route(deliveries, route)

    return {
        "requested_method": method,
        "selected_method": selected_method,
        "total_distance_km": total_distance,
        "runtime_ms": runtime_ms,
        "comparison": comparison,
        "route": ordered_deliveries,
    }