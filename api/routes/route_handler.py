from flask import Blueprint, jsonify, request

from services.route_service import optimise_deliveries


route_bp = Blueprint("route", __name__)


@route_bp.route("/deliveries/optimise", methods=["POST"])
def optimise_route():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON request body."}), 400

    deliveries = data.get("deliveries", [])
    method = data.get("method", "ml_two_opt")

    if not deliveries:
        return jsonify({"error": "No deliveries provided."}), 400

    try:
        result = optimise_deliveries(
            deliveries=deliveries,
            method=method,
        )

        return jsonify(result), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except FileNotFoundError as error:
        return jsonify({"error": str(error)}), 500

    except Exception as error:
        return jsonify({
            "error": "Route optimisation failed.",
            "details": str(error),
        }), 500