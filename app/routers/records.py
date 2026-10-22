from math import ceil
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.deps import get_current_user, require_roles
from app.models import BusinessRecord, User
from app.schemas import RecordCreate, RecordPage, RecordRead, RecordUpdate

router = APIRouter(prefix="/records", tags=["Business Records"])


@router.get("", response_model=RecordPage)
def list_records(
    q: str | None = Query(default=None, max_length=200),
    status_filter: Literal["open", "in_progress", "closed"] | None = Query(default=None, alias="status"),
    priority: Literal["low", "medium", "high", "critical"] | None = None,
    owner: str | None = Query(default=None, max_length=120),
    sort_by: Literal["created_at", "updated_at", "title", "priority"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    stmt = select(BusinessRecord)
    filters = []
    if q:
        term = f"%{q.strip()}%"
        filters.append(or_(BusinessRecord.title.ilike(term), BusinessRecord.description.ilike(term)))
    if status_filter:
        filters.append(BusinessRecord.status == status_filter)
    if priority:
        filters.append(BusinessRecord.priority == priority)
    if owner:
        filters.append(BusinessRecord.owner.ilike(f"%{owner.strip()}%"))
    if filters:
        stmt = stmt.where(*filters)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    sort_column = getattr(BusinessRecord, sort_by)
    stmt = stmt.order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc())
    rows = list(db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all())
    return RecordPage(items=rows, total=total, page=page, page_size=page_size,
                      pages=ceil(total / page_size) if total else 0)


@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(payload: RecordCreate, db: Session = Depends(get_db),
                  user: User = Depends(require_roles("admin", "analyst"))):
    record = BusinessRecord(**payload.model_dump(), created_by_id=user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{record_id}", response_model=RecordRead)
def get_record(record_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    record = db.get(BusinessRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.patch("/{record_id}", response_model=RecordRead)
def update_record(record_id: int, payload: RecordUpdate, db: Session = Depends(get_db),
                  _: User = Depends(require_roles("admin", "analyst"))):
    record = db.get(BusinessRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int, db: Session = Depends(get_db),
                  _: User = Depends(require_roles("admin"))):
    record = db.get(BusinessRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return None
