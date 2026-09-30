"""
Core Analytics API Endpoints for Sales Analytics Platform (Phase 5.3 & Phase 5.4).
Exposes PostgreSQL views and analytics through REST API endpoints with interactive filtering.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Analytics"])


def clean_val(val: Any) -> Any:
    """
    Convert database types like Decimal into JSON-serializable standard Python types.
    Integers or whole-number Decimals become int, floating Decimals become float.
    """
    if isinstance(val, Decimal):
        if val % 1 == 0:
            return int(val)
        return float(val)
    return val


def clean_row(row_mapping: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a database row mapping into a clean JSON-serializable dictionary.
    """
    return {k: clean_val(v) for k, v in row_mapping.items()}


def build_where_clause(
    year: Optional[int] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    table_prefix: str = "",
) -> tuple[str, Dict[str, Any]]:
    """
    Build parameterized SQL WHERE clause and parameter dictionary safely.
    Prevents SQL injection using bind variables.
    """
    conditions = []
    params: Dict[str, Any] = {}
    prefix = f"{table_prefix}." if table_prefix else ""

    if year is not None:
        conditions.append(f"{prefix}order_year = :year")
        params["year"] = year
    if region is not None:
        conditions.append(f"{prefix}region = :region")
        params["region"] = region
    if category is not None:
        conditions.append(f"{prefix}category = :category")
        params["category"] = category
    if segment is not None:
        conditions.append(f"{prefix}segment = :segment")
        params["segment"] = segment

    where_str = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where_str, params


@router.get("/summary")
def get_executive_summary(
    year: Optional[int] = Query(None, description="Filter by order year"),
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by category"),
    segment: Optional[str] = Query(None, description="Filter by customer segment"),
    db: Session = Depends(get_db),
):
    """
    GET /api/summary
    Return main business KPIs with optional filtering by year, region, category, and segment.
    """
    try:
        where_str, params = build_where_clause(year, region, category, segment)
        where_str_o, params_o = build_where_clause(year, region, category, segment, table_prefix="o")

        # When no filters are passed, query vw_executive_summary for 100% Phase 5.3 backward compatibility
        if not params:
            query = text("""
                SELECT 
                    e.total_sales,
                    e.total_profit,
                    e.total_orders,
                    e.total_customers,
                    e.avg_profit_margin AS profit_margin,
                    (
                        SELECT ROUND(COUNT(DISTINCT r.order_id) * 100.0 / NULLIF(COUNT(DISTINCT o.order_id), 0), 2)
                        FROM orders o
                        LEFT JOIN returns r ON o.order_id = r.order_id
                    ) AS return_rate
                FROM vw_executive_summary e;
            """)
            row = db.execute(query).mappings().first()
        else:
            query = text(f"""
                SELECT 
                    COALESCE(ROUND(SUM(sales), 2), 0) AS total_sales,
                    COALESCE(ROUND(SUM(profit), 2), 0) AS total_profit,
                    COUNT(DISTINCT order_id) AS total_orders,
                    COUNT(DISTINCT customer_id) AS total_customers,
                    COALESCE(ROUND(SUM(profit) * 100.0 / NULLIF(SUM(sales), 0), 2), 0) AS profit_margin,
                    (
                        SELECT COALESCE(ROUND(COUNT(DISTINCT r.order_id) * 100.0 / NULLIF(COUNT(DISTINCT o.order_id), 0), 2), 0)
                        FROM orders o
                        LEFT JOIN returns r ON o.order_id = r.order_id
                        {where_str_o}
                    ) AS return_rate
                FROM orders
                {where_str};
            """)
            row = db.execute(query, params).mappings().first()

        if not row:
            return {
                "total_sales": 0,
                "total_profit": 0,
                "total_orders": 0,
                "total_customers": 0,
                "profit_margin": 0,
                "return_rate": 0,
            }
        return clean_row(dict(row))
    except Exception as e:
        logger.error(f"Error fetching executive summary: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve analytics data",
        )


@router.get("/sales/summary")
def get_sales_summary(
    year: Optional[int] = Query(None, description="Filter by order year"),
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by category"),
    segment: Optional[str] = Query(None, description="Filter by customer segment"),
    db: Session = Depends(get_db),
):
    """
    GET /api/sales/summary
    Return overall sales-related metrics with optional filtering.
    """
    try:
        where_str, params = build_where_clause(year, region, category, segment)
        query = text(f"""
            SELECT 
                COALESCE(ROUND(SUM(sales), 2), 0) AS total_sales,
                COALESCE(ROUND(SUM(profit), 2), 0) AS total_profit,
                COUNT(DISTINCT order_id) AS total_orders,
                COALESCE(SUM(quantity), 0) AS total_quantity,
                COALESCE(ROUND(SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0), 2), 0) AS average_order_value,
                COALESCE(ROUND(AVG(discount), 2), 0) AS average_discount,
                COALESCE(ROUND(AVG(profit_margin), 2), 0) AS profit_margin
            FROM orders
            {where_str};
        """)
        row = db.execute(query, params).mappings().first()
        if not row:
            return {
                "total_sales": 0,
                "total_profit": 0,
                "total_orders": 0,
                "total_quantity": 0,
                "average_order_value": 0,
                "average_discount": 0,
                "profit_margin": 0,
            }
        return clean_row(dict(row))
    except Exception as e:
        logger.error(f"Error fetching sales summary: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve analytics data",
        )


@router.get("/sales/monthly")
def get_monthly_sales(
    year: Optional[int] = Query(None, description="Filter by order year"),
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by category"),
    segment: Optional[str] = Query(None, description="Filter by customer segment"),
    db: Session = Depends(get_db),
):
    """
    GET /api/sales/monthly
    Return monthly sales and profit performance in chronological order with optional filtering.
    """
    try:
        where_str, params = build_where_clause(year, region, category, segment)
        query = text(f"""
            SELECT 
                order_year AS year,
                order_month AS month,
                ROUND(SUM(sales), 2) AS sales,
                ROUND(SUM(profit), 2) AS profit
            FROM orders
            {where_str}
            GROUP BY order_year, order_month
            ORDER BY order_year, order_month;
        """)
        rows = db.execute(query, params).mappings().all()
        return [clean_row(dict(r)) for r in rows]
    except Exception as e:
        logger.error(f"Error fetching monthly sales: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve analytics data",
        )


@router.get("/sales/region")
def get_regional_sales(
    year: Optional[int] = Query(None, description="Filter by order year"),
    category: Optional[str] = Query(None, description="Filter by category"),
    segment: Optional[str] = Query(None, description="Filter by customer segment"),
    db: Session = Depends(get_db),
):
    """
    GET /api/sales/region
    Return sales and profit performance aggregated by region with optional filtering.
    """
    try:
        where_str, params = build_where_clause(year=year, category=category, segment=segment)
        query = text(f"""
            SELECT 
                region,
                ROUND(SUM(sales), 2) AS sales,
                ROUND(SUM(profit), 2) AS profit,
                COUNT(DISTINCT order_id) AS orders
            FROM orders
            {where_str}
            GROUP BY region
            ORDER BY sales DESC;
        """)
        rows = db.execute(query, params).mappings().all()
        return [clean_row(dict(r)) for r in rows]
    except Exception as e:
        logger.error(f"Error fetching regional sales: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve analytics data",
        )


@router.get("/products/top")
def get_top_products(
    year: Optional[int] = Query(None, description="Filter by order year"),
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by category"),
    segment: Optional[str] = Query(None, description="Filter by customer segment"),
    limit: int = Query(10, ge=1, le=100, description="Top-N limit (1-100)"),
    db: Session = Depends(get_db),
):
    """
    GET /api/products/top
    Return top N products by sales with optional filtering.
    """
    try:
        where_str, params = build_where_clause(year, region, category, segment)
        params["limit"] = limit
        query = text(f"""
            SELECT 
                product_name,
                category,
                sub_category,
                ROUND(SUM(sales), 2) AS sales,
                ROUND(SUM(profit), 2) AS profit
            FROM orders
            {where_str}
            GROUP BY product_name, category, sub_category
            ORDER BY sales DESC
            LIMIT :limit;
        """)
        rows = db.execute(query, params).mappings().all()
        return [clean_row(dict(r)) for r in rows]
    except Exception as e:
        logger.error(f"Error fetching top products: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve analytics data",
        )


@router.get("/customers/top")
def get_top_customers(
    year: Optional[int] = Query(None, description="Filter by order year"),
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by category"),
    segment: Optional[str] = Query(None, description="Filter by customer segment"),
    limit: int = Query(10, ge=1, le=100, description="Top-N limit (1-100)"),
    db: Session = Depends(get_db),
):
    """
    GET /api/customers/top
    Return top N customers by sales with optional filtering.
    """
    try:
        where_str, params = build_where_clause(year, region, category, segment)
        params["limit"] = limit
        query = text(f"""
            SELECT 
                customer_id,
                customer_name,
                segment,
                ROUND(SUM(sales), 2) AS sales,
                ROUND(SUM(profit), 2) AS profit
            FROM orders
            {where_str}
            GROUP BY customer_id, customer_name, segment
            ORDER BY sales DESC
            LIMIT :limit;
        """)
        rows = db.execute(query, params).mappings().all()
        return [clean_row(dict(r)) for r in rows]
    except Exception as e:
        logger.error(f"Error fetching top customers: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve analytics data",
        )
