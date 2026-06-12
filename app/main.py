import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database import Base, engine
from app.routes import auth, contacts, users
from app.services.redis_cache import cache


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.

    On startup:
    - initializes database tables
    - checks Redis connection

    On shutdown:
    - closes Redis connection
    """

    logger.info("Starting application")

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized")
    except Exception as error:
        logger.error(f"Database startup error: {error}")

    try:
        await cache.redis.ping()
        logger.info("Redis connected")
    except Exception as error:
        logger.warning(f"Redis unavailable: {error}")

    yield

    logger.info("Shutting down application")

    try:
        await cache.close()
        logger.info("Redis connection closed")
    except Exception as error:
        logger.warning(f"Redis shutdown error: {error}")


app = FastAPI(
    title="Contacts API",
    description="REST API for contacts management with JWT authentication, Redis caching and role-based access control",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming HTTP requests.

    :param request: Incoming request.
    :param call_next: FastAPI handler.
    :return: Response object.
    """

    start_time = time.time()

    try:
        response = await call_next(request)

    except Exception as error:
        logger.error(f"Request failed: {error}")
        raise

    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"| status={response.status_code} "
        f"| time={process_time:.4f}s"
    )

    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    """
    Handle FastAPI HTTP exceptions.

    :param request: Incoming request.
    :param exc: HTTP exception.
    :return: JSON response.
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Handle unexpected application errors.

    :param request: Incoming request.
    :param exc: Unexpected exception.
    :return: JSON response.
    """

    logger.error(f"Unhandled exception: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error"
        },
    )


@app.get("/", tags=["Healthcheck"])
async def root():
    """
    Root endpoint.

    :return: API information.
    """

    return {
        "message": "Contacts API is running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Healthcheck"])
async def health_check():
    """
    General health check.

    :return: Service status.
    """

    return {
        "status": "ok"
    }


@app.get("/health/db", tags=["Healthcheck"])
async def health_db():
    """
    Verify database connection.

    :return: Database status.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "database": "ok"
        }

    except Exception as error:
        logger.error(f"Database error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Database connection failed",
        )


@app.get("/health/redis", tags=["Healthcheck"])
async def health_redis():
    """
    Verify Redis connection.

    :return: Redis status.
    """

    try:
        await cache.redis.ping()

        return {
            "redis": "ok"
        }

    except Exception as error:
        logger.error(f"Redis error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Redis connection failed",
        )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(contacts.router)