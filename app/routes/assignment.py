"""
Assignment API routes.

Handles assignment operations:
- Create new assignment (POST /assign)
- Delete assignment (DELETE /assign/:id)
"""

from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.services.assignment_service import AssignmentService
from app.models import (
    AssignmentCreateRequest,
    ErrorResponse,
    SuccessResponse,
    ValidationErrorResponse,
    ValidationErrorDetail,
)

# Create blueprint
assignments_bp = Blueprint("assign", __name__)

# Initialize service
assignment_service = AssignmentService()


@assignments_bp.route("", methods=["POST"])
def create_assignment():
    """
    Assign an employee to a job and write the result to a JSON file.

    Business Rules Enforced:
        - Rule 1: No Double Booking - An employee cannot be assigned to more than one job at the same time
        - Rule 2: No Overlapping Time Slots - Employees cannot be assigned to jobs whose time windows overlap
        - Rule 3: Availability Filtering - If an employee is marked unavailable, assignment is rejected

    Request Body:
        {
            "employeeId": "EMP001",
            "jobId": "JOB001"
        }

    Returns:
        201: Assignment created successfully
        400: Validation error or employee unavailable (Rule 3)
        404: Employee or job not found
        409: Time conflict detected (Rule 1 & 2)
        500: Server error

    Example:
        POST /api/assignments/assign
        Content-Type: application/json

        {
            "employeeId": "EMP001",
            "jobId": "JOB001"
        }
    """
    try:
        # Get and validate request data
        request_data = request.get_json()

        if not request_data:
            error_response = ErrorResponse(
                error="InvalidRequest", message="Request body is required"
            )
            return jsonify(error_response.model_dump()), 400

        # Validate with Pydantic
        try:
            validated_request = AssignmentCreateRequest(**request_data)
        except ValidationError as e:
            # Handle Pydantic validation errors
            validation_errors = []
            for error in e.errors():
                validation_errors.append(
                    ValidationErrorDetail(
                        field=".".join(str(loc) for loc in error["loc"]),
                        message=error["msg"],
                        type=error["type"],
                    )
                )
            error_response = ValidationErrorResponse(errors=validation_errors)
            return jsonify(error_response.model_dump()), 400

        # Create assignment through service (enforces all business rules)
        assignment, error = assignment_service.create_assignment(
            employee_id=validated_request.employeeId,
            job_id=validated_request.jobId,
        )

        # Handle service errors
        if error:
            error_response = ErrorResponse(
                error=error.get("error_type", "Internal Server Error"),
                message=error["message"],
                details=error.get("details"),
            )
            return jsonify(error_response.model_dump()), error["status_code"]

        # Return success response
        response = SuccessResponse(
            message="Assignment created successfully", data=assignment.model_dump()
        )

        return jsonify(response.model_dump()), 201

    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to create assignment",
            details={"error": str(e)},
        )
        return jsonify(error_response.model_dump()), 500


@assignments_bp.route("/<assignment_id>", methods=["DELETE"])
def delete_assignment(assignment_id: str):
    """
    Remove a schedule assignment and update the JSON file.

    Path Parameters:
        assignment_id (str): Unique assignment identifier

    Returns:
        200: Assignment deleted successfully
        404: Assignment not found
        500: Server error

    Example:
        DELETE /assign/ASSIGN001
    """
    try:
        # Delete assignment through service
        deleted, error = assignment_service.delete_assignment(assignment_id)

        # Handle service errors
        if error:
            error_response = ErrorResponse(
                error=error["error_type"], message=error["message"]
            )
            return jsonify(error_response.model_dump()), error["status_code"]

        # Return success response
        response = SuccessResponse(
            message="Assignment deleted successfully", data={"deletedId": assignment_id}
        )

        return jsonify(response.model_dump()), 200

    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to delete assignment",
            details={"error": str(e)},
        )
        return jsonify(error_response.model_dump()), 500
