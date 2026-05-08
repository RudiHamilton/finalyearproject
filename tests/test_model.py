from model.model import predict_ml_route


def test_ml_route_contains_all_locations(monkeypatch):
    class DummyModel:
        def predict_proba(self, rows):
            return [[0.4, 0.6]]

    monkeypatch.setattr("model.model.load_trained_model", lambda: DummyModel())

    distance_matrix = [
        [0, 10, 20],
        [10, 0, 15],
        [20, 15, 0],
    ]

    coordinates = [
        {"id": 0, "lat": 54.1, "lng": -7.1},
        {"id": 1, "lat": 54.2, "lng": -7.2},
        {"id": 2, "lat": 54.3, "lng": -7.3},
    ]

    route = predict_ml_route(distance_matrix, coordinates, start_index=0)

    assert len(route) == 3
    assert sorted(route) == [0, 1, 2]
    assert len(set(route)) == 3