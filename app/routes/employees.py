"""
Employee API routes.
"""

from flask import Blueprint, jsonify

from app.models import SuccessResponse, ErrorResponse
from app.services.employee_service import EmployeeService

# Create blueprint
employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

# Initialize service
employee_service = EmployeeService()


@employees_bp.route('', methods=['GET'])
def get_all_employees():
    """
    Get all employees.
    
    Returns:
        200: List of employees with id, name, role, availability
        500: Server error
    
    Example:
        GET /employees
    """
    try:
        employees = employee_service.get_all_employees()
        
        # Return only id, name, role, availability
        employees_data = [
            {
                "id": emp.id,
                "name": emp.name,
                "role": emp.role,
                "availability": emp.availability
            }
            for emp in employees
        ]
        
        response = SuccessResponse(
            message=f"Retrieved {len(employees_data)} employee(s)",
            data=employees_data
        )
        
        return jsonify(response.model_dump()), 200
        
    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to retrieve employees",
            details={"error": str(e)}
        )
        return jsonify(error_response.model_dump()), 500
