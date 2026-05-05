import os
import html
import barcode
from barcode.writer import ImageWriter

from api.db.db import get_db_connection


OUTPUT_IMAGE_DIR = "data/generated_barcodes/images"
HTML_OUTPUT_PATH = "data/generated_barcodes/barcode_labels.html"

def get_deliveries():
    """
    Reads delivery barcode data from the database.
    """
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    d.id,
                    d.barcode,
                    d.item_description,
                    d.delivery_status,
                    c.first_name || ' ' || c.last_name AS customer_name,
                    c.city,
                    c.postcode
                FROM deliveries d
                JOIN customers c ON d.customer_id = c.id
                ORDER BY d.id;
            """)

            return cursor.fetchall()

    finally:
        conn.close()


def generate_barcode_image(barcode_value):
    """
    Generates a barcode PNG image for a delivery barcode.
    Code128 is used because it scans reliably and supports numeric/string values.
    """
    os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)

    barcode_class = barcode.get_barcode_class("code128")
    barcode_object = barcode_class(barcode_value, writer=ImageWriter())

    output_path_without_extension = os.path.join(
        OUTPUT_IMAGE_DIR,
        barcode_value
    )

    saved_path = barcode_object.save(
        output_path_without_extension,
        options={
            "write_text": True,
            "module_height": 15,
            "module_width": 0.3,
            "quiet_zone": 4,
            "font_size": 10,
            "text_distance": 4,
        },
    )

    return saved_path


def build_html_page(deliveries):
    """
    Creates a printable local HTML page containing generated barcode labels.
    """
    os.makedirs(os.path.dirname(HTML_OUTPUT_PATH), exist_ok=True)

    cards = []

    for delivery in deliveries:
        barcode_value = str(delivery["barcode"])
        image_path = f"images/{barcode_value}.png"

        card = f"""
        <section class="barcode-card">
            <h2>Delivery #{html.escape(str(delivery["id"]))}</h2>

            <img src="{html.escape(image_path)}" alt="Barcode {html.escape(barcode_value)}">

            <p><strong>Barcode:</strong> {html.escape(barcode_value)}</p>
            <p><strong>Customer:</strong> {html.escape(delivery["customer_name"])}</p>
            <p><strong>Item:</strong> {html.escape(delivery["item_description"])}</p>
            <p><strong>Location:</strong> {html.escape(delivery["city"])} - {html.escape(delivery["postcode"])}</p>
            <p><strong>Status:</strong> {html.escape(delivery["delivery_status"])}</p>
        </section>
        """

        cards.append(card)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Generated Delivery Barcodes</title>

    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            color: #222;
        }}

        header {{
            background: #1f2937;
            color: white;
            padding: 1.5rem 2rem;
        }}

        header h1 {{
            margin: 0 0 0.4rem 0;
        }}

        header p {{
            margin: 0;
            color: #d1d5db;
        }}

        main {{
            padding: 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
        }}

        .barcode-card {{
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            break-inside: avoid;
        }}

        .barcode-card h2 {{
            margin-top: 0;
            font-size: 1.1rem;
        }}

        .barcode-card img {{
            width: 100%;
            max-width: 260px;
            display: block;
            margin: 0.75rem auto;
        }}

        .barcode-card p {{
            margin: 0.3rem 0;
            font-size: 0.9rem;
        }}

        @media print {{
            body {{
                background: white;
            }}

            header {{
                display: none;
            }}

            main {{
                padding: 0;
                grid-template-columns: repeat(2, 1fr);
            }}

            .barcode-card {{
                box-shadow: none;
                border: 1px solid #ccc;
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Generated Delivery Barcodes</h1>
        <p>Barcode labels generated locally from the PostgreSQL deliveries table.</p>
    </header>

    <main>
        {''.join(cards)}
    </main>
</body>
</html>
"""

    with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as file:
        file.write(html_content)


def main():
    deliveries = get_deliveries()

    if not deliveries:
        print("No deliveries found in the database.")
        return

    for delivery in deliveries:
        barcode_value = str(delivery["barcode"])
        saved_path = generate_barcode_image(barcode_value)
        print(f"Generated barcode image: {saved_path}")

    build_html_page(deliveries)

    print("")
    print(f"Generated {len(deliveries)} barcode images.")
    print(f"Barcode page created at: {HTML_OUTPUT_PATH}")
    print("")
    print("Open it with:")
    print("xdg-open data/generated_barcodes/barcode_labels.html")


if __name__ == "__main__":
    main()