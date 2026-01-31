"""
Job API routes.

Handles all job-related endpoints including:
- List all jobs
- Get single job
- Filter jobs by time range
"""

from flask import Blueprint, jsonify, request

from app.models import ErrorResponse, SuccessResponse
from app.services.job_service import (
    JobService,
    InvalidDateTimeError,
    InvalidParameterError
)
from app.utils.exceptions import ResourceNotFoundError

# Create blueprint
jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

# Initialize service
job_service = JobService()


@jobs_bp.route('', methods=['GET'])
def get_all_jobs():
    """
    Get all jobs with optional filtering.
    
    Query Parameters:
        - startDate (str): Filter jobs starting after this date (ISO 8601)
        - endDate (str): Filter jobs ending before this date (ISO 8601)
        - minDuration (float): Minimum duration in hours
        - maxDuration (float): Maximum duration in hours
    
    Returns:
        200: List of jobs
        400: Invalid query parameters
        500: Server error
    
    Example:
        GET /jobs
        GET /jobs?startDate=2024-01-30T08:00:00
        GET /jobs?minDuration=4
        GET /jobs?startDate=2024-01-30T00:00:00&endDate=2024-01-31T00:00:00
    """
    try:
        jobs = job_service.get_all_jobs(
            start_date=request.args.get('startDate'),
            end_date=request.args.get('endDate'),
            min_duration=request.args.get('minDuration'),
            max_duration=request.args.get('maxDuration')
        )
        
        # Convert to dict for JSON response
        jobs_data = [job.model_dump() for job in jobs]
        
        response = SuccessResponse(
            message=f"Retrieved {len(jobs_data)} job(s)",
            data=jobs_data
        )
        
        return jsonify(response.model_dump()), 200
    
    except InvalidDateTimeError as e:
        error_response = ErrorResponse(
            error="InvalidDateTime",
            message=str(e),
            details={"providedValue": e.value}
        )
        return jsonify(error_response.model_dump()), 400
    
    except InvalidParameterError as e:
        error_response = ErrorResponse(
            error="InvalidParameter",
            message=str(e),
            details={"providedValue": e.value}
        )
        return jsonify(error_response.model_dump()), 400
        
    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to retrieve jobs",
            details={"error": str(e)}
        )
        return jsonify(error_response.model_dump()), 500


@jobs_bp.route('/<job_id>', methods=['GET'])
def get_job_by_id(job_id: str):
    """
    Get a single job by ID.
    
    Path Parameters:
        job_id (str): Unique job identifier
    
    Returns:
        200: Job details with calculated duration
        404: Job not found
        500: Server error
    
    Example:
        GET /jobs/JOB001
    """
    try:
        job_data = job_service.get_job_with_duration(job_id)
        
        response = SuccessResponse(
            message="Job retrieved successfully",
            data=job_data
        )
        
        return jsonify(response.model_dump()), 200
        
    except ResourceNotFoundError as e:
        error_response = ErrorResponse(
            error="NotFound",
            message=str(e)
        )
        return jsonify(error_response.model_dump()), 404
        
    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to retrieve job",
            details={"error": str(e)}
        )
        return jsonify(error_response.model_dump()), 500


@jobs_bp.route('/upcoming', methods=['GET'])
def get_upcoming_jobs():
    """
    Get jobs scheduled to start in the future.
    
    Query Parameters:
        - hours (int): Number of hours to look ahead (default: 24)
    
    Returns:
        200: List of upcoming jobs
        400: Invalid hours parameter
        500: Server error
    
    Example:
        GET /jobs/upcoming
        GET /jobs/upcoming?hours=48
    """
    try:
        # Parse hours parameter
        hours_str = request.args.get('hours', '24')
        hours_ahead = int(hours_str)
        
        jobs = job_service.get_upcoming_jobs(hours_ahead=hours_ahead)
        
        jobs_data = [job.model_dump() for job in jobs]
        
        response = SuccessResponse(
            message=f"Retrieved {len(jobs_data)} upcoming job(s)",
            data=jobs_data
        )
        
        return jsonify(response.model_dump()), 200
        
    except ValueError:
        error_response = ErrorResponse(
            error="InvalidParameter",
            message="hours parameter must be a valid integer"
        )
        return jsonify(error_response.model_dump()), 400
        
    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to retrieve upcoming jobs",
            details={"error": str(e)}
        )
        return jsonify(error_response.model_dump()), 500


@jobs_bp.route('/stats', methods=['GET'])
def get_job_statistics():
    """
    Get job statistics and summary.
    
    Returns:
        200: Statistics including total count, average duration, time distribution
        500: Server error
    
    Example:
        GET /jobs/stats
    """
    try:
        stats = job_service.get_statistics()
        
        response = SuccessResponse(
            message="Statistics retrieved successfully",
            data=stats
        )
        
        return jsonify(response.model_dump()), 200
        
    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to retrieve statistics",
            details={"error": str(e)}
        )
        return jsonify(error_response.model_dump()), 500


@jobs_bp.errorhandler(404)
def job_not_found(e):
    """Handle 404 errors for job routes."""
    error_response = ErrorResponse(
        error="NotFound",
        message="Job endpoint not found"
    )
    return jsonify(error_response.model_dump()), 404