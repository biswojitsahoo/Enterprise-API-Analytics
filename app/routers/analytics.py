from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.deps import get_current_user
from app.models import BusinessRecord, User
from app.schemas import AnalyticsOverview, MonthlyCount, StatusCount

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def overview(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    total = db.scalar(select(func.count(BusinessRecord.id))) or 0
    open_count = db.scalar(select(func.count(BusinessRecord.id)).where(BusinessRecord.status == "open")) or 0
    progress_count = db.scalar(select(func.count(BusinessRecord.id)).where(BusinessRecord.status == "in_progress")) or 0
    closed_count = db.scalar(select(func.count(BusinessRecord.id)).where(BusinessRecord.status == "closed")) or 0
    high_count = db.scalar(select(func.count(BusinessRecord.id)).where(BusinessRecord.priority.in_(["high", "critical"]))) or 0
    return AnalyticsOverview(total_records=total, open_records=open_count,
                             in_progress_records=progress_count, closed_records=closed_count,
                             high_priority_records=high_count)


@router.get("/status-breakdown", response_model=list[StatusCount])
def status_breakdown(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.execute(select(BusinessRecord.status, func.count(BusinessRecord.id))
                      .group_by(BusinessRecord.status).order_by(BusinessRecord.status)).all()
    return [{"status": status, "count": count} for status, count in rows]


@router.get("/records-by-month", response_model=list[MonthlyCount])
def records_by_month(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    # Use Python grouping to keep the endpoint portable across PostgreSQL and SQLite.
    rows = db.scalars(select(BusinessRecord.created_at).order_by(BusinessRecord.created_at)).all()
    counts: dict[str, int] = {}
    for created_at in rows:
        month = created_at.strftime("%Y-%m")
        counts[month] = counts.get(month, 0) + 1
    return [{"month": month, "count": count} for month, count in sorted(counts.items())]
