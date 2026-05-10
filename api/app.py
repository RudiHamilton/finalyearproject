from flask import Flask, jsonify
from flask_cors import CORS
from api.routes.delivery_handler import delivery_bp
from api.routes.employee_handler import employee_bp
from api.routes.route_handler import route_bp


def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="")
    CORS(app)
    app.register_blueprint(delivery_bp, url_prefix="/api")
    app.register_blueprint(employee_bp, url_prefix="/api")
    app.register_blueprint(route_bp, url_prefix="/api")
    
    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8000)