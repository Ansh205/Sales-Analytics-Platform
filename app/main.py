from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes import analytics

# Base directory using portable pathlib
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
IMAGES_DIR = BASE_DIR / "images"

app = FastAPI(
    title="Sales Analytics Platform API",
    description="Provides analytics from the Sales Analytics Platform PostgreSQL database",
    version="1.0.0",
)

# Ensure directories exist before mounting
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files and images
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# Jinja2 template engine configuration
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include analytics API router
app.include_router(analytics.router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Redirect root URL to the Executive Overview dashboard.
    """
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/dashboard/", response_class=HTMLResponse, include_in_schema=False)
def render_dashboard(request: Request):
    """
    GET /dashboard
    Renders the Executive Analytics Dashboard Jinja2 HTML template.
    """
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"active_page": "overview"}
    )


@app.get("/products", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/products/", response_class=HTMLResponse, include_in_schema=False)
def render_products(request: Request):
    """
    GET /products
    Renders the Product Analytics Jinja2 HTML template.
    """
    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={"active_page": "products"}
    )


@app.get("/customers", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/customers/", response_class=HTMLResponse, include_in_schema=False)
def render_customers(request: Request):
    """
    GET /customers
    Renders the Customer Analytics Jinja2 HTML template.
    """
    return templates.TemplateResponse(
        request=request,
        name="customers.html",
        context={"active_page": "customers"}
    )


@app.get("/regions", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/regions/", response_class=HTMLResponse, include_in_schema=False)
def render_regions(request: Request):
    """
    GET /regions
    Renders the Regional Analytics Jinja2 HTML template.
    """
    return templates.TemplateResponse(
        request=request,
        name="regions.html",
        context={"active_page": "regions"}
    )


@app.get("/powerbi", response_class=HTMLResponse, tags=["Frontend"])
@app.get("/powerbi/", response_class=HTMLResponse, include_in_schema=False)
def render_powerbi(request: Request):
    """
    GET /powerbi
    Renders the Power BI Executive Dashboard Jinja2 HTML template.
    """
    return templates.TemplateResponse(
        request=request,
        name="powerbi.html",
        context={"active_page": "powerbi"}
    )



@app.get("/api/health/db", tags=["Health"])
def health_check_db(db: Session = Depends(get_db)):
    """
    Database connectivity health check endpoint.
    Executes SELECT 1 against PostgreSQL sales_analytics_db.
    """
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {
                "status": "healthy",
                "database": "connected",
            }
        raise Exception("Database query returned unexpected result")
    except Exception as e:
        # Server-side logging without exposing sensitive connection credentials
        print(f"[ERROR] Database health check failed: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection error",
        )
