import logging
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime

from app.models import Assignment, ConflictDetail
from app.repositories import EmployeeRepository, JobRepository, AssignmentRepository

logger = logging.getLogger(__name__)


class AssignmentService:
    """
    Service layer for assignment business logic.


    """

    def __init__(
        self,
        employee_repo: EmployeeRepository = None,
        job_repo: JobRepository = None,
        assignment_repo: AssignmentRepository = None,
    ):
        """
        Initialize the service with repositories.


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

        # Rule 1: Check for double booking (same employee-job pair already exists)
        if self.assignment_repo.exists(employee_id, job_id):
            logger.warning(
                f"Assignment rejected (Double Booking): "
                f"Employee {employee.name} already assigned to job {job.name}"
            )
            return None, {
                "error_type": "DoubleBooking",
                "message": f"Employee '{employee.name}' is already assigned to '{job.name}'",
                "status_code": 409,
            }

        # Rule 2: Check for time overlap with ALL existing assignments for this employee
        existing_assignments = self.assignment_repo.get_all_by_employee_id(employee_id)

        for existing_assignment in existing_assignments:
            existing_job = self.job_repo.get_by_id(existing_assignment.jobId)
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


        """
        return self.assignment_repo.get_by_employee_id(employee_id)

    def get_assignment_by_id(self, assignment_id: str) -> Optional[Assignment]:
        """
        Get an assignment by ID.

        """
        return self.assignment_repo.get_by_id(assignment_id)
