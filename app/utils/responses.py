"""
Standard response helpers for consistent API responses.
"""

from flask import jsonify


def success_response(data=None, message=None, status_code=200):
    """
    Create a successful response.

    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code

    Returns:
        Flask response tuple
    """
    response = {"success": True}

    if data is not None:
        response["data"] = data

    if message:
        response["message"] = message

    return jsonify(response), status_code


def error_response(error, status_code=400, details=None):
    """
    Create an error response.

    Args:
        error: Error message
        status_code: HTTP status code
        details: Optional error details

    Returns:
        Flask response tuple
    """
    response = {"success": False, "error": error}

    if details:
        response["details"] = details

    return jsonify(response), status_code
