"""
Repository layer for data access operations.

Repositories handle all database/file I/O operations,
providing a clean interface for the service layer.
"""

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.job_repository import JobRepository
from app.repositories.assignment_repository import AssignmentRepository

__all__ = [
    "EmployeeRepository",
    "JobRepository",
    "AssignmentRepository",
]
