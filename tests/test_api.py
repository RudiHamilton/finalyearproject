from api.app import create_app


def test_home_endpoint_responds():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_optimise_endpoint_rejects_empty_request():
    app = create_app()
    client = app.test_client()

    response = client.post("/api/deliveries/optimise", json={})

    assert response.status_code == 400