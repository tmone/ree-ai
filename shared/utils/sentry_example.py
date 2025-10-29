"""
Example usage of Sentry integration in REE AI services

This file demonstrates how to integrate Sentry error tracking
into your FastAPI services.
"""

from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager

# Import Sentry utilities
from shared.utils.sentry import (
    init_sentry,
    capture_exception,
    capture_message,
    set_user_context,
    set_request_context,
    add_breadcrumb,
    trace_function,
    capture_exception_decorator,
    start_transaction,
)
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


# ============================================================
# EXAMPLE 1: Basic Service Integration
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events with Sentry initialization"""
    # Initialize Sentry on startup
    logger.info("🚀 Service starting up...")
    init_sentry(service_name="example-service")
    logger.info("✅ Service ready!")
    yield
    logger.info("👋 Service shutting down...")


app = FastAPI(
    title="REE AI - Example Service",
    description="Example service with Sentry integration",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================
# EXAMPLE 2: Manual Exception Capture
# ============================================================

@app.post("/manual-capture")
async def manual_capture_example():
    """Example of manually capturing exceptions"""
    try:
        # Your code here
        result = 1 / 0  # This will raise ZeroDivisionError

    except Exception as e:
        # Manually capture the exception with context
        event_id = capture_exception(
            error=e,
            context={
                "operation": "division",
                "values": {"numerator": 1, "denominator": 0}
            },
            tags={
                "service": "example-service",
                "feature": "calculation"
            },
            level="error"
        )
        logger.error(f"❌ Exception captured: {event_id}")

        raise HTTPException(status_code=500, detail="Calculation failed")


# ============================================================
# EXAMPLE 3: Decorator-based Exception Capture
# ============================================================

@app.post("/decorator-capture")
@capture_exception_decorator(
    tags={"endpoint": "decorator-capture"},
    context={"feature": "auto-capture"},
    re_raise=True  # Re-raise the exception after capturing
)
async def decorator_capture_example():
    """Example using decorator for automatic exception capture"""
    # Any exception raised here will be automatically captured
    result = 1 / 0
    return {"result": result}


# ============================================================
# EXAMPLE 4: Function Tracing for Performance Monitoring
# ============================================================

@trace_function(operation="db.query")
async def fetch_user_from_db(user_id: str):
    """Example function with performance tracing"""
    # Simulate database query
    import asyncio
    await asyncio.sleep(0.1)
    return {"user_id": user_id, "name": "John Doe"}


@app.get("/user/{user_id}")
async def get_user(user_id: str):
    """Endpoint with traced database call"""
    # Set user context for error tracking
    set_user_context(user_id=user_id)

    # Add breadcrumb
    add_breadcrumb(
        message=f"Fetching user {user_id}",
        category="database",
        level="info"
    )

    # Call traced function
    user = await fetch_user_from_db(user_id)

    return user


# ============================================================
# EXAMPLE 5: Request Context and Breadcrumbs
# ============================================================

@app.post("/process-data")
async def process_data(request: Request, data: dict):
    """Example with request context and breadcrumbs"""

    # Set request context
    request_id = request.headers.get("X-Request-ID", "unknown")
    set_request_context(
        request_id=request_id,
        endpoint="/process-data",
        method="POST"
    )

    # Add breadcrumbs to track the flow
    add_breadcrumb(
        message="Starting data processing",
        category="process",
        level="info",
        data={"data_size": len(data)}
    )

    try:
        # Step 1: Validate data
        add_breadcrumb(
            message="Validating data",
            category="validation",
            level="info"
        )
        if not data.get("required_field"):
            raise ValueError("Missing required field")

        # Step 2: Process data
        add_breadcrumb(
            message="Processing data",
            category="process",
            level="info"
        )
        result = {"processed": True, "data": data}

        # Step 3: Complete
        add_breadcrumb(
            message="Processing completed",
            category="process",
            level="info"
        )

        return result

    except Exception as e:
        # All breadcrumbs will be included in the error report
        capture_exception(
            error=e,
            tags={"endpoint": "process-data"},
            level="error"
        )
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# EXAMPLE 6: Custom Transactions for Performance Monitoring
# ============================================================

@app.post("/complex-operation")
async def complex_operation():
    """Example with custom transaction and spans"""

    # Start a transaction
    with start_transaction(name="complex_operation", op="task") as transaction:
        # Step 1: Database query
        with transaction.start_child(op="db.query", description="Fetch data"):
            # Simulate database query
            import asyncio
            await asyncio.sleep(0.1)
            data = {"id": 1, "value": "test"}

        # Step 2: External API call
        with transaction.start_child(op="http.client", description="Call external API"):
            # Simulate API call
            await asyncio.sleep(0.2)
            api_result = {"status": "success"}

        # Step 3: Processing
        with transaction.start_child(op="process", description="Process results"):
            # Simulate processing
            await asyncio.sleep(0.05)
            result = {**data, **api_result}

    return result


# ============================================================
# EXAMPLE 7: Capture Messages (Non-Exception Events)
# ============================================================

@app.post("/important-action")
async def important_action(user_id: str):
    """Example of capturing important events as messages"""

    # Capture an informational message
    capture_message(
        message=f"User {user_id} performed important action",
        level="info",
        tags={"action": "important", "user": user_id},
        context={"timestamp": "2025-10-29"}
    )

    return {"status": "success"}


# ============================================================
# EXAMPLE 8: Middleware for Automatic Request Context
# ============================================================

@app.middleware("http")
async def sentry_context_middleware(request: Request, call_next):
    """Middleware to automatically set request context for all requests"""

    # Set request context
    request_id = request.headers.get("X-Request-ID", "unknown")
    user_id = request.headers.get("X-User-ID")

    set_request_context(
        request_id=request_id,
        endpoint=request.url.path,
        method=request.method
    )

    # Set user context if available
    if user_id:
        set_user_context(user_id=user_id)

    # Add breadcrumb
    add_breadcrumb(
        message=f"{request.method} {request.url.path}",
        category="http",
        level="info",
        data={"request_id": request_id}
    )

    response = await call_next(request)
    return response


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "example-service",
        "sentry_enabled": bool(init_sentry)
    }


# ============================================================
# USAGE NOTES
# ============================================================
"""
To use Sentry in your service:

1. Add Sentry DSN to your .env file:
   SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
   SENTRY_ENVIRONMENT=production
   SENTRY_TRACES_SAMPLE_RATE=1.0

2. Initialize Sentry in your startup event:
   from shared.utils.sentry import init_sentry

   @asynccontextmanager
   async def lifespan(app: FastAPI):
       init_sentry(service_name="your-service-name")
       yield

3. Use decorators for automatic error capture:
   @capture_exception_decorator(tags={"feature": "auth"})
   async def authenticate_user(token: str):
       ...

4. Use manual capture when you need more control:
   try:
       ...
   except Exception as e:
       capture_exception(e, context={...}, tags={...})

5. Add breadcrumbs to track user flow:
   add_breadcrumb(message="User logged in", category="auth")

6. Trace expensive functions:
   @trace_function(operation="llm.call")
   async def call_llm(prompt: str):
       ...

7. Set user context for better debugging:
   set_user_context(user_id="123", username="john")

8. Use transactions for complex operations:
   with start_transaction(name="process_order", op="task"):
       ...
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
