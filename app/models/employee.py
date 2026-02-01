from pydantic import BaseModel, Field, field_validator
from typing import Literal
from uuid import uuid4


class Employee(BaseModel):
    """
    Employee model with role-based validation and availability tracking.
    """

    id: str = Field(
        default_factory=lambda: f"EMP{uuid4().hex[:8].upper()}",
        description="Unique employee identifier",
    )
    name: str = Field(
        ..., min_length=2, max_length=100, description="Employee full name"
    )
    role: Literal["TCP", "LCT", "Supervisor"] = Field(
        ..., description="Employee role type"
    )
    availability: bool = Field(
        default=True, description="Whether employee is available for assignments"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name contains only valid characters and is properly formatted."""
        if not v.strip():
            raise ValueError("Name cannot be empty or only whitespace")

        # Remove extra spaces
        cleaned = " ".join(v.split())

        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not all(c.isalpha() or c in " -'" for c in cleaned):
            raise ValueError("Name contains invalid characters")

        return cleaned

    class Config:
        # Allow validation on assignment
        validate_assignment = True

    def mark_unavailable(self) -> None:
        """Mark employee as unavailable."""
        self.availability = False

    def mark_available(self) -> None:
        """Mark employee as available."""
        self.availability = True
