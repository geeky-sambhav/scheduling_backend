"""
Pydantic models for request/response validation and serialization.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class EmployeeModel(BaseModel):
    """Model for employee data."""
    
    id: str
    name: str = Field(..., min_length=1, max_length=100)
    role: Literal['TCP', 'LCT', 'Supervisor', 'Operator', 'Technician']
    availability: bool


class JobModel(BaseModel):
    """Model for job data."""
    
    id: str
    name: str = Field(..., min_length=1, max_length=200)
    startTime: str
    endTime: str
    
    @field_validator('startTime', 'endTime')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate time format (HH:MM)."""
        if not cls._is_valid_time(v):
            raise ValueError('Invalid time format. Use HH:MM (24-hour format)')
        return v
    
    @staticmethod
    def _is_valid_time(time_str: str) -> bool:
        """Check if time string is in valid HH:MM format."""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False


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
