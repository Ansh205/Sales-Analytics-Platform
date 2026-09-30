from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes import analytics

app = FastAPI(
    title="Sales Analytics Platform API",
    description="Provides analytics from the Sales Analytics Platform PostgreSQL database",
    version="1.0.0",
)

app.include_router(analytics.router)


@app.get("/")
def read_root():
    return {
        "message": "Sales Analytics Platform API is running",
        "status": "healthy",
    }


@app.get("/api/health/db")
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
