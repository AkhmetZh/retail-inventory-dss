# StockWise — Inventory Replenishment Decision Support

A small academic prototype for inventory tracking, statistical sales analysis, and replenishment recommendations for small retail businesses.

## Features

- Dashboard with product count, stock units, and 14-day sales summary
- Product catalogue with SKU, category, price, stock, supplier lead time, safety stock, and target coverage
- Sales entry that records a transaction and updates stock
- Average daily sales and reorder-point calculation
- Suggested replenishment quantity when stock is at or below the reorder point
- CSV export of products that need replenishment
- SQLite database created automatically on first run
- Demo products and synthetic demo sales history for immediate demonstration

## Technology stack

- Python 3
- Flask
- SQLite
- HTML / CSS
- Jinja templates

Pandas/forecasting libraries are intentionally not required for this first working prototype. The current recommendation algorithm is a transparent baseline heuristic; a later version can compare moving-average and exponential-smoothing forecasts.

## Run locally

Python 3.10+ is recommended.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, use Command Prompt:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

The SQLite database `inventory.db` is created beside `app.py`. The app inserts a small synthetic demo catalogue only when the database contains no products. These records are fictional and must not be presented as real store data.

## Replenishment logic

The application uses the most recent 14 calendar days, including today.

- `average_daily_sales = units_sold_in_period / 14`
- `reorder_point = average_daily_sales * supplier_lead_time_days + safety_stock`
- `target_stock = average_daily_sales * target_coverage_days + safety_stock`
- `suggested_order_quantity = max(0, round(target_stock - current_stock))`, but only when current stock is at or below the reorder point.

This is a simple educational baseline, not a production-grade inventory optimizer. It does not yet model purchase orders in transit, stock reservations, supplier minimum order quantities, expiry, variable lead times, or forecast uncertainty. Sales larger than current stock are recorded, while stock is floored at zero; a production version should explicitly model stockouts and backorders.

## Main pages

- `/` — dashboard and replenishment recommendations
- `/products` — add and view products
- `/sales` — record sales and review recent transactions
- `/recommendations.csv` — download the current reorder list as CSV
- `/health` — basic health endpoint

## Create a Git repository and version tag

After you have run and reviewed the project, open a terminal in this folder:

```bash
git init
git add .
git commit -m "Build initial inventory replenishment prototype"
git branch -M main
```

Create an empty repository on GitHub (do not add a README there if you already have this README locally), then connect it:

```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Only create the required tag after confirming which features the supervisor expects in the `prob-period-1` version:

```bash
git tag -a prob-period-1 -m "Project version prob-period-1"
git push origin prob-period-1
```

The tag URL will be:

`https://github.com/YOUR-USERNAME/YOUR-REPOSITORY/tree/prob-period-1`

Replace the placeholders with your actual GitHub username and repository name. Do not claim the tag or push exists until you have completed those commands successfully.

## Suggested next improvements

1. Add editing of existing products and inventory adjustments.
2. Import sales from CSV with validation.
3. Separate sales transactions from stock adjustments and model stockouts.
4. Add date-range selection and sales charts.
5. Compare moving-average and exponential-smoothing forecasts using time-based holdout evaluation.
6. Add tests for reorder calculations and form validation.
7. Add authentication and deployment hardening if required by the supervisor.

## Academic integrity and reporting

The seeded transactions are synthetic demo data. Describe them as simulated data in the thesis. Report only features and tests that you have actually run. The prototype is a starting implementation and should be reviewed with the supervisor before being presented as the required tagged project version.
