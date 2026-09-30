# Frontend Architecture & Jinja2 Setup Documentation

## 1. Overview & Technical Stack

The Sales Analytics Platform frontend is implemented using a lightweight, server-rendered Jinja2 template architecture with vanilla JavaScript, Apache ECharts, and custom CSS:
- **Template Engine**: Jinja2 (`fastapi.templating.Jinja2Templates`)
- **Static Assets**: FastAPI StaticFiles (`fastapi.staticfiles.StaticFiles`)
- **Visualization Libraries**: Apache ECharts v5.4.3 via official CDN & Power BI via official secure `reportEmbed` iframe
- **Styling**: HTML5 + CSS3 (CSS Custom Properties design system with responsive card layouts, styled data tables, and 16:9 Power BI aspect-ratio containers)
- **Scripting**: Vanilla JavaScript (ES6+ `fetch` API, `Promise.all` concurrent fetching, and `URLSearchParams`)

---

## 2. Directory Architecture & Final Navigation

```
Sales-Analytics-Platform/
├── app/
│   └── main.py              # Page routes (/dashboard, /products, /customers, /regions, /powerbi) & static mounts
├── templates/
│   ├── base.html            # Application shell shell, 5-item sidebar navigation, and Apache ECharts CDN
│   ├── dashboard.html       # Executive Overview template (6 KPI cards, 4 ECharts cards)
│   ├── products.html        # Product Analytics template (3 KPI cards, Top Products chart & table)
│   ├── customers.html       # Customer Analytics template (3 KPI cards, Top Customers chart & table)
│   ├── regions.html         # Regional Analytics template (3 KPI cards, Sales by Region chart & table)
│   └── powerbi.html         # Power BI Executive Dashboard template (Secure reportEmbed iframe)
├── static/
│   ├── css/
│   │   └── style.css        # Core styles, sidebar, KPI cards, filter panel, ECharts containers, data tables & Power BI
│   └── js/
│       ├── charts.js        # ECharts initialization, custom elementId options, tooltips, resize & empty states
│       └── dashboard.js     # Shared filter state, modular page controllers, Promise.all API fetching & tables
└── docs/
    └── frontend_setup.md    # Frontend documentation
```

### Final Sidebar Navigation Structure
1. **Overview**: `/dashboard`
2. **Products**: `/products`
3. **Customers**: `/customers`
4. **Regions**: `/regions`
5. **Power BI**: `/powerbi`

*(Note: The placeholder `Analytics` navigation item has been completely removed).*

---

## 3. Serving Frontend & Static Files

### Page Route Matrix
- `GET /`: API Root health JSON payload (`{"message": "...", "status": "healthy"}`)
- `GET /dashboard`: Executive Overview Jinja2 Dashboard HTML page (`active_page = "overview"`)
- `GET /products`: Product Analytics Jinja2 HTML page (`active_page = "products"`)
- `GET /customers`: Customer Analytics Jinja2 HTML page (`active_page = "customers"`)
- `GET /regions`: Regional Analytics Jinja2 HTML page (`active_page = "regions"`)
- `GET /powerbi`: Power BI Executive Dashboard Jinja2 HTML page (`active_page = "powerbi"`)
- `GET /static/...`: Serves static CSS, JS, and media assets

---

## 4. Page Architecture & Feature Breakdown

### A. Executive Dashboard (`/dashboard`)
- **Route**: `GET /dashboard`
- **APIs Used**: `GET /api/summary`, `GET /api/sales/monthly`, `GET /api/sales/region`, `GET /api/products/top?limit=10`, `GET /api/customers/top?limit=10`
- **KPI Cards**: Total Sales, Total Profit, Total Orders, Total Customers, Profit Margin, Return Rate
- **Charts**: Sales & Profit Trend (Line), Sales by Region (Bar), Top 10 Products (Bar), Top 10 Customers (Bar)

### B. Product Analytics (`/products`)
- **Route**: `GET /products`
- **APIs Used**: `GET /api/summary`, `GET /api/products/top?limit=10`
- **Purpose**: Analyze product-level sales performance and identify top catalog items
- **KPI Cards**: Total Product Sales, Total Product Profit, Total Orders
- **Chart**: Top 10 Products by Sales (Horizontal ECharts bar chart)
- **Data Table**: Top Product Performance Details (Rank, Product Name, Category, Sub-Category, Sales, Profit)

### C. Customer Analytics (`/customers`)
- **Route**: `GET /customers`
- **APIs Used**: `GET /api/summary`, `GET /api/customers/top?limit=10`
- **Purpose**: Analyze customer contribution and identify high-value accounts
- **KPI Cards**: Total Customers, Customer Sales, Total Orders
- **Chart**: Top 10 Customers by Sales (Horizontal ECharts bar chart)
- **Data Table**: Top Customer Performance Details (Rank, Customer Name, Segment, Total Sales, Total Profit)

### D. Regional Analytics (`/regions`)
- **Route**: `GET /regions`
- **APIs Used**: `GET /api/summary`, `GET /api/sales/region`
- **Purpose**: Compare sales performance and profit across geographic regions
- **KPI Cards**: Regional Sales, Regional Profit, Total Orders
- **Chart**: Sales by Region Comparison (Horizontal ECharts bar chart)
- **Data Table**: Regional Performance Comparison Table (Rank, Region Name, Sales, Profit, Total Orders)

### E. Power BI Executive Dashboard (`/powerbi`)
- **Route**: `GET /powerbi`
- **Embed URL**: Official secure `reportEmbed` URL:
  `https://app.powerbi.com/reportEmbed?reportId=7248aa69-bfc4-4d0f-a647-e07ba6618878&autoAuth=true&ctid=35e8087e-75a7-4479-b528-df0fbbb7fc26&actionBarEnabled=true`
- **Security & Authentication Architecture**:
  - Uses Power BI's secure `reportEmbed` architecture.
  - Does **NOT** use public "Publish to web" (no public data exposure).
  - No credentials, tokens, or client secrets are exposed in backend or frontend JavaScript.
  - Native Microsoft Azure AD authentication & workspace permissions are delegated securely to Power BI.
- **Informational Callout**: Includes a subtle user notice stating *"Power BI may require Microsoft authentication and appropriate report permissions."*

---

## 5. How to Run Locally

1. Start the FastAPI development server:
   ```powershell
   .\venv\Scripts\python -m uvicorn app.main:app --reload
   ```

2. Open the pages in your browser:
   - Dashboard: `http://127.0.0.1:8000/dashboard`
   - Products: `http://127.0.0.1:8000/products`
   - Customers: `http://127.0.0.1:8000/customers`
   - Regions: `http://127.0.0.1:8000/regions`
   - Power BI: `http://127.0.0.1:8000/powerbi`

3. Run the automated test suite:
   ```powershell
   .\venv\Scripts\python -m unittest discover -s tests
   ```
