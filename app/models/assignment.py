from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from uuid import uuid4


class Assignment(BaseModel):
    """
    Assignment model linking employees to jobs with timestamp tracking.
    
    Attributes:
        id: Unique identifier for the assignment
        employeeId: Reference to Employee.id
        jobId: Reference to Job.id
        assignedAt: Timestamp when assignment was created
        notes: Optional notes about the assignment
    """
    
    id: str = Field(
        default_factory=lambda: f"ASSIGN{uuid4().hex[:8].upper()}",
        description="Unique assignment identifier"
    )
    employeeId: str = Field(
        ...,
        min_length=1,
        description="ID of the assigned employee"
    )
    jobId: str = Field(
        ...,
        min_length=1,
        description="ID of the assigned job"
    )
    assignedAt: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of assignment creation"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional notes about this assignment"
    )
    
    @field_validator('employeeId', 'jobId')
    @classmethod
    def validate_ids(cls, v: str) -> str:
        """Ensure IDs are not empty."""
        if not v.strip():
            raise ValueError("ID cannot be empty or only whitespace")
        return v.strip()
    
    class Config:
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "id": "ASSIGN001",
                "employeeId": "EMP001",
                "jobId": "JOB001",
                "assignedAt": "2024-01-30T07:30:00",
                "notes": "Regular assignment"
            }
        }


class AssignmentWithDetails(BaseModel):
    """
    Extended assignment model with full employee and job details.
    Used for API responses that need complete information.
    """
    
    id: str
    employeeId: str
    jobId: str
    assignedAt: datetime
    notes: Optional[str] = None
    
    # Nested details
    employee: Optional['EmployeeBasic'] = None
    job: Optional['JobBasic'] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ASSIGN001",
                "employeeId": "EMP001",
                "jobId": "JOB001",
                "assignedAt": "2024-01-30T07:30:00",
                "employee": {
                    "id": "EMP001",
                    "name": "John Doe",
                    "role": "TCP"
                },
                "job": {
                    "id": "JOB001",
                    "name": "Morning Shift",
                    "startTime": "2024-01-30T08:00:00",
                    "endTime": "2024-01-30T16:00:00"
                }
            }
        }


# Lightweight models for nested responses (avoid circular imports)
class EmployeeBasic(BaseModel):
    """Basic employee info for nested responses."""
    id: str
    name: str
    role: str


class JobBasic(BaseModel):
    """Basic job info for nested responses."""
    id: str
    name: str
    startTime: datetime
    endTime: datetime