from typing import List, Optional, Tuple, Dict, Any
from app.models import Employee
from app.repositories import EmployeeRepository


VALID_ROLES = ["TCP", "LCT", "Supervisor"]


# Shared repository instance
_employee_repo = EmployeeRepository()


def get_employee_repository() -> EmployeeRepository:
    """Get the employee repository instance."""
    return _employee_repo


class EmployeeService:
    """Service layer for employee business logic."""

    def __init__(self, repository: EmployeeRepository = None):
        """
        Initialize the service with a repository.

        Args:
            repository: Optional repository instance (uses default if not provided)
        """
        self.repository = _employee_repo

    def get_all_employees(
        self,
    ) -> Tuple[Optional[List[Employee]], Optional[Dict[str, Any]]]:
        """
        Get all employees.
        """
        employees = self.repository.get_all()

        return employees, None

    def get_employee_by_id(
        self, employee_id: str
    ) -> Tuple[Optional[Employee], Optional[Dict[str, Any]]]:
        """
        Get a single employee by ID.
        """
        employee = self.repository.get_by_id(employee_id)

        if not employee:
            return None, {
                "error_type": "EmployeeNotFound",
                "message": f"Employee with id '{employee_id}' not found",
                "status_code": 404,
            }

        return employee, None
