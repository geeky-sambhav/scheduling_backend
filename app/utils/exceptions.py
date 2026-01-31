"""
Custom exceptions and error handlers for the scheduling backend.
"""
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


class SchedulingError(Exception):
    """Base exception for scheduling errors."""
    
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class DoubleBookingError(SchedulingError):
    """Raised when an employee is already assigned to a job at the same time."""
    
    def __init__(self, employee_name, job_name):
        message = f"Employee '{employee_name}' is already assigned to '{job_name}' at this time"
        super().__init__(message, 409)


class TimeOverlapError(SchedulingError):
    """Raised when job time slots overlap for an employee."""
    
    def __init__(self, employee_name, existing_job, new_job):
        message = (
            f"Time conflict for employee '{employee_name}': "
            f"'{new_job}' overlaps with existing assignment '{existing_job}'"
        )
        super().__init__(message, 409)


class EmployeeUnavailableError(SchedulingError):
    """Raised when trying to assign an unavailable employee."""
    
    def __init__(self, employee_name):
        message = f"Employee '{employee_name}' is currently unavailable for assignment"
        super().__init__(message, 400)


class ResourceNotFoundError(SchedulingError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type, resource_id):
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, 404)


class ValidationError(SchedulingError):
    """Raised when request validation fails."""
    
    def __init__(self, errors):
        message = "Validation failed"
        super().__init__(message, 400)
        self.errors = errors


def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    
    @app.errorhandler(SchedulingError)
    def handle_scheduling_error(error):
        logger.warning(f"Scheduling error: {error.message}")
        response = {
            'success': False,
            'error': error.message
        }
        if isinstance(error, ValidationError):
            response['details'] = error.errors
        return jsonify(response), error.status_code
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        logger.warning(f"Bad request: {error}")
        return jsonify({
            'success': False,
            'error': 'Bad request'
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
