from data.generator import generate_dataset
from optimisation.nearest_neighbour import nearest_neighbour


def test_nearest_neighbour_with_fixed_matrix():
    """
    Unit test using a fixed distance matrix.

    This proves the nearest-neighbour logic works because the expected
    route can be manually verified.
    """

    distance_matrix = [
        [0, 2, 9, 10],
        [2, 0, 6, 4],
        [9, 6, 0, 3],
        [10, 4, 3, 0],
    ]

    route = nearest_neighbour(distance_matrix, start_index=0)

    assert route == [0, 1, 3, 2]


def test_nearest_neighbour_with_seeded_dataset_returns_valid_route():
    """
    Integration test using generated project data.

    The fixed seed makes the dataset repeatable.
    This checks the algorithm works with generated distance matrices.
    """

    dataset = generate_dataset(n=10, seed=42, save=False)

    distance_matrix = dataset["distance_matrix"]
    route = nearest_neighbour(distance_matrix, start_index=0)

    assert len(route) == dataset["num_locations"]
    assert route[0] == 0
    assert sorted(route) == list(range(dataset["num_locations"]))