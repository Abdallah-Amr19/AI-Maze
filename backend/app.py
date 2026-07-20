"""Flask application entry point for the Intelligent Maze Navigation System."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from backend.routes.api import api_blueprint


def create_app() -> Flask:
    """Application factory used for local development and production."""
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    app = Flask(__name__, static_folder=str(frontend_dir), static_url_path="")
    app.register_blueprint(api_blueprint, url_prefix="/api")

    @app.route("/", methods=["GET"])
    def serve_index():
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/<path:path>", methods=["GET"])
    def serve_static(path: str):
        return send_from_directory(frontend_dir, path)

    @app.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        return jsonify({"success": False, "error": str(error)}), 400

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"success": False, "error": "Resource not found."}), 404

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unexpected server error: %s", error)
        return jsonify(
            {
                "success": False,
                "error": "Unexpected server error. Check backend logs for details.",
            }
        ), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
