"""
Custom validators and validation utilities for business rules.
"""

from typing import List, Tuple, Optional
from datetime import datetime
from app.models.job import Job
from app.models.assignment import Assignment


class TimeValidator:
    """Utility class for time-related validations."""
    
    @staticmethod
    def check_overlap(
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """
        Check if two time ranges overlap.
        
        Args:
            start1: Start of first time range
            end1: End of first time range
            start2: Start of second time range
            end2: End of second time range
            
        Returns:
            True if ranges overlap, False otherwise
        """
        return (start1 < end2) and (end1 > start2)
    
    @staticmethod
    def find_conflicts(
        job: Job,
        existing_jobs: List[Job]
    ) -> List[Job]:
        """
        Find all jobs that conflict with the given job.
        
        Args:
            job: Job to check for conflicts
            existing_jobs: List of jobs to check against
            
        Returns:
            List of conflicting jobs
        """
        conflicts = []
        for existing_job in existing_jobs:
            if TimeValidator.check_overlap(
                job.startTime,
                job.endTime,
                existing_job.startTime,
                existing_job.endTime
            ):
                conflicts.append(existing_job)
        return conflicts
    
    @staticmethod
    def get_available_slots(
        blocked_jobs: List[Job],
        start_date: datetime,
        end_date: datetime
    ) -> List[Tuple[datetime, datetime]]:
        """
        Calculate available time slots given blocked jobs.
        
        Args:
            blocked_jobs: List of jobs that block time
            start_date: Start of time range to consider
            end_date: End of time range to consider
            
        Returns:
            List of (start, end) tuples representing free slots
        """
        # Sort jobs by start time
        sorted_jobs = sorted(blocked_jobs, key=lambda j: j.startTime)
        
        available = []
        current = start_date
        
        for job in sorted_jobs:
            if job.startTime > current:
                available.append((current, job.startTime))
            current = max(current, job.endTime)
        
        if current < end_date:
            available.append((current, end_date))
        
        return available


class AssignmentValidator:
    """Utility class for assignment-related validations."""
    
    @staticmethod
    def parse_datetime(dt_str: str) -> datetime:
        """
        Parse datetime string to datetime object.
        
        Args:
            dt_str: ISO 8601 datetime string
            
        Returns:
            datetime object
            
        Raises:
            ValueError: If string is not valid ISO 8601 format
        """
        try:
            # Try ISO format with timezone
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            # Try basic ISO format
            return datetime.fromisoformat(dt_str)
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """
        Format datetime object to ISO 8601 string.
        
        Args:
            dt: datetime object
            
        Returns:
            ISO 8601 formatted string
        """
        return dt.isoformat()