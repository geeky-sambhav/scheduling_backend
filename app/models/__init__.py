"""
Pydantic models for the Employee Scheduler application.

This module provides strongly-typed, validated data models for:
- Employees
- Jobs
- Assignments
- API requests and responses
"""

from app.models.employee import Employee
from app.models.job import Job
from app.models.assignment import (
    Assignment,
    AssignmentWithDetails,
    EmployeeBasic,
    JobBasic,
)
from app.models.requests import (
    AssignmentCreateRequest,
    EmployeeCreateRequest,
    JobCreateRequest,
)
from app.models.responses import (
    SuccessResponse,
    ErrorResponse,
    ValidationErrorResponse,
    ValidationErrorDetail,
    TimeConflictResponse,
    ConflictDetail,
)

__all__ = [
    # Core models
    "Employee",
    "Job",
    "Assignment",
    "AssignmentWithDetails",
    "EmployeeBasic",
    "JobBasic",
    # Request models
    "AssignmentCreateRequest",
    "EmployeeCreateRequest",
    "JobCreateRequest",
    # Response models
    "SuccessResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    "ValidationErrorDetail",
    "TimeConflictResponse",
    "ConflictDetail",
]
