# Sentry Integration Guide

This document describes how to use Sentry error tracking and performance monitoring in the REE AI platform.

## Overview

Sentry is integrated into the platform to provide:
- **Error Tracking**: Automatic capture and reporting of exceptions
- **Performance Monitoring**: Transaction tracing and performance metrics
- **User Context**: Track which users are affected by errors
- **Request Context**: Full request data for debugging
- **Breadcrumbs**: Track user actions leading to errors
- **Data Privacy**: Automatic filtering of sensitive data (passwords, tokens, etc.)

## Configuration

### 1. Environment Variables

Add these variables to your `.env` file:

```bash
# Sentry Error Tracking
SENTRY_DSN=https://your-key@o123456.ingest.sentry.io/123456
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=1.0
```

**Configuration Options:**

- `SENTRY_DSN`: Your Sentry project DSN (Data Source Name)
  - Get this from your Sentry project settings
  - Leave empty to disable Sentry

- `SENTRY_ENVIRONMENT`: Environment name for organizing errors
  - Common values: `development`, `staging`, `production`
  - Used to filter errors in Sentry dashboard

- `SENTRY_TRACES_SAMPLE_RATE`: Performance monitoring sample rate
  - `1.0` = 100% of transactions (recommended for development)
  - `0.1` = 10% of transactions (recommended for high-traffic production)
  - `0.0` = Disable performance monitoring

### 2. Get Your Sentry DSN

1. Create a Sentry account at https://sentry.io
2. Create a new project (select Python/FastAPI)
3. Copy the DSN from Project Settings > Client Keys (DSN)
4. Add to your `.env` file

## Basic Usage

### Initialize Sentry in Your Service

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.utils.sentry import init_sentry
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Service starting up...")

    # Initialize Sentry
    init_sentry(service_name="my-service")

    yield
    logger.info("👋 Service shutting down...")

app = FastAPI(
    title="My Service",
    lifespan=lifespan
)
```

## Advanced Usage

### 1. Automatic Exception Capture with Decorator

```python
from shared.utils.sentry import capture_exception_decorator

@app.post("/process")
@capture_exception_decorator(
    tags={"feature": "data-processing"},
    context={"module": "processing"},
    re_raise=True
)
async def process_data(data: dict):
    # Any exception here is automatically captured
    result = perform_complex_operation(data)
    return result
```

### 2. Manual Exception Capture

```python
from shared.utils.sentry import capture_exception

@app.post("/custom-error")
async def custom_error_handling():
    try:
        risky_operation()
    except Exception as e:
        # Capture with custom context
        event_id = capture_exception(
            error=e,
            context={
                "operation": "risky_operation",
                "input_data": {"key": "value"}
            },
            tags={
                "service": "my-service",
                "severity": "high"
            },
            level="error"
        )
        logger.error(f"❌ Error captured: {event_id}")

        # Return user-friendly error
        raise HTTPException(status_code=500, detail="Operation failed")
```

### 3. Performance Tracing

```python
from shared.utils.sentry import trace_function

@trace_function(operation="db.query")
async def fetch_user(user_id: str):
    """This function's performance will be tracked"""
    # Database operation
    user = await db.query(User).filter(User.id == user_id).first()
    return user

@trace_function(operation="llm.call")
async def call_llm(prompt: str):
    """Track LLM API call performance"""
    response = await llm_client.complete(prompt)
    return response
```

### 4. Custom Transactions

```python
from shared.utils.sentry import start_transaction

@app.post("/complex-task")
async def complex_task():
    # Start a transaction
    with start_transaction(name="complex_task", op="task") as transaction:

        # Step 1: Database query
        with transaction.start_child(op="db.query", description="Fetch data"):
            data = await fetch_data()

        # Step 2: External API
        with transaction.start_child(op="http.client", description="Call API"):
            api_result = await call_external_api()

        # Step 3: Processing
        with transaction.start_child(op="process", description="Process results"):
            result = process_results(data, api_result)

    return result
```

### 5. User Context

```python
from shared.utils.sentry import set_user_context

@app.get("/user/{user_id}")
async def get_user(user_id: str):
    # Set user context for all subsequent errors
    set_user_context(
        user_id=user_id,
        username="john_doe",
        email="john@example.com"
    )

    # Now any errors will be associated with this user
    user_data = await fetch_user_data(user_id)
    return user_data
```

### 6. Request Context

```python
from shared.utils.sentry import set_request_context

@app.post("/api/endpoint")
async def api_endpoint(request: Request):
    # Set request context
    request_id = request.headers.get("X-Request-ID", "unknown")
    set_request_context(
        request_id=request_id,
        endpoint="/api/endpoint",
        method="POST",
        ip_address=request.client.host
    )

    # Process request...
    return {"status": "success"}
```

### 7. Breadcrumbs

```python
from shared.utils.sentry import add_breadcrumb

@app.post("/checkout")
async def checkout(cart_id: str):
    add_breadcrumb(
        message="Starting checkout process",
        category="checkout",
        level="info",
        data={"cart_id": cart_id}
    )

    # Step 1
    add_breadcrumb(message="Validating cart", category="validation")
    validate_cart(cart_id)

    # Step 2
    add_breadcrumb(message="Processing payment", category="payment")
    process_payment(cart_id)

    # Step 3
    add_breadcrumb(message="Creating order", category="order")
    order = create_order(cart_id)

    return order
```

### 8. Capture Custom Messages

```python
from shared.utils.sentry import capture_message

@app.post("/admin/action")
async def admin_action(action: str):
    # Log important events that aren't errors
    capture_message(
        message=f"Admin performed action: {action}",
        level="warning",
        tags={"action": action, "user_type": "admin"},
        context={"timestamp": datetime.now().isoformat()}
    )

    return {"status": "success"}
```

### 9. Middleware for Automatic Context

```python
from shared.utils.sentry import set_request_context, set_user_context, add_breadcrumb

@app.middleware("http")
async def sentry_middleware(request: Request, call_next):
    """Automatically set context for all requests"""

    # Set request context
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    set_request_context(
        request_id=request_id,
        endpoint=request.url.path,
        method=request.method
    )

    # Set user context if authenticated
    user_id = request.headers.get("X-User-ID")
    if user_id:
        set_user_context(user_id=user_id)

    # Add request breadcrumb
    add_breadcrumb(
        message=f"{request.method} {request.url.path}",
        category="http",
        level="info"
    )

    response = await call_next(request)
    return response
```

## Data Privacy

The Sentry integration automatically filters sensitive data:

### Automatically Filtered Fields:
- **Headers**: `Authorization`, `Cookie`, `X-Api-Key`, `X-Auth-Token`
- **Request Body**: `password`, `token`, `secret`, `api_key`, `credentials`, `private_key`
- **Query Strings**: Containing `token` or `key`
- **Email Addresses**: Partially masked (e.g., `jo***@example.com`)

### Custom Filtering:

If you need additional filtering, you can modify the `_before_send` function in `shared/utils/sentry.py`.

## Best Practices

### 1. Service Naming
Always use descriptive service names when initializing:
```python
init_sentry(service_name="api-gateway")  # Good
init_sentry(service_name="service")       # Bad
```

### 2. Meaningful Tags
Use tags for filtering in Sentry dashboard:
```python
capture_exception(
    error=e,
    tags={
        "feature": "authentication",
        "endpoint": "/login",
        "severity": "high"
    }
)
```

### 3. Rich Context
Provide context to help debugging:
```python
capture_exception(
    error=e,
    context={
        "user_action": "checkout",
        "cart_items": 5,
        "payment_method": "credit_card",
        "total_amount": 99.99
    }
)
```

### 4. Appropriate Levels
Use the right level for each event:
- `error`: Exceptions and errors
- `warning`: Important events, potential issues
- `info`: General information
- `debug`: Detailed debugging information

### 5. Sample Rate Configuration
For production services with high traffic:
```bash
# Sample 10% of transactions
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### 6. Don't Over-Instrument
Only trace expensive or critical operations:
```python
# Good - trace expensive operations
@trace_function(operation="llm.call")
async def call_llm(prompt: str):
    ...

# Bad - don't trace simple operations
@trace_function(operation="validation")
def validate_string(s: str):
    return len(s) > 0
```

## Testing

To test Sentry integration:

### 1. Test Error Capture
```python
@app.get("/test-sentry-error")
async def test_error():
    """Test endpoint to verify Sentry is working"""
    try:
        1 / 0
    except Exception as e:
        event_id = capture_exception(e)
        return {"event_id": event_id, "message": "Check Sentry dashboard"}
```

### 2. Test Performance Monitoring
```python
@app.get("/test-sentry-performance")
async def test_performance():
    """Test endpoint to verify performance monitoring"""
    with start_transaction(name="test_transaction", op="test"):
        import asyncio
        await asyncio.sleep(0.1)
    return {"message": "Check Sentry performance dashboard"}
```

## Monitoring Dashboard

In your Sentry dashboard, you can:

1. **View Errors**: See all captured exceptions
2. **Filter by Service**: Use the `service` tag
3. **Filter by Environment**: Use `development`, `staging`, `production`
4. **View Performance**: See transaction traces and slow operations
5. **User Impact**: See which users are affected
6. **Trends**: Monitor error rates over time
7. **Alerts**: Set up alerts for critical errors

## Troubleshooting

### Sentry Not Capturing Errors

1. Check if `SENTRY_DSN` is set:
   ```bash
   echo $SENTRY_DSN
   ```

2. Check service logs for initialization message:
   ```
   ✅ Sentry initialized for my-service in production environment
   ```

3. If you see this warning, Sentry is disabled:
   ```
   ⚠️  Sentry DSN not configured - skipping Sentry initialization
   ```

### Performance Monitoring Not Working

1. Check `SENTRY_TRACES_SAMPLE_RATE` is > 0:
   ```bash
   SENTRY_TRACES_SAMPLE_RATE=1.0
   ```

2. Verify transactions are being created:
   ```python
   with start_transaction(name="test", op="test"):
       print("Transaction started")
   ```

### Sensitive Data Not Filtered

1. Review the `_before_send` function in `shared/utils/sentry.py`
2. Add custom filtering for your specific fields
3. Use `send_default_pii=False` (already configured)

## Example Service Integration

See `shared/utils/sentry_example.py` for a complete working example of all Sentry features.

## Additional Resources

- [Sentry Python SDK Documentation](https://docs.sentry.io/platforms/python/)
- [FastAPI Integration](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Data Privacy](https://docs.sentry.io/data-management/sensitive-data/)

## Support

For issues or questions about Sentry integration:
1. Check the Sentry dashboard for error details
2. Review service logs for Sentry initialization
3. Consult this documentation
4. Check the example file: `shared/utils/sentry_example.py`
