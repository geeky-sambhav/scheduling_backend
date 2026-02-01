from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from uuid import uuid4


class Assignment(BaseModel):
    """
    Assignment model linking employees to jobs with timestamp tracking.
    """

    id: str = Field(
        default_factory=lambda: f"ASSIGN{uuid4().hex[:8].upper()}",
        description="Unique assignment identifier",
    )
    employeeId: str = Field(
        ..., min_length=1, description="ID of the assigned employee"
    )
    jobId: str = Field(..., min_length=1, description="ID of the assigned job")
    assignedAt: datetime = Field(
        default_factory=datetime.now, description="Timestamp of assignment creation"
    )

    @field_validator("employeeId", "jobId")
    @classmethod
    def validate_ids(cls, v: str) -> str:
        """Ensure IDs are not empty."""
        if not v.strip():
            raise ValueError("ID cannot be empty or only whitespace")
        return v.strip()

    class Config:
        validate_assignment = True


class AssignmentWithDetails(BaseModel):
    """
    Extended assignment model with full employee and job details.
    Used for API responses that need complete information.
    """

    id: str
    assignedAt: datetime

    # Nested details
    employee: Optional["EmployeeBasic"] = None
    job: Optional["JobBasic"] = None


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
