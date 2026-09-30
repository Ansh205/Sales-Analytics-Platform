from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
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

app = FastAPI(
    title="Sales Analytics Platform API",
    description="Provides analytics from the Sales Analytics Platform PostgreSQL database",
    version="1.0.0",
)

# Ensure static directory exists before mounting
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Jinja2 template engine configuration
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include analytics API router
app.include_router(analytics.router)


@app.get("/", tags=["Root"])
def read_root():
    """
    API Root endpoint returning health status JSON payload.
    Retained for 100% Phase 5 backward compatibility and API health verification.
    """
    return {
        "message": "Sales Analytics Platform API is running",
        "status": "healthy",
    }


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
