import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import text
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app import models  # noqa: F401 - registers ORM models
from app.models import User
from app.routers import analytics, auth, records, users

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("enterprise_api")
FRONTEND_PATH = Path(__file__).resolve().parent.parent / "frontend" / "index.html"

 
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.seed_admin:
        with SessionLocal() as db:
            admin_email = settings.admin_email.lower()
            admin = db.query(User).filter(User.email == admin_email).first()
            if not admin:
                db.add(User(email=admin_email, full_name="Development Admin",
                            hashed_password=hash_password(settings.admin_password), role="admin"))
                db.commit()
                logger.warning("Seeded development admin account. Change its password before deployment.")
    yield


app = FastAPI(title=settings.app_name, version="1.0.0",
              description="Authenticated business-record APIs and analytics.", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_id_and_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled error request_id=%s path=%s", request_id, request.url.path)
        response = JSONResponse(status_code=500, content={"detail": "Internal server error"})
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health", tags=["Health"])
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "reachable"}
    except Exception:
        logger.exception("Health check failed")
        return JSONResponse(status_code=503, content={"status": "error", "database": "unavailable"})


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(FRONTEND_PATH)


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(records.router, prefix=settings.api_v1_prefix)
app.include_router(analytics.router, prefix=settings.api_v1_prefix)
