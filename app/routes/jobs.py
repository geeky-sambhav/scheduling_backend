"""
Job API routes.

Handles all job-related endpoints including:
- List all jobs
- Get single job
"""

from flask import Blueprint, jsonify

from app.models import SuccessResponse, ErrorResponse
from app.services.job_service import JobService

# Create blueprint
jobs_bp = Blueprint("jobs", __name__)

# Initialize service
job_service = JobService()


@jobs_bp.route("", methods=["GET"])
def get_all_jobs():
    """Get all jobs."""
    try:
        jobs, _ = job_service.get_all_jobs()
        jobs_data = [job.model_dump() for job in jobs]

        response = SuccessResponse(
            count=len(jobs_data),
            data=jobs_data,
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to retrieve jobs",
            details={"error": str(e)},
        )
        return jsonify(error_response.model_dump()), 500


@jobs_bp.route("/<job_id>", methods=["GET"])
def get_job_by_id(job_id: str):

    try:
        job_data, error = job_service.get_job_with_duration(job_id)

        # Handle service errors
        if error:
            error_response = ErrorResponse(
                error=error["error_type"], message=error["message"]
            )
            return jsonify(error_response.model_dump()), error["status_code"]

        response = SuccessResponse(message="Job retrieved successfully", data=job_data)

        return jsonify(response.model_dump()), 200

    except Exception as e:
        error_response = ErrorResponse(
            error="InternalError",
            message="Failed to retrieve job",
            details={"error": str(e)},
        )
        return jsonify(error_response.model_dump()), 500
