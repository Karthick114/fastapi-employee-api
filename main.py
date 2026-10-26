from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_connection

app = FastAPI()
employees = []


class Employee(BaseModel):
    name: str
    role: str
    experience: int

@app.get("/")
def home():
    return {"message": "My first FastAPI is working!"}


@app.post("/employees", status_code=201)
def create_employee(employee: Employee):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO employees (name, role, experience)
        VALUES (?, ?, ?)
        """,
        (employee.name, employee.role, employee.experience)
    )

    connection.commit()

    employee_id = cursor.lastrowid
    connection.close()

    return {
        "message": "Employee created successfully",
        "id": employee_id,
        "name": employee.name,
        "role": employee.role,
        "experience": employee.experience
    }



@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    connection = get_connection()

    cursor = connection.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    )

    employee = cursor.fetchone()
    connection.close()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return dict(employee)

@app.get("/employees")
def get_employees():
    connection = get_connection()

    cursor = connection.execute(
        "SELECT * FROM employees"
    )

    employees = cursor.fetchall()
    connection.close()

    return [dict(employee) for employee in employees]



@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: Employee):
    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE employees
        SET name = ?, role = ?, experience = ?
        WHERE id = ?
        """,
        (
            employee.name,
            employee.role,
            employee.experience,
            employee_id
        )
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    connection.close()

    return {
        "message": "Employee updated successfully",
        "id": employee_id,
        "name": employee.name,
        "role": employee.role,
        "experience": employee.experience
    }



@app.patch("/employees/{employee_id}")
def patch_employee(employee_id: int, updates: dict):
    allowed_fields = ["name", "role", "experience"]

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="At least one field is required"
        )

    for key in updates:
        if key not in allowed_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid field: {key}"
            )

    connection = get_connection()

    cursor = connection.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    )
    employee = cursor.fetchone()

    if employee is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    fields = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [employee_id]

    connection.execute(
        f"UPDATE employees SET {fields} WHERE id = ?",
        values
    )

    connection.commit()

    cursor = connection.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    )
    updated_employee = dict(cursor.fetchone())
    connection.close()

    return {
        "message": "Employee partially updated",
        "employee": updated_employee
    }




@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    connection = get_connection()

    cursor = connection.execute(
        "SELECT * FROM employees WHERE id = ?",
        (employee_id,)
    )

    employee = cursor.fetchone()

    if employee is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    deleted_employee = dict(employee)

    connection.execute(
        "DELETE FROM employees WHERE id = ?",
        (employee_id,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Employee deleted successfully",
        "employee": deleted_employee
    }
