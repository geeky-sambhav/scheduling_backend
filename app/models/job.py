from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from uuid import uuid4


class Job(BaseModel):








    """
    Job model with time validation and conflict detection support.

    Attributes:
        id: Unique identifier for the job
        name: Descriptive name of the job/shift
        startTime: ISO format start datetime
        endTime: ISO format end datetime
    """

    id: str = Field(
        default_factory=lambda: f"JOB{uuid4().hex[:8].upper()}",
        description="Unique job identifier",
    )
    name: str = Field(
        ..., min_length=3, max_length=200, description="Job or shift name"
    )
    startTime: datetime = Field(..., description="Job start time in ISO 8601 format")
    endTime: datetime = Field(..., description="Job end time in ISO 8601 format")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure job name is properly formatted."""
        if not v.strip():
            raise ValueError("Job name cannot be empty or only whitespace")
        return v.strip()

    @model_validator(mode="after")
    def validate_time_range(self) -> "Job":
        """Ensure end time is after start time and duration is reasonable."""
        if self.endTime <= self.startTime:
            raise ValueError("End time must be after start time")

        # Check duration is not too long (e.g., max 24 hours)
        duration = (self.endTime - self.startTime).total_seconds() / 3600
        if duration > 24:
            raise ValueError("Job duration cannot exceed 24 hours")

        # Check minimum duration (e.g., at least 30 minutes)
        if duration < 0.5:
            raise ValueError("Job duration must be at least 30 minutes")

        return self

    class Config:
        validate_assignment = True
       

    def get_duration_hours(self) -> float:
        """Calculate job duration in hours."""
        return (self.endTime - self.startTime).total_seconds() / 3600

    def overlaps_with(self, other: "Job") -> bool:
        """
        Check if this job overlaps with another job's time window.

        Args:
            other: Another Job instance to compare against

        Returns:
            True if time windows overlap, False otherwise
        """
        return (self.startTime < other.endTime) and (self.endTime > other.startTime)
