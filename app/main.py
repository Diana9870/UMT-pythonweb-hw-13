import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import Base, engine
from app.routes import auth, users, contacts
from app.services.redis_cache import cache


# -------------------- LOGGING --------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("app")


# -------------------- LIFESPAN --------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown logic.
    Initializes DB and checks Redis connection.
    """
    logger.info("🚀 Starting application...")

    # DB init
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database connected")

    # Redis check
    try:
        await cache.client.ping()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️ Redis not available: {e}")

    yield

    # Shutdown
    logger.info("🛑 Shutting down application...")

    try:
        await cache.client.close()
        logger.info("✅ Redis connection closed")
    except Exception:
        pass


# -------------------- APP --------------------

app = FastAPI(
    title="Contacts API",
    description="Contacts manager with JWT auth, Redis cache, and role-based access",
    version="1.0.0",
    lifespan=lifespan,
)


# -------------------- CORS --------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # у проді краще обмежити
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------- MIDDLEWARE --------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Logs all incoming requests with execution time.
    """
    start_time = time.time()

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"❌ Request failed: {e}")
        raise

    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.4f}s"
    )

    return response


# -------------------- EXCEPTION HANDLERS --------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles FastAPI HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handles unexpected errors.
    """
    logger.error(f"❌ Unhandled error: {exc}")

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


# -------------------- HEALTHCHECK --------------------

@app.get("/", tags=["Healthcheck"])
def root():
    """
    Root endpoint.
    """
    return {
        "message": "API is running 🚀",
        "docs": "/docs",
    }


@app.get("/health", tags=["Healthcheck"])
def health_check():
    """
    Basic health check.
    """
    return {"status": "ok"}


@app.get("/health/db", tags=["Healthcheck"])
def health_db():
    """
    Check database connection.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/health/redis", tags=["Healthcheck"])
async def health_redis():
    """
    Check Redis connection.
    """
    try:
        await cache.client.ping()
        return {"redis": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="Redis error")


# -------------------- ROUTERS --------------------

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(contacts.router)  # prefix вже всередині