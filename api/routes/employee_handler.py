from flask import Blueprint, jsonify
from api.db.db import get_db_connection

employee_bp = Blueprint("employee", __name__)


@employee_bp.route("/employees/<employee_number>", methods=["GET"])
def get_employee_by_number(employee_number):
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    employee_number,
                    full_name
                FROM employees
                WHERE employee_number = %s;
                """,
                (employee_number,),
            )

            employee = cursor.fetchone()

        if employee is None:
            return jsonify({"error": "Employee not found"}), 404

        return jsonify(employee)

    finally:
        conn.close()