"""
Assignment API routes.

Handles assignment operations:
- Create new assignment (POST /assign)
- Delete assignment (DELETE /assign/:id)
"""

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.utils.data_store import DataStore
from app.services.assignment_service import AssignmentService
from app.models import (
    AssignmentCreateRequest,
    ErrorResponse,
    SuccessResponse,
    ValidationErrorResponse,
    ValidationErrorDetail
)
from app.utils.exceptions import (
    EmployeeNotFoundError,
    JobNotFoundError,
    EmployeeUnavailableError,
    TimeConflictError,
    AssignmentNotFoundError
)

# Create blueprint
assignments_bp = Blueprint('assignments', __name__, url_prefix='/assign')

# Initialize service
assignment_service = AssignmentService()


@assignments_bp.route('', methods=['POST'])
def create_assignment():
    """
    Assign an employee to a job and write the result to a JSON file.
    
    Request Body:
        {
            "employeeId": "EMP001",
            "jobId": "JOB001",
            "notes": "Optional notes"  // optional
        }
    
    
    Returns:
        201: Assignment created successfully
        400: Validation error or employee unavailable
        404: Employee or job not found
        409: Time conflict detected
        500: Server error
    
    Example:
        POST /assign
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
                error="InvalidRequest",
                message="Request body is required"
            )
            return jsonify(error_response.model_dump()), 400
        
        # Validate with Pydantic
        validated_request = AssignmentCreateRequest(**request_data)
        
        # Create assignment through service (enforces all business rules)
        assignment = assignment_service.create_assignment(
            employee_id=validated_request.employeeId,
            job_id=validated_request.jobId,
            notes=validated_request.notes
        )
        
        # Return success response
        response = SuccessResponse(
            message="Assignment created successfully",
            data=assignment.model_dump()
        )
        
        return jsonify(response.model_dump()), 201
        
    except ValidationError as e:
        # Handle Pydantic validation errors
        validation_errors = []
        for error in e.errors():
            validation_errors.append(
                ValidationErrorDetail(
                    field='.'.join(str(loc) for loc in error['loc']),
                    message=error['msg'],
                    type=error['type']
                )
            )
        
        error_response = ValidationErrorResponse(
            errors=validation_errors
        )
        return jsonify(error_response.model_dump()), 400
        
    except EmployeeUnavailableError as e:
        # Rule 3: Availability Filtering
        error_response = ErrorResponse(
            error="EmployeeUnavailable",
            message=str(e),
            details={
                "rule": "Rule 3 - Availability Filtering",
                "description": "Employee is marked as unavailable"
            }
        )
        return jsonify(error_response.model_dump()), 400
        
    except TimeConflictError as e:
        # Rule 1 & 2: No Double Booking / No Overlapping Time Slots
        error_response = ErrorResponse(
            error="TimeConflict",
            message=str(e),
            details={
                "rule": "Rule 1 & 2 - No Double Booking / No Overlapping Time Slots",
                "conflicts": [conflict.model_dump() for conflict in e.conflicts]
            }
        )
        return jsonify(error_response.model_dump()), 409
        
    except EmployeeNotFoundError as e:
        error_response = ErrorResponse(
            error="EmployeeNotFound",
            message=str(e)
        )
        return jsonify(error_response.model_dump()), 404
        
    except JobNotFoundError as e:
        error_response = ErrorResponse(
            error="JobNotFound",
            message=str(e)
        )
        return jsonify(error_response.model_dump()), 404
        
    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to create assignment",
            details={"error": str(e)}
        )
        return jsonify(error_response.model_dump()), 500


@assignments_bp.route('/<assignment_id>', methods=['DELETE'])
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
        deleted = assignment_service.delete_assignment(assignment_id)
        
        # Return success response
        response = SuccessResponse(
            message="Assignment deleted successfully",
            data={"deletedId": assignment_id}
        )
        
        return jsonify(response.model_dump()), 200
        
    except AssignmentNotFoundError as e:
        error_response = ErrorResponse(
            error="AssignmentNotFound",
            message=str(e)
        )
        return jsonify(error_response.model_dump()), 404
        
    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to delete assignment",
            details={"error": str(e)}
        )
        return jsonify(error_response.model_dump()), 500


@assignments_bp.errorhandler(404)
def assignment_not_found(e):
    """Handle 404 errors for assignment routes."""
    error_response = ErrorResponse(
        error="NotFound",
        message="Assignment endpoint not found"
    )
    return jsonify(error_response.model_dump()), 404