from typing import List, Optional
from flask import current_app
from app.models import Employee
from app.services.data_service import read_json_file, write_json_file


class EmployeeRepository:
    """Repository for employee data access operations."""

    def get_all(self) -> List[Employee]:
        """
        Load all employees from the data store.
        """
        print(current_app.config["EMPLOYEES_FILE"])
        data = read_json_file(current_app.config["EMPLOYEES_FILE"])
        return [Employee(**emp) for emp in data]

    def get_by_id(self, employee_id: str) -> Optional[Employee]:
        """
        Get a single employee by ID.
        """
        employees = self.get_all()
        return next((e for e in employees if e.id == employee_id), None)

    def save_all(self, employees: List[Employee]) -> None:
        """
        Save all employees to the data store.
        """
        data = [emp.model_dump(mode="json") for emp in employees]
        write_json_file(current_app.config["EMPLOYEES_FILE"], data)

    def create(self, employee: Employee) -> Employee:
        """
        Create a new employee.
        """
        employees = self.get_all()
        employees.append(employee)
        self.save_all(employees)
        return employee

    def update(self, employee: Employee) -> Optional[Employee]:
        """
        Update an existing employee.
        """
        employees = self.get_all()
        for i, emp in enumerate(employees):
            if emp.id == employee.id:
                employees[i] = employee
                self.save_all(employees)
                return employee
        return None

    def delete(self, employee_id: str) -> bool:
        """
        Delete an employee by ID.
        """
        employees = self.get_all()
        original_count = len(employees)
        employees = [e for e in employees if e.id != employee_id]

        if len(employees) < original_count:
            self.save_all(employees)
            return True
        return False
