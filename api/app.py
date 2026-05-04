from flask import Flask, jsonify
from api.routes.delivery_handler import delivery_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(delivery_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return jsonify({
            "message": "FYP Route Planner API running",
            "endpoints": [
                "/api/deliveries",
                "/api/deliveries/pending"
            ]
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)