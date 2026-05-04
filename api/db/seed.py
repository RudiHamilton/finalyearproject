import os
import random

import psycopg2
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

load_dotenv()

fake = Faker("en_GB")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")


FERMANAGH_LOCATIONS = [
    ("Enniskillen", "BT74", 54.3438, -7.6315),
    ("Lisnaskea", "BT92", 54.2500, -7.4428),
    ("Irvinestown", "BT94", 54.4706, -7.6336),
    ("Ballinamallard", "BT94", 54.4237, -7.5940),
    ("Kesh", "BT93", 54.5092, -7.7278),
    ("Belleek", "BT93", 54.4793, -8.0895),
    ("Derrygonnelly", "BT93", 54.4191, -7.8180),
    ("Florencecourt", "BT92", 54.2526, -7.7314),
    ("Belcoo", "BT93", 54.2975, -7.8682),
    ("Tempo", "BT94", 54.3784, -7.4630),
    ("Maguiresbridge", "BT94", 54.2867, -7.4680),
    ("Ederney", "BT93", 54.5420, -7.6630),
    ("Newtownbutler", "BT92", 54.1820, -7.3590),
]


ITEMS = [
    "Small parcel",
    "Medium parcel",
    "Large box",
    "Document envelope",
    "Electronics package",
    "Clothing order",
    "Fragile parcel",
    "Replacement item",
    "Customer return",
    "Medical supplies",
    "Household item",
    "Book package",
]


STATUSES = [
    "pending",
    "pending",
    "pending",
    "pending",
    "assigned",
    "delivered",
]


NOTES = [
    None,
    "Leave with neighbour if unavailable",
    "Signature required",
    "Do not leave outside",
    "Customer requested afternoon delivery",
    "Handle with care",
    "Ring doorbell twice",
    "Leave in porch if safe",
]


def random_near(base_lat, base_lng, spread=0.018):
    """
    Creates a random coordinate close to a town centre.
    Keeps demo data geographically realistic for route optimisation.
    """
    return (
        round(base_lat + random.uniform(-spread, spread), 6),
        round(base_lng + random.uniform(-spread, spread), 6),
    )


def reset_tables(cursor):
    """
    Clears existing demo data.
    Uses DELETE instead of TRUNCATE so the restricted app user can run it.
    """
    cursor.execute("DELETE FROM deliveries;")
    cursor.execute("DELETE FROM customers;")


def seed_customers(cursor, count=40):
    """
    Creates random customers around Fermanagh.
    Returns created customer IDs so deliveries can link to them.
    """
    customer_ids = []

    for _ in range(count):
        town, postcode_prefix, base_lat, base_lng = random.choice(FERMANAGH_LOCATIONS)
        latitude, longitude = random_near(base_lat, base_lng)

        cursor.execute(
            """
            INSERT INTO customers
            (
                first_name,
                last_name,
                phone,
                email,
                address_line_1,
                address_line_2,
                city,
                postcode,
                latitude,
                longitude
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                fake.first_name(),
                fake.last_name(),
                fake.phone_number(),
                fake.email(),
                fake.street_address(),
                random.choice([None, fake.secondary_address()]),
                town,
                f"{postcode_prefix} {random.randint(1, 9)}"
                f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
                f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}",
                latitude,
                longitude,
            ),
        )

        customer_id = cursor.fetchone()[0]
        customer_ids.append(customer_id)

    return customer_ids


def seed_deliveries(cursor, customer_ids, count=100):
    """
    Creates random deliveries and links each one to an existing customer.
    """
    used_barcodes = set()

    for _ in range(count):
        barcode = None

        while barcode is None or barcode in used_barcodes:
            barcode = f"DEL-{random.randint(100000, 999999)}"

        used_barcodes.add(barcode)

        cursor.execute(
            """
            INSERT INTO deliveries
            (
                customer_id,
                barcode,
                item_description,
                delivery_status,
                delivery_notes
            )
            VALUES (%s, %s, %s, %s, %s);
            """,
            (
                random.choice(customer_ids),
                barcode,
                random.choice(ITEMS),
                random.choice(STATUSES),
                random.choice(NOTES),
            ),
        )


def main():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            reset_tables(cursor)

            customer_ids = seed_customers(cursor, count=40)
            seed_deliveries(cursor, customer_ids, count=100)

            conn.commit()

    print("Database seeded successfully.")
    print("Created 40 customers.")
    print("Created 100 deliveries.")


if __name__ == "__main__":
    main()