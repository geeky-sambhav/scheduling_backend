"""
Job repository for data access operations.

Handles all job-related database/file I/O operations.
"""

from typing import List, Optional

from flask import current_app

from app.models import Job
from app.services.data_service import read_json_file, write_json_file


class JobRepository:
    """Repository for job data access operations."""

    def get_all(self) -> List[Job]:
        """
        Load all jobs from the data store.

        Returns:
            List of Job model instances
        """
        data = read_json_file(current_app.config["JOBS_FILE"])
        return [Job(**job) for job in data]

    def get_by_id(self, job_id: str) -> Optional[Job]:
        """
        Get a single job by ID.

        Args:
            job_id: Unique job identifier

        Returns:
            Job object if found, None otherwise
        """
        jobs = self.get_all()
        return next((j for j in jobs if j.id == job_id), None)

    def save_all(self, jobs: List[Job]) -> None:
        """
        Save all jobs to the data store.

        Args:
            jobs: List of Job objects to save
        """
        data = [job.model_dump(mode="json") for job in jobs]
        write_json_file(current_app.config["JOBS_FILE"], data)

    def create(self, job: Job) -> Job:
        """
        Create a new job.

        Args:
            job: Job object to create

        Returns:
            The created Job object
        """
        jobs = self.get_all()
        jobs.append(job)
        self.save_all(jobs)
        return job

    def update(self, job: Job) -> Optional[Job]:
        """
        Update an existing job.

        Args:
            job: Job object with updated data

        Returns:
            The updated Job object, or None if not found
        """
        jobs = self.get_all()
        for i, j in enumerate(jobs):
            if j.id == job.id:
                jobs[i] = job
                self.save_all(jobs)
                return job
        return None

    def delete(self, job_id: str) -> bool:
        """
        Delete a job by ID.

        Args:
            job_id: ID of the job to delete

        Returns:
            True if deleted, False if not found
        """
        jobs = self.get_all()
        original_count = len(jobs)
        jobs = [j for j in jobs if j.id != job_id]

        if len(jobs) < original_count:
            self.save_all(jobs)
            return True
        return False
