from data.generator import generate_dataset


def test_generate_dataset_creates_correct_number_of_locations():
    dataset = generate_dataset(n=10, seed=42, save=False)

    assert dataset["num_locations"] == 10
    assert len(dataset["coordinates"]) == 10


def test_distance_matrix_shape_matches_locations():
    dataset = generate_dataset(n=10, seed=42, save=False)

    matrix = dataset["distance_matrix"]

    assert len(matrix) == 10
    assert all(len(row) == 10 for row in matrix)


def test_distance_matrix_diagonal_is_zero():
    dataset = generate_dataset(n=10, seed=42, save=False)

    matrix = dataset["distance_matrix"]

    for i in range(10):
        assert matrix[i][i] == 0