"""
Schedule API routes.

Handles schedule-related endpoints:
- Get current list of assignments with full details
"""

from flask import Blueprint, jsonify

from app.models import ErrorResponse, SuccessResponse
from app.services.schedule_service import ScheduleService

# Create blueprint
schedule_bp = Blueprint("schedule", __name__)

# Initialize service
schedule_service = ScheduleService()


@schedule_bp.route("", methods=["GET"])
def get_schedule():
    """
    Get the current list of assignments with full employee and job details.

    Returns:
        200: List of assignments with enriched data
        500: Server error

    Response includes:
        - Assignment details (id, assignedAt, notes)
        - Employee details (id, name, role)
        - Job details (id, name, startTime, endTime)

    Example:
        GET /schedule
    """
    try:
        enriched_assignments = schedule_service.get_enriched_assignments()

        # Convert to dict for JSON response
        assignments_data = [a.model_dump() for a in enriched_assignments]

        response = SuccessResponse(
            count=len(assignments_data),
            data=assignments_data,
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to retrieve schedule",
            details={"error": str(e)},
        )
        return jsonify(error_response.model_dump()), 500
