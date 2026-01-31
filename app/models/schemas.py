"""
Pydantic models for request/response validation and serialization.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class EmployeeModel(BaseModel):
    """Model for employee data."""

    id: str
    name: str = Field(..., min_length=1, max_length=100)
    role: Literal["TCP", "LCT", "Supervisor", "Operator", "Technician"]
    availability: bool


class JobModel(BaseModel):
    """Model for job data."""

    id: str
    name: str = Field(..., min_length=1, max_length=200)
    startTime: datetime = Field(..., description="Job start time in ISO 8601 format")
    endTime: datetime = Field(..., description="Job end time in ISO 8601 format")


class AssignmentModel(BaseModel):
    """Model for schedule assignment data."""

    id: str
    employeeId: str
    jobId: str
    assignedAt: Optional[str] = None


class AssignmentDetailedModel(AssignmentModel):
    """Model for assignment with employee and job details."""

    employee: Optional[EmployeeModel] = None
    job: Optional[JobModel] = None


class AssignRequestModel(BaseModel):
    """Model for assignment request validation."""

    employeeId: str = Field(..., description="ID of the employee to assign")
    jobId: str = Field(..., description="ID of the job to assign")


class APIResponse(BaseModel):
    """Standard API response model."""

    success: bool
    data: Optional[dict | list] = None
    message: Optional[str] = None
    error: Optional[str] = None
    details: Optional[dict] = None
