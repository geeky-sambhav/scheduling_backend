"""
Business logic service for scheduling operations.
Enforces scheduling rules and constraints.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

from app.models import (
    Employee,
    Job,
    Assignment,
    AssignmentWithDetails,
    EmployeeBasic,
    JobBasic,
)
from app.repositories import EmployeeRepository, JobRepository, AssignmentRepository

logger = logging.getLogger(__name__)


# =============================================================================
# Repository instances
# =============================================================================

_employee_repo = EmployeeRepository()
_job_repo = JobRepository()
_assignment_repo = AssignmentRepository()


def get_assignment_repository() -> AssignmentRepository:
    """Get the assignment repository instance."""
    return _assignment_repo


# =============================================================================
# Time overlap helpers
# =============================================================================


def _parse_time(time_str: str) -> Tuple[int, int]:
    """
    Parse time string to hours and minutes.
    """
    parts = time_str.split(":")
    return int(parts[0]), int(parts[1])


def _time_to_minutes(time_str: str) -> int:
    """Convert time string to total minutes since midnight."""
    hours, minutes = _parse_time(time_str)
    return hours * 60 + minutes


def _times_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    """
    Check if two time ranges overlap.
    """
    start1_min = _time_to_minutes(start1)
    end1_min = _time_to_minutes(end1)
    start2_min = _time_to_minutes(start2)
    end2_min = _time_to_minutes(end2)

    # Handle overnight shifts (end < start)
    if end1_min < start1_min:
        end1_min += 24 * 60
    if end2_min < start2_min:
        end2_min += 24 * 60

    # Check for overlap
    return start1_min < end2_min and start2_min < end1_min


def validate_assignment(
    employee_id: str, job_id: str
) -> Tuple[Optional[Tuple[Employee, Job]], Optional[Dict[str, Any]]]:
    """
    Validate that an assignment can be made.
    """
    # Get employee and validate existence
    employee = _employee_repo.get_by_id(employee_id)
    if not employee:
        return None, {
            "error_type": "EmployeeNotFound",
            "message": f"Employee with id '{employee_id}' not found",
            "status_code": 404,
        }

    # Get job and validate existence
    job = _job_repo.get_by_id(job_id)
    if not job:
        return None, {
            "error_type": "JobNotFound",
            "message": f"Job with id '{job_id}' not found",
            "status_code": 404,
        }

    # Rule 3: Check employee availability
    if not employee.availability:
        logger.warning(f"Assignment rejected: Employee {employee.name} is unavailable")
        return None, {
            "error_type": "EmployeeUnavailable",
            "message": f"Employee '{employee.name}' is currently unavailable for assignment",
            "status_code": 400,
        }

    # Rule 1: Check for double booking (same employee-job pair already exists)
    if _assignment_repo.exists(employee_id, job_id):
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
    existing_assignments = _assignment_repo.get_all_by_employee_id(employee_id)

    for existing_assignment in existing_assignments:
        existing_job = _job_repo.get_by_id(existing_assignment.jobId)
        if existing_job and _times_overlap(
            job.startTime, job.endTime, existing_job.startTime, existing_job.endTime
        ):
            logger.warning(
                f"Assignment rejected: Time overlap for {employee.name} "
                f"between {job.name} and {existing_job.name}"
            )
            return None, {
                "error_type": "TimeOverlap",
                "message": f"Time conflict for employee '{employee.name}': '{job.name}' overlaps with existing assignment '{existing_job.name}'",
                "status_code": 409,
            }

    logger.info(f"Validation passed for assigning {employee.name} to {job.name}")
    return (employee, job), None


def create_assignment(
    employee_id: str, job_id: str, notes: Optional[str] = None
) -> Tuple[Optional[Assignment], Optional[Dict[str, Any]]]:
    """
    Create a new assignment after validation
    """
    # Validate the assignment
    validation_result, error = validate_assignment(employee_id, job_id)
    if error:
        return None, error

    employee, job = validation_result

    # Create the assignment
    new_assignment = Assignment(employeeId=employee_id, jobId=job_id, notes=notes)

    # Save to data store
    _assignment_repo.create(new_assignment)

    logger.info(
        f"Created assignment {new_assignment.id}: " f"{employee.name} -> {job.name}"
    )

    return new_assignment, None


def delete_assignment(
    assignment_id: str,
) -> Tuple[Optional[bool], Optional[Dict[str, Any]]]:
    """
    Delete an assignment.
    """
    assignment = _assignment_repo.get_by_id(assignment_id)
    if not assignment:
        return None, {
            "error_type": "AssignmentNotFound",
            "message": f"Assignment with id '{assignment_id}' not found",
            "status_code": 404,
        }

    _assignment_repo.delete(assignment_id)

    logger.info(f"Deleted assignment {assignment_id}")
    return True, None


def get_schedule_with_details() -> List[Dict[str, Any]]:
    """
    Get schedule with employee and job details included (dict format).
    """
    assignments = _assignment_repo.get_all()
    detailed_schedule = []

    for assignment in assignments:
        employee = _employee_repo.get_by_id(assignment.employeeId)
        job = _job_repo.get_by_id(assignment.jobId)

        detailed_assignment = {
            **assignment.model_dump(mode="json"),
            "employee": employee.model_dump(mode="json") if employee else None,
            "job": job.model_dump(mode="json") if job else None,
        }
        detailed_schedule.append(detailed_assignment)

    return detailed_schedule


class ScheduleService:
    """Service layer for schedule business logic."""

    def __init__(
        self,
        employee_repo: EmployeeRepository = None,
        job_repo: JobRepository = None,
        assignment_repo: AssignmentRepository = None,
    ):
        """
        Initialize the service with repositories.
        """
        self.employee_repo = employee_repo or _employee_repo
        self.job_repo = job_repo or _job_repo
        self.assignment_repo = assignment_repo or _assignment_repo

    def get_enriched_assignments(self) -> List[AssignmentWithDetails]:
        """
        Get all assignments with full employee and job details.
        """
        assignments = self.assignment_repo.get_all()
        employees = self.employee_repo.get_all()
        jobs = self.job_repo.get_all()

        enriched_assignments = []

        for assignment in assignments:
            # Find the employee
            employee = next(
                (emp for emp in employees if emp.id == assignment.employeeId), None
            )

            # Find the job
            job = next((j for j in jobs if j.id == assignment.jobId), None)

            # Create enriched assignment object
            enriched = AssignmentWithDetails(
                id=assignment.id,
                assignedAt=assignment.assignedAt,
                employee=(
                    EmployeeBasic(
                        id=employee.id, name=employee.name, role=employee.role
                    )
                    if employee
                    else None
                ),
                job=(
                    JobBasic(
                        id=job.id,
                        name=job.name,
                        startTime=job.startTime,
                        endTime=job.endTime,
                    )
                    if job
                    else None
                ),
            )

            enriched_assignments.append(enriched)

        # Sort by assignment time (most recent first)
        enriched_assignments.sort(key=lambda a: a.assignedAt, reverse=True)

        return enriched_assignments
