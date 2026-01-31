"""
Assignment service for handling employee-to-job assignments.

Enforces business rules:
- Rule 1: No Double Booking - Employee cannot be assigned to more than one job at the same time
- Rule 2: No Overlapping Time Slots - Employees cannot be assigned to jobs whose time windows overlap
- Rule 3: Availability Filtering - If an employee is unavailable, assignment is rejected
"""

import logging
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime

from app.models import Assignment, ConflictDetail
from app.repositories import EmployeeRepository, JobRepository, AssignmentRepository

logger = logging.getLogger(__name__)


class AssignmentService:
    """
    Service layer for assignment business logic.

    Enforces scheduling rules:
    - Rule 1: No Double Booking
    - Rule 2: No Overlapping Time Slots
    - Rule 3: Availability Filtering
    """

    def __init__(
        self,
        employee_repo: EmployeeRepository = None,
        job_repo: JobRepository = None,
        assignment_repo: AssignmentRepository = None,
    ):
        """
        Initialize the service with repositories.

        Args:
            employee_repo: Optional employee repository (uses default if not provided)
            job_repo: Optional job repository (uses default if not provided)
            assignment_repo: Optional assignment repository (uses default if not provided)
        """
        self.employee_repo = employee_repo or EmployeeRepository()
        self.job_repo = job_repo or JobRepository()
        self.assignment_repo = assignment_repo or AssignmentRepository()

    def _times_overlap(
        self, start1: datetime, end1: datetime, start2: datetime, end2: datetime
    ) -> bool:

        return start1 < end2 and start2 < end1

    def _validate_assignment(
        self, employee_id: str, job_id: str
    ) -> Tuple[Optional[tuple], Optional[Dict[str, Any]]]:

        # Get employee and validate existence
        employee = self.employee_repo.get_by_id(employee_id)
        if not employee:
            return None, {
                "error_type": "EmployeeNotFound",
                "message": f"Employee with id '{employee_id}' not found",
                "status_code": 404,
            }

        # Get job and validate existence
        job = self.job_repo.get_by_id(job_id)
        if not job:
            return None, {
                "error_type": "JobNotFound",
                "message": f"Job with id '{job_id}' not found",
                "status_code": 404,
            }

        # Rule 3: Check employee availability
        if not employee.availability:
            logger.warning(
                f"Assignment rejected (Availability Filtering): "
                f"Employee {employee.name} is unavailable"
            )
            return None, {
                "error_type": "EmployeeUnavailable",
                "message": f"Employee '{employee.name}' is currently unavailable for assignment",
                "status_code": 400,
            }

        # Get existing assignment for this employee (each employee has at most one)
        existing_assignment = self.assignment_repo.get_by_employee_id(employee_id)

        if existing_assignment:
            existing_job = self.job_repo.get_by_id(existing_assignment.jobId)

            # Rule 1: Check for double booking (same job)
            if existing_assignment.jobId == job_id:
                print("double booki-------------ng")
                logger.warning(
                    f"Employee {employee.name} already assigned to job {job.name}"
                )
                return None, {
                    "error_type": "DoubleBooking",
                    "message": f"Employee '{employee.name}' is already assigned to '{job.name}'",
                    "status_code": 409,
                }

            # Rule 2: Check for time overlap
            if existing_job and self._times_overlap(
                job.startTime, job.endTime, existing_job.startTime, existing_job.endTime
            ):
                logger.warning(
                    f"Assignment rejected (No Overlapping Time Slots): "
                    f"Time overlap for {employee.name} between {job.name} and {existing_job.name}"
                )
                return None, {
                    "error_type": "TimeOverlap",
                    "message": f"Time overlap for {employee.name} between {job.name} and {existing_job.name}",
                    "status_code": 409,
                }

        logger.info(f"Validation passed for assigning {employee.name} to {job.name}")
        return (employee, job), None

    def create_assignment(
        self,
        employee_id: str,
        job_id: str,
    ) -> Tuple[Optional[Assignment], Optional[Dict[str, Any]]]:
        """
        Create a new assignment after validation.

        Enforces all business rules:
        - Rule 1: No Double Booking
        - Rule 2: No Overlapping Time Slots
        - Rule 3: Availability Filtering

        Args:
            employee_id: ID of the employee to assign
            job_id: ID of the job to assign

        Returns:
            Tuple of (Assignment, None) on success
            Tuple of (None, error_dict) on failure
        """
        # Validate the assignment
        validation_result, error = self._validate_assignment(employee_id, job_id)
        if error:
            return None, error

        employee, job = validation_result

        # Create the assignment
        new_assignment = Assignment(
            employeeId=employee_id,
            jobId=job_id,
        )

        # Save to data store
        self.assignment_repo.create(new_assignment)

        logger.info(
            f"Created assignment {new_assignment.id}: " f"{employee.name} -> {job.name}"
        )

        return new_assignment, None

    def delete_assignment(
        self, assignment_id: str
    ) -> Tuple[Optional[bool], Optional[Dict[str, Any]]]:
        """
        Delete an assignment.

        Args:
            assignment_id: ID of the assignment to delete

        Returns:
            Tuple of (True, None) on success
            Tuple of (None, error_dict) on failure
        """
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            return None, {
                "error_type": "AssignmentNotFound",
                "message": f"Assignment with id '{assignment_id}' not found",
                "status_code": 404,
            }

        self.assignment_repo.delete(assignment_id)

        logger.info(f"Deleted assignment {assignment_id}")
        return True, None

    def get_assignment_for_employee(self, employee_id: str) -> Optional[Assignment]:
        """
        Get the assignment for an employee.

        Args:
            employee_id: ID of the employee

        Returns:
            Assignment for the employee, or None if not found
        """
        return self.assignment_repo.get_by_employee_id(employee_id)

    def get_assignment_by_id(self, assignment_id: str) -> Optional[Assignment]:
        """
        Get an assignment by ID.

        Args:
            assignment_id: ID of the assignment

        Returns:
            Assignment if found, None otherwise
        """
        return self.assignment_repo.get_by_id(assignment_id)
