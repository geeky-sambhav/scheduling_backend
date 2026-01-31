"""
Business logic service for scheduling operations.
Enforces scheduling rules and constraints.
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

from flask import current_app

from app.models import (
    Employee,
    Job,
    Assignment,
    AssignmentWithDetails,
    EmployeeBasic,
    JobBasic
)
from app.services.data_service import read_json_file, write_json_file
from app.services.employee_service import _load_employees
from app.services.job_service import _load_jobs
from app.utils.exceptions import (
    DoubleBookingError,
    TimeOverlapError,
    EmployeeUnavailableError,
    ResourceNotFoundError
)

logger = logging.getLogger(__name__)


# =============================================================================
# Data loading helpers
# =============================================================================

def _load_assignments() -> List[Assignment]:
    """Load all assignments as Pydantic model instances."""
    data = read_json_file(current_app.config['SCHEDULE_FILE'])
    return [Assignment(**a) for a in data]


def _save_assignments(assignments: List[Assignment]) -> None:
    """Save assignments to the JSON file."""
    data = [a.model_dump(mode='json') for a in assignments]
    write_json_file(current_app.config['SCHEDULE_FILE'], data)


def _get_employee_by_id(employee_id: str) -> Optional[Employee]:
    """Get a single employee by ID."""
    employees = _load_employees()
    return next((e for e in employees if e.id == employee_id), None)


def _get_job_by_id(job_id: str) -> Optional[Job]:
    """Get a single job by ID."""
    jobs = _load_jobs()
    return next((j for j in jobs if j.id == job_id), None)


# =============================================================================
# Time overlap helpers
# =============================================================================

def _parse_time(time_str: str) -> Tuple[int, int]:
    """
    Parse time string to hours and minutes.
    
    Args:
        time_str: Time in HH:MM format
        
    Returns:
        Tuple of (hours, minutes)
    """
    parts = time_str.split(':')
    return int(parts[0]), int(parts[1])


def _time_to_minutes(time_str: str) -> int:
    """Convert time string to total minutes since midnight."""
    hours, minutes = _parse_time(time_str)
    return hours * 60 + minutes


def _times_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    """
    Check if two time ranges overlap.
    
    Args:
        start1, end1: First time range
        start2, end2: Second time range
        
    Returns:
        True if the ranges overlap
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


# =============================================================================
# Assignment validation and creation
# =============================================================================

def validate_assignment(employee_id: str, job_id: str) -> Tuple[Employee, Job]:
    """
    Validate that an assignment can be made.
    
    Enforces:
    - Rule 1: No Double Booking
    - Rule 2: No Overlapping Time Slots
    - Rule 3: Availability Filtering
    
    Args:
        employee_id: ID of the employee to assign
        job_id: ID of the job to assign
        
    Returns:
        Tuple of (employee, job) if validation passes
        
    Raises:
        ResourceNotFoundError: If employee or job not found
        EmployeeUnavailableError: If employee is unavailable
        DoubleBookingError: If employee is already assigned to this job
        TimeOverlapError: If new job overlaps with existing assignments
    """
    # Get employee and validate existence
    employee = _get_employee_by_id(employee_id)
    if not employee:
        raise ResourceNotFoundError('Employee', employee_id)
    
    # Get job and validate existence
    job = _get_job_by_id(job_id)
    if not job:
        raise ResourceNotFoundError('Job', job_id)
    
    # Rule 3: Check employee availability
    if not employee.availability:
        logger.warning(f"Assignment rejected: Employee {employee.name} is unavailable")
        raise EmployeeUnavailableError(employee.name)
    
    # Get existing assignments for this employee
    assignments = _load_assignments()
    employee_assignments = [a for a in assignments if a.employeeId == employee_id]
    
    for assignment in employee_assignments:
        existing_job = _get_job_by_id(assignment.jobId)
        if not existing_job:
            continue
        
        # Rule 1: Check for double booking (same job)
        if assignment.jobId == job_id:
            logger.warning(
                f"Assignment rejected: Employee {employee.name} "
                f"already assigned to job {job.name}"
            )
            raise DoubleBookingError(employee.name, job.name)
        
        # Rule 2: Check for time overlap
        if _times_overlap(
            job.startTime, job.endTime,
            existing_job.startTime, existing_job.endTime
        ):
            logger.warning(
                f"Assignment rejected: Time overlap for {employee.name} "
                f"between {job.name} and {existing_job.name}"
            )
            raise TimeOverlapError(employee.name, existing_job.name, job.name)
    
    logger.info(f"Validation passed for assigning {employee.name} to {job.name}")
    return employee, job


def create_assignment(employee_id: str, job_id: str, notes: Optional[str] = None) -> Assignment:
    """
    Create a new assignment after validation.
    
    Args:
        employee_id: ID of the employee to assign
        job_id: ID of the job to assign
        notes: Optional notes for the assignment
        
    Returns:
        The created assignment
    """
    # Validate the assignment (will raise exception if invalid)
    employee, job = validate_assignment(employee_id, job_id)
    
    # Create the assignment
    new_assignment = Assignment(
        employeeId=employee_id,
        jobId=job_id,
        notes=notes
    )
    
    # Save to data store
    assignments = _load_assignments()
    assignments.append(new_assignment)
    _save_assignments(assignments)
    
    logger.info(
        f"Created assignment {new_assignment.id}: "
        f"{employee.name} -> {job.name}"
    )
    
    return new_assignment


def delete_assignment(assignment_id: str) -> bool:
    """
    Delete an assignment.
    
    Args:
        assignment_id: ID of the assignment to delete
        
    Returns:
        True if deleted successfully
        
    Raises:
        ResourceNotFoundError: If assignment not found
    """
    assignments = _load_assignments()
    
    assignment = next((a for a in assignments if a.id == assignment_id), None)
    if not assignment:
        raise ResourceNotFoundError('Assignment', assignment_id)
    
    assignments = [a for a in assignments if a.id != assignment_id]
    _save_assignments(assignments)
    
    logger.info(f"Deleted assignment {assignment_id}")
    return True


def get_schedule_with_details() -> List[Dict[str, Any]]:
    """
    Get schedule with employee and job details included (dict format).
    
    Returns:
        List of assignments with employee and job information as dicts
    """
    assignments = _load_assignments()
    detailed_schedule = []
    
    for assignment in assignments:
        employee = _get_employee_by_id(assignment.employeeId)
        job = _get_job_by_id(assignment.jobId)
        
        detailed_assignment = {
            **assignment.model_dump(mode='json'),
            'employee': employee.model_dump(mode='json') if employee else None,
            'job': job.model_dump(mode='json') if job else None
        }
        detailed_schedule.append(detailed_assignment)
    
    return detailed_schedule


# =============================================================================
# Service class
# =============================================================================

class ScheduleService:
    """Service layer for schedule business logic."""
    
    def get_enriched_assignments(self) -> List[AssignmentWithDetails]:
        """
        Get all assignments with full employee and job details.
        
        Returns:
            List of AssignmentWithDetails objects, sorted by assignedAt (most recent first)
        """
        assignments = _load_assignments()
        employees = _load_employees()
        jobs = _load_jobs()
        
        enriched_assignments = []
        
        for assignment in assignments:
            # Find the employee
            employee = next(
                (emp for emp in employees if emp.id == assignment.employeeId),
                None
            )
            
            # Find the job
            job = next(
                (j for j in jobs if j.id == assignment.jobId),
                None
            )
            
            # Create enriched assignment object
            enriched = AssignmentWithDetails(
                id=assignment.id,
                employeeId=assignment.employeeId,
                jobId=assignment.jobId,
                assignedAt=assignment.assignedAt,
                notes=assignment.notes,
                employee=EmployeeBasic(
                    id=employee.id,
                    name=employee.name,
                    role=employee.role
                ) if employee else None,
                job=JobBasic(
                    id=job.id,
                    name=job.name,
                    startTime=job.startTime,
                    endTime=job.endTime
                ) if job else None
            )
            
            enriched_assignments.append(enriched)
        
        # Sort by assignment time (most recent first)
        enriched_assignments.sort(key=lambda a: a.assignedAt, reverse=True)
        
        return enriched_assignments
