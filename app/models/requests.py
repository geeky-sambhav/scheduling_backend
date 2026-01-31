from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AssignmentCreateRequest(BaseModel):
    """
    Request model for creating a new assignment.
    Used to validate incoming POST /assign requests.
    """

    employeeId: str = Field(..., min_length=1, description="ID of employee to assign")
    jobId: str = Field(..., min_length=1, description="ID of job to assign to")

    class Config:
        json_schema_extra = {"example": {"employeeId": "EMP001", "jobId": "JOB001"}}


class EmployeeCreateRequest(BaseModel):
    """Request model for creating a new employee."""

    name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., pattern="^(TCP|LCT|Supervisor)$")
    availability: bool = Field(default=True)


class JobCreateRequest(BaseModel):
    """Request model for creating a new job."""

    name: str = Field(..., min_length=3, max_length=200)
    startTime: datetime = Field(..., description="ISO 8601 datetime string")
    endTime: datetime = Field(..., description="ISO 8601 datetime string")
    description: Optional[str] = Field(default=None, max_length=500)
