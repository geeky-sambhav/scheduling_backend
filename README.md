# Scheduling Backend API

A Flask-based REST API for managing employee job assignments and scheduling. This backend provides endpoints for managing employees, jobs, and their assignments with built-in validation rules to prevent scheduling conflicts.

## Table of Contents

- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [API Endpoints](#api-endpoints)
- [Business Rules & Validations](#business-rules--validations)
- [Error Handling](#error-handling)
- [Development Notes](#development-notes)

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Runtime |
| Flask | 3.0.0 | Web framework |
| Pydantic | 2.5.0 | Data validation & serialization |
| Flask-CORS | 4.0.0 | Cross-origin resource sharing |
| python-dotenv | 1.0.0 | Environment variable management |

---


## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd scheduling_backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env


---

### Development Mode

```bash
python run.py
```

The server will start at `http://localhost:8000` (or the port specified in `.env`).


---

## API Endpoints

### Base URL

```
http://localhost:8000
```

### Employees

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/employees` | Get all employees |

#### Response Example - GET /employees

```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "id": "emp-001",
      "name": "John Smith",
      "role": "TCP",
      "availability": true
    }
  ]
}
```

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/jobs` | Get all jobs |
| `GET` | `/jobs/<job_id>` | Get a specific job with duration |

#### Response Example - GET /jobs

```json
{
  "success": true,
  "count": 6,
  "data": [
    {
      "id": "job-001",
      "name": "Morning Shift - Assembly Line A",
      "startTime": "2026-01-31T06:00:00",
      "endTime": "2026-01-31T10:00:00"
    }
  ]
}
```

### Schedule

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/schedule` | Get all assignments with employee and job details |

#### Response Example - GET /schedule

```json
{
  "success": true,
  "count": 1,
  "data": [
    {
      "id": "ASSIGN9959039E",
      "assignedAt": "2026-02-01T05:19:17.405554",
      "employee": {
        "id": "emp-001",
        "name": "John Smith",
        "role": "TCP"
      },
      "job": {
        "id": "job-006",
        "name": "Night Shift - Warehouse",
        "startTime": "2026-01-31T20:00:00",
        "endTime": "2026-02-01T06:00:00"
      }
    }
  ]
}
```

### Assignments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/assign` | Create a new assignment |
| `DELETE` | `/assign/<assignment_id>` | Delete an assignment |

#### Request Body - POST /assign

```json
{
  "employeeId": "emp-001",
  "jobId": "job-001"
}
```

#### Response Example - POST /assign (Success)

```json
{
  "success": true,
  "message": "Assignment created successfully",
  "data": {
    "id": "ASSIGN12345678",
    "employeeId": "emp-001",
    "jobId": "job-001",
    "assignedAt": "2026-02-01T10:30:00.000000"
  }
}
```

#### Response Example - DELETE /assign/{id}

```json
{
  "success": true,
  "message": "Assignment deleted successfully",
  "data": {
    "deletedId": "ASSIGN12345678"
  }
}
```

---


## Business Rules & Validations

The system enforces the following business rules when creating assignments:

### 1. No Double Booking
An employee cannot be assigned to the same job twice. The system checks if an assignment already exists for the given employee-job pair.

**Error Response:**
```json
{
  "success": false,
  "error": "DoubleBooking",
  "message": "Employee 'John Smith' is already assigned to 'Morning Shift'"
}
```

### 2. No Overlapping Time Slots
An employee cannot be assigned to jobs with overlapping time windows. The system checks all existing assignments for the employee and ensures no time conflicts exist.

**Error Response:**
```json
{
  "success": false,
  "error": "TimeOverlap",
  "message": "Time overlap for John Smith between Morning Shift and Midday Maintenance"
}
```

### 3. Availability Filtering
Only employees marked as `availability: true` can be assigned to jobs. Unavailable employees are blocked from new assignments.

**Error Response:**
```json
{
  "success": false,
  "error": "EmployeeUnavailable",
  "message": "Employee 'Emily Brown' is currently unavailable for assignment"
}
```

### 4. Job Time Constraints
- Job duration must be at least 30 minutes
- Job duration cannot exceed 24 hours
- End time must be after start time

### 5. Entity Existence
Both the employee and job must exist in the system before an assignment can be created.

---

## Error Handling

The API uses standardized error responses:

### Success Response Format

```json
{
  "success": true,
  "message": "Optional message",
  "count": 10,
  "data": { }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": { },
  "timestamp": "2026-02-01T10:30:00.000000"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created successfully |
| `400` | Bad request / Validation error / Employee unavailable |
| `404` | Resource not found (employee, job, or assignment) |
| `409` | Conflict (double booking or time overlap) |
| `500` | Internal server error |

### Validation Error Response

```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Request validation failed",
  "errors": [
    {
      "field": "employeeId",
      "message": "Field required",
      "type": "missing"
    }
  ],
  "timestamp": "2026-02-01T10:30:00.000000"
}
```


---

## Development Notes

### Architecture

The application follows a layered architecture:

1. **Routes Layer** (`app/routes/`): HTTP request handling, input validation
2. **Service Layer** (`app/services/`): Business logic, validation rules
3. **Repository Layer** (`app/repositories/`): Data access, JSON file operations
4. **Models Layer** (`app/models/`): Data structures, Pydantic models


