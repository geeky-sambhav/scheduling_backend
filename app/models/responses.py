from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime


class SuccessResponse(BaseModel):
    """Standard success response wrapper."""
    
    success: bool = Field(default=True)
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Assignment created successfully",
                "data": {"id": "ASSIGN001"},
                "timestamp": "2024-01-30T08:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""
    
    success: bool = Field(default=False)
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error context"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "TimeConflict",
                "message": "Employee is already assigned to another job during this time",
                "details": {
                    "conflicts": [
                        {
                            "assignmentId": "ASSIGN001",
                            "jobName": "Morning Shift",
                            "timeRange": "08:00-16:00"
                        }
                    ]
                },
                "timestamp": "2024-01-30T08:00:00"
            }
        }


class ValidationErrorDetail(BaseModel):
    """Individual validation error detail."""
    
    field: str
    message: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Response for validation errors (422)."""
    
    success: bool = Field(default=False)
    error: str = Field(default="ValidationError")
    message: str = Field(default="Request validation failed")
    errors: List[ValidationErrorDetail]
    timestamp: datetime = Field(default_factory=datetime.now)


class ConflictDetail(BaseModel):
    """Details about a scheduling conflict."""
    
    assignmentId: str
    jobId: str
    jobName: str
    startTime: datetime
    endTime: datetime


class TimeConflictResponse(BaseModel):
    """Specific response for time conflict errors."""
    
    success: bool = Field(default=False)
    error: str = Field(default="TimeConflict")
    message: str
    conflicts: List[ConflictDetail]
    timestamp: datetime = Field(default_factory=datetime.now)