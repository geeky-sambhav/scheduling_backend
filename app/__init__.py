import logging
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.routes.employees import employees_bp
from app.routes.jobs import jobs_bp
from app.routes.schedule import schedule_bp
from app.routes.assignment import assignments_bp


def create_app(config_class=Config):
    """
    Application factory for creating Flask app instances.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO if not app.debug else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    # Register basic Flask error handlers for unhandled errors
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    app.register_blueprint(employees_bp, url_prefix="/employees")
    app.register_blueprint(jobs_bp, url_prefix="/jobs")
    app.register_blueprint(schedule_bp, url_prefix="/schedule")
    app.register_blueprint(assignments_bp, url_prefix="/assign")

    return app
