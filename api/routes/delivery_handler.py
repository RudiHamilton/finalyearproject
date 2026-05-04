from flask import Blueprint, jsonify
from api.db.db import get_db_connection

delivery_bp = Blueprint("delivery", __name__)


@delivery_bp.route("/deliveries", methods=["GET"])
def get_deliveries():
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    d.id,
                    d.barcode,
                    d.item_description,
                    d.delivery_status,
                    d.delivery_notes,
                    c.first_name || ' ' || c.last_name AS customer_name,
                    c.city,
                    c.postcode,
                    c.latitude,
                    c.longitude
                FROM deliveries d
                JOIN customers c ON d.customer_id = c.id
                ORDER BY d.id;
            """)
            rows = cursor.fetchall()

        return jsonify(rows)

    finally:
        conn.close()


@delivery_bp.route("/deliveries/pending", methods=["GET"])
def get_pending_deliveries():
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    d.id,
                    d.barcode,
                    d.item_description,
                    c.first_name || ' ' || c.last_name AS customer_name,
                    c.city,
                    c.postcode,
                    c.latitude,
                    c.longitude
                FROM deliveries d
                JOIN customers c ON d.customer_id = c.id
                WHERE d.delivery_status = 'pending'
                ORDER BY d.id;
            """)
            rows = cursor.fetchall()

        return jsonify(rows)

    finally:
        conn.close()