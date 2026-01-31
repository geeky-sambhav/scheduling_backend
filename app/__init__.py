"""
Flask Application Factory
"""
import logging
from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.utils.exceptions import register_error_handlers


def create_app(config_class=Config):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if not app.debug else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.routes.employees import employees_bp
    from app.routes.jobs import jobs_bp
    from app.routes.schedule import schedule_bp
    
    app.register_blueprint(employees_bp, url_prefix='/api')
    app.register_blueprint(jobs_bp, url_prefix='/api')
    app.register_blueprint(schedule_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'scheduling-backend'}
    
    app.logger.info('Scheduling Backend initialized successfully')
    
    return app
