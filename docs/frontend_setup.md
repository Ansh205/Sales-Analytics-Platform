# Frontend Architecture & Jinja2 Setup Documentation

## 1. Overview & Technical Stack

The Sales Analytics Platform frontend is implemented using a lightweight, server-rendered Jinja2 template architecture with vanilla JavaScript, Apache ECharts, and custom CSS:
- **Template Engine**: Jinja2 (`fastapi.templating.Jinja2Templates`)
- **Static Assets**: FastAPI StaticFiles (`fastapi.staticfiles.StaticFiles`)
- **Visualization Library**: Apache ECharts v5.4.3 via official CDN (`https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js`)
- **Styling**: HTML5 + CSS3 (CSS Custom Properties design system)
- **Scripting**: Vanilla JavaScript (ES6+ `fetch` API, `Promise.all` concurrent fetching, and `URLSearchParams`)

---

## 2. Directory Architecture

```
Sales-Analytics-Platform/
├── app/
│   └── main.py              # Configured with Jinja2Templates, StaticFiles, and /dashboard route
├── templates/
│   ├── base.html            # Core HTML5 layout shell + Apache ECharts CDN script tag
│   └── dashboard.html       # Executive Overview template with filter panel, KPI grid & 4 chart cards
├── static/
│   ├── css/
│   │   └── style.css        # CSS variables, card layouts, filter panel grid & chart container styles
│   └── js/
│       ├── charts.js        # Apache ECharts initialization, options, tooltips, resize & empty states
│       └── dashboard.js     # Shared filter state, Promise.all concurrent API fetching, KPI updates
└── docs/
    └── frontend_setup.md    # Frontend documentation
```

---

## 3. Serving Frontend & Static Files

### Route Matrix
- `GET /`: API Health & Root JSON payload (`{"message": "...", "status": "healthy"}`)
- `GET /dashboard`: Executive Overview Jinja2 Dashboard HTML page
- `GET /static/...`: Serves CSS, JS, and static media from `static/` directory

### Portable Path Configuration (`app/main.py`)
```python
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
```

---

## 4. Executive Dashboard & KPI Cards

The dashboard at `/dashboard` displays six key performance metrics populated asynchronously via relative API path `/api/summary`:
1. **Total Sales**: Currency formatted (e.g., `$2.30M` / `$2,297,200.86`)
2. **Total Profit**: Currency formatted (e.g., `$286.40K` / `$286,397.02`)
3. **Total Orders**: Thousands separator formatted (e.g., `5,009`)
4. **Total Customers**: Thousands separator formatted (e.g., `793`)
5. **Profit Margin**: Percentage formatted (e.g., `12.46%`)
6. **Return Rate**: Percentage formatted (e.g., `5.43%`)

---

## 5. Dashboard Filters (Phase 6.3)

The dashboard includes an interactive filter panel above the KPI grid allowing users to filter analytics dynamically by:
- **Year**: All Years (`""`), 2020, 2021, 2022, 2023
- **Region**: All Regions (`""`), Central, East, South, West
- **Category**: All Categories (`""`), Furniture, Office Supplies, Technology
- **Segment**: All Segments (`""`), Consumer, Corporate, Home Office

---

## 6. ECharts Interactive Charts (Phase 6.4)

The dashboard features four interactive charts powered by Apache ECharts (`static/js/charts.js`), updated dynamically via shared filter state in `static/js/dashboard.js`:

| Chart Name | Element ID | Endpoint API | Visual Type | Key Metrics / Features |
|---|---|---|---|---|
| **Sales & Profit Trend** | `#salesTrendChart` | `GET /api/sales/monthly` | Smooth Line Chart | Dual series (Sales in blue `#2563eb`, Profit in green `#10b981`), legend, gradient fill, formatted currency tooltip |
| **Sales by Region** | `#regionChart` | `GET /api/sales/region` | Horizontal Bar Chart | Regional sales comparison, sorted rank |
| **Top Products** | `#productChart` | `GET /api/products/top?limit=10` | Horizontal Bar Chart | Top 10 products by sales, visual text truncation for long product names, full name tooltip |
| **Top Customers** | `#customerChart` | `GET /api/customers/top?limit=10` | Horizontal Bar Chart | Top 10 customer accounts by sales |

### Shared Filter State & Concurrent API Requests
- Clicking **Apply Filters** or **Reset** reads the single shared filter state (`year`, `region`, `category`, `segment`), constructs query parameters via `URLSearchParams`, and executes concurrent requests via `Promise.all([fetchSummary(), fetchMonthlySales(), fetchRegionSales(), fetchTopProducts(), fetchTopCustomers()])`.
- Charts update in-place without page reload using `chart.setOption()`.
- If an endpoint returns an empty array, the chart displays a clean empty state message: *"No data available for the selected filters."*
- Window resize events call `chart.resize()` automatically for fluid responsive behavior across desktop, tablet, and mobile screens.

---

## 7. How to Run Locally

1. Start the FastAPI development server:
   ```powershell
   .\venv\Scripts\python -m uvicorn app.main:app --reload
   ```

2. Open the Executive Dashboard in your browser:
   ```text
   http://127.0.0.1:8000/dashboard
   ```

3. Run the automated backend test suite:
   ```powershell
   .\venv\Scripts\python -m unittest discover -s tests
   ```
