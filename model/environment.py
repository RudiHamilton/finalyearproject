import itertools
import math


def calculate_route_distance(route, distance_matrix):
    """
    Calculates total distance for a route using a distance matrix.
    The route is a list of location indexes, e.g. [0, 3, 2, 1].
    """
    total_distance = 0

    for index in range(len(route) - 1):
        current_location = route[index]
        next_location = route[index + 1]

        total_distance += distance_matrix[current_location][next_location]

    return total_distance


def nearest_neighbour_route(distance_matrix, start_index=0):
    """
    Greedy nearest neighbour route.
    Starts at start_index and repeatedly chooses the closest unvisited location.
    """
    number_of_locations = len(distance_matrix)

    unvisited = set(range(number_of_locations))
    unvisited.remove(start_index)

    route = [start_index]
    current_location = start_index

    while unvisited:
        next_location = min(
            unvisited,
            key=lambda candidate: distance_matrix[current_location][candidate]
        )

        route.append(next_location)
        unvisited.remove(next_location)
        current_location = next_location

    return route


def two_opt_route(route, distance_matrix):
    """
    Improves a route by reversing sections when this reduces total distance.
    """
    best_route = route.copy()
    best_distance = calculate_route_distance(best_route, distance_matrix)

    improved = True

    while improved:
        improved = False

        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route)):
                if j - i == 1:
                    continue

                new_route = best_route[:]
                new_route[i:j] = reversed(best_route[i:j])

                new_distance = calculate_route_distance(new_route, distance_matrix)

                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True

    return best_route


def brute_force_best_route(distance_matrix, start_index=0):
    """
    Finds the true best route by checking every possible route.
    Only use this for small datasets because it scales factorially.
    For n=10 this can be too slow, so mainly use it for n<=8.
    """
    number_of_locations = len(distance_matrix)
    other_locations = [i for i in range(number_of_locations) if i != start_index]

    best_route = None
    best_distance = math.inf

    for permutation in itertools.permutations(other_locations):
        route = [start_index] + list(permutation)
        distance = calculate_route_distance(route, distance_matrix)

        if distance < best_distance:
            best_distance = distance
            best_route = route

    return best_route


def get_candidate_features(
    distance_matrix,
    coordinates,
    current_location,
    candidate_location,
    unvisited_locations,
    total_locations,
):
    """
    Builds one ML feature row for one candidate next stop.

    The model sees:
    - distance from current stop to candidate
    - how central the candidate is among remaining stops
    - min/max/average distance from candidate to other unvisited stops
    - number of stops remaining
    - coordinate information
    """
    distance_current_to_candidate = distance_matrix[current_location][candidate_location]

    distance_to_depot = distance_matrix[candidate_location][0]

    progress = 1 - (len(unvisited_locations) / total_locations)

    distances_from_candidate = [
        distance_matrix[candidate_location][other]
        for other in unvisited_locations
        if other != candidate_location
    ]

    if distances_from_candidate:
        candidate_average_distance = sum(distances_from_candidate) / len(distances_from_candidate)
        candidate_min_distance = min(distances_from_candidate)
        candidate_max_distance = max(distances_from_candidate)
    else:
        candidate_average_distance = 0
        candidate_min_distance = 0
        candidate_max_distance = 0
        
    relative_distance = distance_current_to_candidate / (candidate_average_distance + 1e-9)


    current_coordinates = coordinates[current_location]
    candidate_coordinates = coordinates[candidate_location]

    return [
        distance_current_to_candidate,
        distance_to_depot,
        progress,
        candidate_average_distance,
        candidate_min_distance,
        candidate_max_distance,
        relative_distance,
        len(unvisited_locations),
        current_coordinates["lat"],
        current_coordinates["lng"],
        candidate_coordinates["lat"],
        candidate_coordinates["lng"],
    ]


def create_training_rows_from_teacher_route(distance_matrix, coordinates, teacher_route):
    """
    Converts a teacher route into supervised learning rows.

    For each route step:
    - every unvisited candidate becomes one training row
    - the actual next stop from the teacher route gets label 1
    - all other candidates get label 0
    """
    features = []
    labels = []

    visited = {teacher_route[0]}

    for route_position in range(len(teacher_route) - 1):
        current_location = teacher_route[route_position]
        correct_next_location = teacher_route[route_position + 1]

        unvisited_locations = [
            location
            for location in range(len(distance_matrix))
            if location not in visited
        ]

        for candidate_location in unvisited_locations:
            row = get_candidate_features(
                distance_matrix=distance_matrix,
                coordinates=coordinates,
                current_location=current_location,
                candidate_location=candidate_location,
                unvisited_locations=unvisited_locations,
                total_locations=len(distance_matrix),
            )

            label = 1 if candidate_location == correct_next_location else 0

            features.append(row)
            labels.append(label)

        visited.add(correct_next_location)

    return features, labels