"""
Employee business logic service.

Handles all employee-related operations including:
- Retrieving employees with filtering
- Getting individual employees by ID
- Computing employee statistics
"""

from typing import List, Optional

from flask import current_app

from app.models import Employee
from app.services.data_service import read_json_file
from app.utils.exceptions import ResourceNotFoundError


VALID_ROLES = ['TCP', 'LCT', 'Supervisor']


class InvalidRoleError(Exception):
    """Raised when an invalid role is provided."""
    
    def __init__(self, role: str):
        self.role = role
        self.valid_roles = VALID_ROLES
        super().__init__(f"Invalid role '{role}'. Must be one of: {', '.join(VALID_ROLES)}")


def _load_employees() -> List[Employee]:
    """Load all employees as Pydantic model instances."""
    data = read_json_file(current_app.config['EMPLOYEES_FILE'])
    return [Employee(**emp) for emp in data]


class EmployeeService:
    """Service layer for employee business logic."""
    
    def get_all_employees(
        self,
        available: Optional[bool] = None,
        role: Optional[str] = None
    ) -> List[Employee]:
        """
        Get all employees with optional filtering.
        
        Args:
            available: Filter by availability (True/False/None for all)
            role: Filter by role (TCP/LCT/Supervisor)
        
        Returns:
            List of filtered Employee objects
        
        Raises:
            InvalidRoleError: If an invalid role is provided
        """
        employees = _load_employees()
        
        # Filter by availability
        if available is not None:
            employees = [emp for emp in employees if emp.availability == available]
        
        # Filter by role
        if role is not None:
            if role not in VALID_ROLES:
                raise InvalidRoleError(role)
            employees = [emp for emp in employees if emp.role == role]
        
        return employees
    
    def get_employee_by_id(self, employee_id: str) -> Employee:
        """
        Get a single employee by ID.
        
        Args:
            employee_id: Unique employee identifier
        
        Returns:
            Employee object
        
        Raises:
            ResourceNotFoundError: If employee not found
        """
        employees = _load_employees()
        employee = next((e for e in employees if e.id == employee_id), None)
        
        if not employee:
            raise ResourceNotFoundError("Employee", employee_id)
        
        return employee
