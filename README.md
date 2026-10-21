# StockWise — Inventory Replenishment Decision Support

## 1. Project Overview

StockWise is an academic software prototype designed to support inventory tracking, sales analysis, and replenishment decisions for small retail businesses.

The system analyzes recent sales, estimates average daily demand, calculates reorder points, and recommends replenishment quantities when stock levels become too low.

The project explores how a lightweight, data-driven application can help small retailers make more consistent inventory replenishment decisions.

## 2. Problem Statement

Small retail businesses need to maintain sufficient stock to meet customer demand while avoiding unnecessary inventory accumulation. Manual inventory monitoring and replenishment decisions can be time-consuming and may not consistently account for sales rates, supplier lead times, and safety stock.

StockWise addresses this problem by providing a simple inventory management interface and transparent, sales-based replenishment recommendations.

The current prototype uses a baseline statistical heuristic. Its recommendations are intended for educational evaluation and should not be treated as guaranteed optimal ordering decisions.

## 3. Aim and Objectives

### Aim

To develop and evaluate a lightweight inventory replenishment decision-support prototype for small retail businesses.

### Objectives

- Implement a product catalogue and basic inventory tracking.
- Record sales transactions and update stock quantities.
- Analyze sales over a rolling 14-calendar-day period.
- Calculate average daily sales and reorder points.
- Recommend replenishment quantities based on current stock and target coverage.
- Export products requiring replenishment to CSV.
- Evaluate the functionality and limitations of the baseline recommendation algorithm.
- Establish a foundation for comparing alternative demand forecasting methods in future development.

## 4. Target Users

The intended users are:

- Owners of small retail businesses.
- Retail inventory managers.
- Staff responsible for monitoring stock and recording sales.

These groups represent the intended audience of the prototype. Their needs should be validated through interviews or discussions with relevant users.

## 5. Project Scope

### In scope

- Product catalogue management and product creation.
- Inventory quantity tracking.
- Sales transaction recording.
- Basic sales statistics.
- Reorder-point calculations.
- Replenishment quantity recommendations.
- CSV export of replenishment recommendations.
- Local deployment using Flask and SQLite.

### Out of scope for the current prototype

- Automated purchase order submission.
- Supplier integrations.
- Purchase orders in transit and reserved stock.
- Supplier minimum order quantities.
- Expiry-date management.
- Probabilistic demand forecasting.
- Production-grade authentication and deployment security.

These limitations may be reconsidered as part of future development.

## 6. Main Features

- **Dashboard:** Displays product count, total stock units, and a 14-day sales summary.
- **Product catalogue:** Stores SKU, category, price, stock quantity, supplier lead time, safety stock, and target coverage.
- **Sales recording:** Records a sale and updates inventory.
- **Sales analysis:** Calculates average daily sales using the most recent 14 calendar days, including today.
- **Replenishment recommendations:** Identifies products at or below their calculated reorder points and suggests order quantities.
- **CSV export:** Exports the current replenishment recommendation list.
- **Automatic database initialization:** Creates the SQLite database and inserts fictional demonstration data when the database has no products.
- **Health endpoint:** Provides a basic application health check.

## 7. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3 | Application logic |
| Flask | Web application framework |
| SQLite | Local relational database |
| HTML and CSS | User interface |
| Jinja | Server-side HTML templates |

Pandas and dedicated forecasting libraries are not required for the current prototype.

## 8. Replenishment Algorithm

The baseline algorithm uses sales from the most recent 14 calendar days, including today.

Let:

- `units_sold_14d` be the number of units sold during this period.
- `lead_time_days` be the supplier lead time in days.
- `safety_stock` be the additional stock buffer.
- `target_coverage_days` be the desired stock coverage in days.
- `current_stock` be the current inventory quantity.

### Average daily sales

`average_daily_sales = units_sold_14d / 14`

### Reorder point

`reorder_point = average_daily_sales * lead_time_days + safety_stock`

### Target stock

`target_stock = average_daily_sales * target_coverage_days + safety_stock`

### Suggested order quantity

If current stock is at or below the reorder point:

`suggested_order_quantity = max(0, round(target_stock - current_stock))`

Otherwise, the suggested order quantity is zero.

The algorithm is a transparent baseline heuristic rather than a production-grade inventory optimizer. It does not currently account for demand uncertainty, purchase orders in transit, stock reservations, supplier minimum order quantities, expiry dates, or variable supplier lead times.

Sales exceeding available stock are recorded, while stock is floored at zero. Explicit stockout and backorder modelling remains a potential improvement.

## 9. Application Routes

| Route | Description |
|---|---|
| `/` | Dashboard and replenishment recommendations |
| `/products` | Product catalogue and product creation |
| `/sales` | Sales entry and recent transactions |
| `/recommendations.csv` | CSV export of replenishment recommendations |
| `/health` | Basic health endpoint |

## 10. Project Structure

The following structure is recommended for organizing the project repository. Adjust it to match the actual files in the repository.

```text
StockWise/
├── app.py
├── requirements.txt
├── README.md
├── inventory.db          # Local database; normally not committed
├── templates/
├── static/
├── docs/
├── diagrams/
├── tests/
├── .gitignore
└── .env.example
```

## 11. Installation and Execution

### Requirements

- Python 3.10 or newer.
- Git, if cloning the repository.

### Windows — PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If PowerShell blocks virtual environment activation, use Command Prompt:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

### macOS and Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open the application at:

http://127.0.0.1:5000

The SQLite database is created beside `app.py` by default. The application seeds a fictional demonstration catalogue and synthetic sales history when the database contains no products.

The database and demonstration data must not be presented as real business records.

## 12. Testing and Verification

The following checks should be performed and documented before claiming that the corresponding functionality has been verified:

- Application starts successfully.
- Database initialization works as expected.
- Products can be created and displayed.
- Sales transactions update inventory correctly.
- Average daily sales are calculated using the intended 14-day period.
- Reorder points are calculated correctly.
- Replenishment recommendations follow the stated decision rule.
- CSV export produces the expected columns and records.
- Invalid or unexpected input is handled appropriately.
- The health endpoint returns the expected response.

Automated tests and their results should be added when implemented. Do not report tests as passed until they have actually been executed.

## 13. Current Development Status

**Project stage:** Initial academic prototype.

**Implemented functionality:** [Confirm against the current code and tests before submission.]

**Known limitations:** The current algorithm uses a simple historical average and does not model several operational inventory constraints.

**Next development steps:**

1. Add automated tests for replenishment calculations and input validation.
2. Implement inventory adjustments and product editing.
3. Add validated sales CSV import.
4. Introduce date-range selection and sales charts.
5. Compare moving-average and exponential-smoothing forecasts using time-based holdout evaluation.
6. Consider authentication and deployment hardening if required.

### Version Control

Development should be recorded through meaningful commits, task-linked branches, and reviewed pull or merge requests. The repository should preserve the history of documentation, design decisions, implementation, and testing.

The required first pre-defense submission tag is `pre-defense-1`, subject to confirmation by the supervisor.

## 14. Academic Integrity and Data Limitations

All seeded demonstration transactions are synthetic and must be described as simulated data in the thesis and project presentation.

Claims about implemented features, testing outcomes, user feedback, and system performance must be supported by actual evidence. The prototype should be reviewed with the supervisor before it is presented as the official pre-defense submission.

The project is intended for academic demonstration and evaluation. Its recommendations should not be interpreted as guaranteed optimal purchasing decisions.
