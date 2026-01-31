"""
Job business logic service.

Handles all job-related operations including:
- Retrieving jobs with filtering
- Getting individual jobs by ID
- Finding upcoming jobs
- Computing job statistics
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from app.models import Job
from app.models.validators import AssignmentValidator
from app.repositories import JobRepository


# Shared repository instance
_job_repo = JobRepository()


def get_job_repository() -> JobRepository:
    """Get the job repository instance."""
    return _job_repo


class JobService:
    """Service layer for job business logic."""

    def __init__(self, repository: JobRepository = None):
        """
        Initialize the service with a repository.

        Args:
            repository: Optional repository instance (uses default if not provided)
        """
        self.repository = repository or _job_repo

    def get_all_jobs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_duration: Optional[str] = None,
        max_duration: Optional[str] = None,
    ) -> Tuple[Optional[List[Job]], Optional[Dict[str, Any]]]:
        """
        Get all jobs with optional filtering.

        Args:
            start_date: Filter jobs starting after this date (ISO 8601 string)
            end_date: Filter jobs ending before this date (ISO 8601 string)
            min_duration: Minimum duration in hours (string to parse)
            max_duration: Maximum duration in hours (string to parse)

        Returns:
            Tuple of (List[Job], None) on success
            Tuple of (None, error_dict) on failure
        """
        jobs = self.repository.get_all()

        # Filter by start date
        if start_date:
            try:
                parsed_start = AssignmentValidator.parse_datetime(start_date)
                jobs = [job for job in jobs if job.startTime >= parsed_start]
            except ValueError:
                return None, {
                    "error_type": "InvalidDateTime",
                    "message": "Invalid startDate format. Use ISO 8601 format (e.g., 2024-01-30T08:00:00)",
                    "status_code": 400,
                    "details": {"providedValue": start_date},
                }

        # Filter by end date
        if end_date:
            try:
                parsed_end = AssignmentValidator.parse_datetime(end_date)
                jobs = [job for job in jobs if job.endTime <= parsed_end]
            except ValueError:
                return None, {
                    "error_type": "InvalidDateTime",
                    "message": "Invalid endDate format. Use ISO 8601 format (e.g., 2024-01-30T08:00:00)",
                    "status_code": 400,
                    "details": {"providedValue": end_date},
                }

        # Filter by minimum duration
        if min_duration:
            try:
                min_hours = float(min_duration)
                jobs = [job for job in jobs if job.get_duration_hours() >= min_hours]
            except ValueError:
                return None, {
                    "error_type": "InvalidParameter",
                    "message": "minDuration must be a valid number",
                    "status_code": 400,
                    "details": {"providedValue": min_duration},
                }

        # Filter by maximum duration
        if max_duration:
            try:
                max_hours = float(max_duration)
                jobs = [job for job in jobs if job.get_duration_hours() <= max_hours]
            except ValueError:
                return None, {
                    "error_type": "InvalidParameter",
                    "message": "maxDuration must be a valid number",
                    "status_code": 400,
                    "details": {"providedValue": max_duration},
                }

        # Sort by start time (most recent first)
        jobs.sort(key=lambda j: j.startTime, reverse=True)

        return jobs, None

    def get_job_by_id(
        self, job_id: str
    ) -> Tuple[Optional[Job], Optional[Dict[str, Any]]]:
        """
        Get a single job by ID.

        Args:
            job_id: Unique job identifier

        Returns:
            Tuple of (Job, None) on success
            Tuple of (None, error_dict) on failure
        """
        job = self.repository.get_by_id(job_id)

        if not job:
            return None, {
                "error_type": "JobNotFound",
                "message": f"Job with id '{job_id}' not found",
                "status_code": 404,
            }

        return job, None

    def get_job_with_duration(
        self, job_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Get a single job by ID with calculated duration.

        Args:
            job_id: Unique job identifier

        Returns:
            Tuple of (job_data_dict, None) on success
            Tuple of (None, error_dict) on failure
        """
        job, error = self.get_job_by_id(job_id)
        if error:
            return None, error

        job_data = job.model_dump()
        job_data["durationHours"] = job.get_duration_hours()
        return job_data, None

    def get_upcoming_jobs(self, hours_ahead: int = 24) -> List[Job]:
        """
        Get jobs scheduled to start in the future.

        Args:
            hours_ahead: Number of hours to look ahead (currently unused,
                        returns all future jobs sorted by soonest first)

        Returns:
            List of upcoming jobs, sorted by start time (soonest first)
        """
        jobs = self.repository.get_all()
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
        jobs = self.repository.get_all()

        if not jobs:
            return {
                "totalJobs": 0,
                "averageDurationHours": 0,
                "shortestDurationHours": 0,
                "longestDurationHours": 0,
            }

        durations = [job.get_duration_hours() for job in jobs]

        return {
            "totalJobs": len(jobs),
            "averageDurationHours": round(sum(durations) / len(durations), 2),
            "shortestDurationHours": round(min(durations), 2),
            "longestDurationHours": round(max(durations), 2),
            "totalHours": round(sum(durations), 2),
        }
