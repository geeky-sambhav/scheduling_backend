"""
Job business logic service.

Handles all job-related operations including:
- Retrieving jobs with filtering
- Getting individual jobs by ID
- Finding upcoming jobs
- Computing job statistics
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from flask import current_app

from app.models import Job
from app.models.validators import AssignmentValidator
from app.services.data_service import read_json_file
from app.utils.exceptions import ResourceNotFoundError


class InvalidDateTimeError(Exception):
    """Raised when an invalid datetime string is provided."""
    
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(
            f"Invalid {field} format. Use ISO 8601 format (e.g., 2024-01-30T08:00:00)"
        )


class InvalidParameterError(Exception):
    """Raised when an invalid parameter value is provided."""
    
    def __init__(self, field: str, value: str, expected_type: str = "number"):
        self.field = field
        self.value = value
        self.expected_type = expected_type
        super().__init__(f"{field} must be a valid {expected_type}")


def _load_jobs() -> List[Job]:
    """Load all jobs as Pydantic model instances."""
    data = read_json_file(current_app.config['JOBS_FILE'])
    return [Job(**job) for job in data]


class JobService:
    """Service layer for job business logic."""
    
    def get_all_jobs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_duration: Optional[str] = None,
        max_duration: Optional[str] = None
    ) -> List[Job]:
        """
        Get all jobs with optional filtering.
        
        Args:
            start_date: Filter jobs starting after this date (ISO 8601 string)
            end_date: Filter jobs ending before this date (ISO 8601 string)
            min_duration: Minimum duration in hours (string to parse)
            max_duration: Maximum duration in hours (string to parse)
        
        Returns:
            List of filtered Job objects, sorted by start time (most recent first)
        
        Raises:
            InvalidDateTimeError: If date format is invalid
            InvalidParameterError: If duration is not a valid number
        """
        jobs = _load_jobs()
        
        # Filter by start date
        if start_date:
            try:
                parsed_start = AssignmentValidator.parse_datetime(start_date)
                jobs = [job for job in jobs if job.startTime >= parsed_start]
            except ValueError:
                raise InvalidDateTimeError("startDate", start_date)
        
        # Filter by end date
        if end_date:
            try:
                parsed_end = AssignmentValidator.parse_datetime(end_date)
                jobs = [job for job in jobs if job.endTime <= parsed_end]
            except ValueError:
                raise InvalidDateTimeError("endDate", end_date)
        
        # Filter by minimum duration
        if min_duration:
            try:
                min_hours = float(min_duration)
                jobs = [job for job in jobs if job.get_duration_hours() >= min_hours]
            except ValueError:
                raise InvalidParameterError("minDuration", min_duration)
        
        # Filter by maximum duration
        if max_duration:
            try:
                max_hours = float(max_duration)
                jobs = [job for job in jobs if job.get_duration_hours() <= max_hours]
            except ValueError:
                raise InvalidParameterError("maxDuration", max_duration)
        
        # Sort by start time (most recent first)
        jobs.sort(key=lambda j: j.startTime, reverse=True)
        
        return jobs
    
    def get_job_by_id(self, job_id: str) -> Job:
        """
        Get a single job by ID.
        
        Args:
            job_id: Unique job identifier
        
        Returns:
            Job object
        
        Raises:
            ResourceNotFoundError: If job not found
        """
        jobs = _load_jobs()
        
        job = next(
            (j for j in jobs if j.id == job_id),
            None
        )
        
        if not job:
            raise ResourceNotFoundError("Job", job_id)
        
        return job
    
    def get_job_with_duration(self, job_id: str) -> Dict[str, Any]:
        """
        Get a single job by ID with calculated duration.
        
        Args:
            job_id: Unique job identifier
        
        Returns:
            Job data dict with durationHours field
        
        Raises:
            ResourceNotFoundError: If job not found
        """
        job = self.get_job_by_id(job_id)
        job_data = job.model_dump()
        job_data['durationHours'] = job.get_duration_hours()
        return job_data
    
    def get_upcoming_jobs(self, hours_ahead: int = 24) -> List[Job]:
        """
        Get jobs scheduled to start in the future.
        
        Args:
            hours_ahead: Number of hours to look ahead (currently unused, 
                        returns all future jobs sorted by soonest first)
        
        Returns:
            List of upcoming jobs, sorted by start time (soonest first)
        """
        jobs = _load_jobs()
        now = datetime.now()
        
        # Filter for upcoming jobs
        upcoming = [job for job in jobs if job.startTime > now]
        
        # Sort by start time (soonest first)
        upcoming.sort(key=lambda j: j.startTime)
        
        return upcoming
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate job statistics and summary.
        
        Returns:
            Dictionary containing:
            - totalJobs: Total job count
            - averageDurationHours: Average duration
            - shortestDurationHours: Minimum duration
            - longestDurationHours: Maximum duration
            - totalHours: Sum of all durations
        """
        jobs = _load_jobs()
        
        if not jobs:
            return {
                'totalJobs': 0,
                'averageDurationHours': 0,
                'shortestDurationHours': 0,
                'longestDurationHours': 0
            }
        
        durations = [job.get_duration_hours() for job in jobs]
        
        return {
            'totalJobs': len(jobs),
            'averageDurationHours': round(sum(durations) / len(durations), 2),
            'shortestDurationHours': round(min(durations), 2),
            'longestDurationHours': round(max(durations), 2),
            'totalHours': round(sum(durations), 2)
        }
