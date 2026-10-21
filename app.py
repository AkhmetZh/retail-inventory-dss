from datetime import date, datetime, timedelta
import csv
import io
import os
import sqlite3

from flask import Flask, Response, flash, redirect, render_template, request, url_for


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.environ.get("INVENTORY_DB_PATH", os.path.join(BASE_DIR, "inventory.db"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-for-production")


def connect_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    with connect_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '',
                unit_price REAL NOT NULL DEFAULT 0 CHECK (unit_price >= 0),
                stock_qty INTEGER NOT NULL DEFAULT 0 CHECK (stock_qty >= 0),
                lead_time_days INTEGER NOT NULL DEFAULT 3 CHECK (lead_time_days >= 0),
                safety_stock INTEGER NOT NULL DEFAULT 2 CHECK (safety_stock >= 0),
                target_days INTEGER NOT NULL DEFAULT 14 CHECK (target_days >= 1),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                sale_date TEXT NOT NULL,
                unit_price REAL NOT NULL DEFAULT 0 CHECK (unit_price >= 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_sales_product_date
            ON sales(product_id, sale_date);
        """)


def add_demo_data():
    with connect_db() as db:
        count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count:
            return

        products = [
            ("COF-001", "Ground coffee 250g", "Beverages", 5.49, 8, 4, 3, 14),
            ("TEA-001", "Black tea 100 bags", "Beverages", 3.25, 24, 5, 5, 14),
            ("PAS-001", "Pasta 500g", "Food", 1.79, 12, 3, 4, 14),
            ("MIL-001", "UHT milk 1L", "Dairy", 1.49, 6, 2, 4, 7),
            ("SOAP-01", "Hand soap", "Household", 2.99, 30, 5, 4, 21),
        ]

        db.executemany("""
            INSERT INTO products
                (sku, name, category, unit_price, stock_qty,
                 lead_time_days, safety_stock, target_days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, products)

        product_ids = {
            row["sku"]: row["id"]
            for row in db.execute("SELECT id, sku FROM products")
        }

        sales_history = {
            "COF-001": [2, 1, 3, 2, 1, 2, 3, 2, 2, 1, 2, 3, 1, 2],
            "TEA-001": [1, 0, 2, 1, 0, 1, 2, 1, 1, 0, 1, 2, 1, 1],
            "PAS-001": [3, 4, 2, 3, 4, 3, 2, 4, 3, 3, 4, 2, 3, 4],
            "MIL-001": [4, 5, 3, 4, 5, 4, 3, 5, 4, 4, 5, 3, 4, 5],
            "SOAP-01": [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        }

        today = date.today()
        for sku, daily_sales in sales_history.items():
            product = db.execute(
                "SELECT unit_price FROM products WHERE sku = ?", (sku,)
            ).fetchone()

            for day_index, quantity in enumerate(daily_sales):
                if quantity == 0:
                    continue

                sale_day = today - timedelta(days=13 - day_index)
                db.execute("""
                    INSERT INTO sales (product_id, quantity, sale_date, unit_price)
                    VALUES (?, ?, ?, ?)
                """, (
                    product_ids[sku],
                    quantity,
                    sale_day.isoformat(),
                    product["unit_price"],
                ))


def calculate_metrics(product, db, period_days=14):
    today = date.today()
    first_day = today - timedelta(days=period_days - 1)

    sales = db.execute("""
        SELECT COALESCE(SUM(quantity), 0) AS quantity_sold,
               COALESCE(SUM(quantity * unit_price), 0) AS revenue
        FROM sales
        WHERE product_id = ? AND sale_date BETWEEN ? AND ?
    """, (
        product["id"],
        first_day.isoformat(),
        today.isoformat(),
    )).fetchone()

    sold = int(sales["quantity_sold"])
    daily_average = sold / period_days
    stock = int(product["stock_qty"])
    lead_time = int(product["lead_time_days"])
    safety_stock = int(product["safety_stock"])
    target_days = int(product["target_days"])

    reorder_point = daily_average * lead_time + safety_stock
    target_stock = daily_average * target_days + safety_stock
    reorder_needed = stock <= reorder_point
    order_quantity = max(0, round(target_stock - stock)) if reorder_needed else 0

    return {
        "sold_period": sold,
        "avg_daily": daily_average,
        "reorder_point": reorder_point,
        "suggested_qty": order_quantity,
        "needs_reorder": reorder_needed,
        "revenue": float(sales["revenue"]),
        "days_cover": stock / daily_average if daily_average else None,
    }


@app.route("/")
def dashboard():
    with connect_db() as db:
        products = db.execute(
            "SELECT * FROM products ORDER BY name"
        ).fetchall()

        rows = []
        for product in products:
            metrics = calculate_metrics(product, db)
            rows.append({"product": product, **metrics})

        low_stock_count = sum(row["needs_reorder"] for row in rows)
        stock_units = sum(int(product["stock_qty"]) for product in products)

        sales_units = db.execute("""
            SELECT COALESCE(SUM(quantity), 0)
            FROM sales
            WHERE sale_date >= ?
        """, (
            (date.today() - timedelta(days=13)).isoformat(),
        )).fetchone()[0]

        revenue = sum(row["revenue"] for row in rows)

    return render_template(
        "dashboard.html",
        rows=rows,
        total_revenue=revenue,
        low_stock=low_stock_count,
        units=stock_units,
        sales_count=sales_units,
    )


@app.route("/products")
def products_page():
    with connect_db() as db:
        products = db.execute(
            "SELECT * FROM products ORDER BY name"
        ).fetchall()

    return render_template("products.html", products=products)


@app.route("/products/add", methods=["POST"])
def add_product():
    product_data = {
        "sku": request.form.get("sku", "").strip(),
        "name": request.form.get("name", "").strip(),
        "category": request.form.get("category", "").strip(),
    }

    try:
        price = float(request.form.get("unit_price", "0"))
        stock = int(request.form.get("stock_qty", "0"))
        lead_time = int(request.form.get("lead_time_days", "3"))
        safety_stock = int(request.form.get("safety_stock", "2"))
        target_days = int(request.form.get("target_days", "14"))

        if not product_data["sku"] or not product_data["name"]:
            raise ValueError("SKU and product name are required.")

        if price < 0 or min(stock, lead_time, safety_stock) < 0 or target_days < 1:
            raise ValueError(
                "Price and quantities must be non-negative; target days must be at least 1."
            )

        with connect_db() as db:
            db.execute("""
                INSERT INTO products
                    (sku, name, category, unit_price, stock_qty,
                     lead_time_days, safety_stock, target_days)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data["sku"],
                product_data["name"],
                product_data["category"],
                price,
                stock,
                lead_time,
                safety_stock,
                target_days,
            ))

        flash("Product added successfully.", "success")

    except sqlite3.IntegrityError:
        flash("That SKU already exists. Use a unique SKU.", "error")
    except (ValueError, TypeError) as error:
        flash(str(error) or "Please check the entered values.", "error")

    return redirect(url_for("products_page"))


@app.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    with connect_db() as db:
        db.execute("DELETE FROM products WHERE id = ?", (product_id,))

    flash("Product deleted.", "success")
    return redirect(url_for("products_page"))


@app.route("/sales")
def sales_page():
    with connect_db() as db:
        products = db.execute(
            "SELECT id, sku, name FROM products ORDER BY name"
        ).fetchall()

        sales = db.execute("""
            SELECT sales.*, products.name AS product_name, products.sku
            FROM sales
            JOIN products ON products.id = sales.product_id
            ORDER BY sales.sale_date DESC, sales.id DESC
            LIMIT 100
        """).fetchall()

    return render_template(
        "sales.html",
        products=products,
        sales=sales,
        today=date.today().isoformat(),
    )


@app.route("/sales/add", methods=["POST"])
def add_sale():
    try:
        product_id = int(request.form.get("product_id", ""))
        quantity = int(request.form.get("quantity", "0"))
        sale_date = request.form.get("sale_date", date.today().isoformat())
        datetime.strptime(sale_date, "%Y-%m-%d")

        if quantity <= 0:
            raise ValueError("Sale quantity must be greater than zero.")

        with connect_db() as db:
            product = db.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()

            if product is None:
                raise ValueError("Please select a valid product.")

            db.execute("""
                INSERT INTO sales (product_id, quantity, sale_date, unit_price)
                VALUES (?, ?, ?, ?)
            """, (
                product_id,
                quantity,
                sale_date,
                product["unit_price"],
            ))

            remaining_stock = max(0, int(product["stock_qty"]) - quantity)
            db.execute(
                "UPDATE products SET stock_qty = ? WHERE id = ?",
                (remaining_stock, product_id),
            )

        flash("Sale recorded and stock updated.", "success")

    except (ValueError, TypeError) as error:
        flash(str(error) or "Please check the sale details.", "error")

    return redirect(url_for("sales_page"))


@app.route("/recommendations.csv")
def export_recommendations():
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "SKU",
        "Product",
        "Current stock",
        "14-day sales",
        "Average daily sales",
        "Lead time (days)",
        "Safety stock",
        "Reorder point",
        "Suggested order quantity",
    ])

    with connect_db() as db:
        products = db.execute(
            "SELECT * FROM products ORDER BY name"
        ).fetchall()

        for product in products:
            metrics = calculate_metrics(product, db)
            if not metrics["needs_reorder"]:
                continue

            writer.writerow([
                product["sku"],
                product["name"],
                product["stock_qty"],
                metrics["sold_period"],
                round(metrics["avg_daily"], 2),
                product["lead_time_days"],
                product["safety_stock"],
                round(metrics["reorder_point"], 2),
                metrics["suggested_qty"],
            ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=replenishment_recommendations.csv"
        },
    )


@app.route("/health")
def health():
    return {"status": "ok"}


create_tables()
add_demo_data()


if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )
