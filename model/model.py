import os
import joblib

from model.environment import get_candidate_features
from optimisation.two_opt import two_opt


MODEL_PATH = "model/trained_route_model.joblib"


def load_trained_model():
    """
    Load the trained ML route model from disk.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Trained model not found at {MODEL_PATH}. Run model training first."
        )

    return joblib.load(MODEL_PATH)


def predict_ml_route(distance_matrix, coordinates, start_index=0):
    """
    Predicts a route order using the trained ML model.

    The model scores every unvisited candidate at each step and selects
    the candidate with the highest probability of being the next best stop.
    """
    trained_model = load_trained_model()

    number_of_locations = len(distance_matrix)

    route = [start_index]
    visited = {start_index}
    current_location = start_index

    while len(route) < number_of_locations:
        unvisited_locations = [
            location
            for location in range(number_of_locations)
            if location not in visited
        ]

        candidate_scores = []

        for candidate_location in unvisited_locations:
            features = get_candidate_features(
                distance_matrix=distance_matrix,
                coordinates=coordinates,
                current_location=current_location,
                candidate_location=candidate_location,
                unvisited_locations=unvisited_locations,
                total_locations=number_of_locations,
            )

            probability = trained_model.predict_proba([features])[0][1]

            candidate_scores.append({
                "candidate": candidate_location,
                "probability": probability,
            })

        best_candidate = max(
            candidate_scores,
            key=lambda item: item["probability"]
        )["candidate"]

        route.append(best_candidate)
        visited.add(best_candidate)
        current_location = best_candidate

    return route


def predict_ml_two_opt_route(distance_matrix, coordinates, start_index=0):
    """
    Predicts an ML route, then improves it using 2-opt.
    """
    ml_route = predict_ml_route(
        distance_matrix=distance_matrix,
        coordinates=coordinates,
        start_index=start_index,
    )

    improved_route = two_opt(ml_route, distance_matrix)

    return improved_route