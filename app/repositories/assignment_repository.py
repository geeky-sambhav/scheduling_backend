"""
Assignment repository for data access operations.

Handles all assignment/schedule-related database/file I/O operations.
"""

from typing import List, Optional

from flask import current_app

from app.models import Assignment
from app.services.data_service import read_json_file, write_json_file


class AssignmentRepository:
    """Repository for assignment data access operations."""

    def get_all(self) -> List[Assignment]:
        """
        Load all assignments from the data store.

        Returns:
            List of Assignment model instances
        """
        data = read_json_file(current_app.config["SCHEDULE_FILE"])
        if data is None:
            return []
        return [Assignment(**item) for item in data]

    def get_by_id(self, assignment_id: str) -> Optional[Assignment]:
        """
        Get a single assignment by ID.

        Args:
            assignment_id: Unique assignment identifier

        Returns:
            Assignment object if found, None otherwise
        """
        assignments = self.get_all()
        return next((a for a in assignments if a.id == assignment_id), None)

    def get_by_employee_id(self, employee_id: str) -> Optional[Assignment]:
        """
        Get the assignment for a specific employee.

        Args:
            employee_id: Employee identifier

        Returns:
            Assignment object for the employee, or None if not found
        """
        assignments = self.get_all()
        return next((a for a in assignments if a.employeeId == employee_id), None)

    def get_by_job_id(self, job_id: str) -> List[Assignment]:
        """
        Get all assignments for a specific job.

        Args:
            job_id: Job identifier

        Returns:
            List of Assignment objects for the job
        """
        assignments = self.get_all()
        return [a for a in assignments if a.jobId == job_id]

    def save_all(self, assignments: List[Assignment]) -> None:
        """
        Save all assignments to the data store.

        Args:
            assignments: List of Assignment objects to save
        """
        data = [a.model_dump(mode="json") for a in assignments]
        write_json_file(current_app.config["SCHEDULE_FILE"], data)

    def create(self, assignment: Assignment) -> Assignment:
        """
        Create a new assignment.

        Args:
            assignment: Assignment object to create

        Returns:
            The created Assignment object
        """
        assignments = self.get_all()
        assignments.append(assignment)
        self.save_all(assignments)
        return assignment

    def update(self, assignment: Assignment) -> Optional[Assignment]:
        """
        Update an existing assignment.

        Args:
            assignment: Assignment object with updated data

        Returns:
            The updated Assignment object, or None if not found
        """
        assignments = self.get_all()
        for i, a in enumerate(assignments):
            if a.id == assignment.id:
                assignments[i] = assignment
                self.save_all(assignments)
                return assignment
        return None

    def delete(self, assignment_id: str) -> bool:
        """
        Delete an assignment by ID.

        Args:
            assignment_id: ID of the assignment to delete

        Returns:
            True if deleted, False if not found
        """
        assignments = self.get_all()
        original_count = len(assignments)
        assignments = [a for a in assignments if a.id != assignment_id]

        if len(assignments) < original_count:
            self.save_all(assignments)
            return True
        return False

    def exists(self, employee_id: str, job_id: str) -> bool:
        """
        Check if an assignment already exists for an employee-job pair.

        Args:
            employee_id: Employee identifier
            job_id: Job identifier

        Returns:
            True if assignment exists, False otherwise
        """
        assignments = self.get_all()
        return any(
            a.employeeId == employee_id and a.jobId == job_id for a in assignments
        )
