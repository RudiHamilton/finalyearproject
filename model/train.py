import glob
import json
import os

import joblib
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from model.environment import (
    nearest_neighbour_route,
    two_opt_route,
    create_training_rows_from_teacher_route,
    calculate_route_distance,
)


DATASET_FOLDER = "data/datasets"
MODEL_OUTPUT_PATH = "model/trained_route_model.joblib"


def load_dataset_files():
    """
    Loads all generated dataset JSON files from data/datasets.
    """
    file_paths = glob.glob(os.path.join(DATASET_FOLDER, "*.json"))

    datasets = []

    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as file:
            dataset = json.load(file)
            datasets.append(dataset)

    return datasets


def build_training_dataset(datasets):
    """
    Converts generated route datasets into ML training rows.

    The teacher route is created using:
    nearest neighbour -> 2-opt improvement
    """
    all_features = []
    all_labels = []

    route_summary = []

    for dataset in datasets:
        coordinates = dataset["coordinates"]
        distance_matrix = dataset["distance_matrix"]

        nearest_route = nearest_neighbour_route(distance_matrix, start_index=0)
        teacher_route = two_opt_route(nearest_route, distance_matrix)

        nearest_distance = calculate_route_distance(nearest_route, distance_matrix)
        teacher_distance = calculate_route_distance(teacher_route, distance_matrix)

        features, labels = create_training_rows_from_teacher_route(
            distance_matrix=distance_matrix,
            coordinates=coordinates,
            teacher_route=teacher_route
        )

        all_features.extend(features)
        all_labels.extend(labels)

        route_summary.append({
            "file_seed": dataset.get("seed"),
            "num_locations": dataset.get("num_locations"),
            "nearest_distance": nearest_distance,
            "teacher_distance": teacher_distance,
            "teacher_route": teacher_route,
        })

    return all_features, all_labels, route_summary


def main():
    print("Loading generated datasets...")

    datasets = load_dataset_files()

    if not datasets:
        print(f"No dataset files found in {DATASET_FOLDER}")
        return

    print(f"Loaded {len(datasets)} dataset file(s).")

    features, labels, route_summary = build_training_dataset(datasets)

    if not features:
        print("No training rows generated.")
        return

    print(f"Training rows: {len(features)}")
    print(f"Positive labels: {sum(labels)}")
    print(f"Negative labels: {len(labels) - sum(labels)}")

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels
    )

    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=8,
        random_state=42,
        eval_metric="logloss"
    )

    print("Training XGBoost model...")
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)

    accuracy = accuracy_score(y_test, predictions)

    print("")
    print("Model evaluation")
    print("----------------")
    print(f"Accuracy: {accuracy:.4f}")
    print("")
    print(classification_report(y_test, predictions))

    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT_PATH)

    print("")
    print(f"Saved model to: {MODEL_OUTPUT_PATH}")
    print("")
    print("Teacher route examples:")
    for item in route_summary[:5]:
        print(
            f"Seed {item['file_seed']} | "
            f"NN: {item['nearest_distance']:.2f} km | "
            f"Teacher NN+2opt: {item['teacher_distance']:.2f} km | "
            f"Route: {item['teacher_route']}"
        )
        
        feature_names = [
        "dist_to_candidate",
        "relative_distance",
        "avg_dist_from_candidate",
        "min_dist",
        "max_dist",
        "stops_remaining",
        "current_lat",
        "current_lng",
        "candidate_lat",
        "candidate_lng",
    ]

    report = classification_report(y_test, predictions, output_dict=True)

    training_summary = {
        "training_rows": len(features),
        "positive_labels": sum(labels),
        "negative_labels": len(labels) - sum(labels),
        "accuracy": round(accuracy, 4),
        "class_1_precision": round(report["1"]["precision"], 4),
        "class_1_recall": round(report["1"]["recall"], 4),
        "class_1_f1": round(report["1"]["f1-score"], 4),
    }

    feature_importance = sorted(
        [
            {"name": name, "importance": round(float(imp), 6)}
            for name, imp in zip(feature_names, model.feature_importances_)
        ],
        key=lambda x: -x["importance"]
    )

    os.makedirs("experiments", exist_ok=True)

    with open("experiments/training_summary.json", "w") as f:
        json.dump(training_summary, f, indent=2)

    with open("experiments/feature_importance.json", "w") as f:
        json.dump(feature_importance, f, indent=2)

    print("Saved training_summary.json and feature_importance.json")


if __name__ == "__main__":
    main()