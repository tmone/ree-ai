# Sentry Integration Setup

## Quick Start Guide

### 1. Install Sentry SDK

Add to your `requirements.txt` or install directly:

```bash
pip install sentry-sdk[fastapi]
```

Or add to `requirements.txt`:
```
sentry-sdk[fastapi]>=1.40.0
```

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Sentry Error Tracking
SENTRY_DSN=https://your-key@o123456.ingest.sentry.io/123456
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
```

**Get Your Sentry DSN:**
1. Sign up at https://sentry.io (free tier available)
2. Create a new Python/FastAPI project
3. Copy the DSN from Project Settings > Client Keys
4. Paste into your `.env` file

### 3. Initialize in Your Service

Update your service's `main.py`:

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
    init_sentry(service_name="your-service-name")

    logger.info("✅ Service ready!")
    yield
    logger.info("👋 Service shutting down...")

app = FastAPI(
    title="Your Service",
    lifespan=lifespan
)
```

### 4. Test the Integration

Add a test endpoint to verify Sentry is working:

```python
from shared.utils.sentry import capture_exception

@app.get("/test-sentry")
async def test_sentry():
    """Test endpoint to verify Sentry integration"""
    try:
        # Intentional error
        result = 1 / 0
    except Exception as e:
        event_id = capture_exception(e)
        return {
            "message": "Error captured!",
            "event_id": event_id,
            "check": "https://sentry.io to see the error"
        }
```

Visit `http://localhost:8080/test-sentry` and check your Sentry dashboard.

## What's Included

The integration provides:

✅ **Automatic Error Tracking**
- All uncaught exceptions are captured
- Full stack traces
- Request data (with sensitive data filtered)

✅ **Performance Monitoring**
- Transaction tracing
- Slow operation detection
- Database query monitoring

✅ **User Context**
- Track which users experience errors
- User actions before errors

✅ **Request Context**
- Full request details
- Headers (sensitive data filtered)
- Query parameters

✅ **Data Privacy**
- Automatic filtering of passwords, tokens, API keys
- Email masking
- Configurable sensitive field filtering

✅ **Easy-to-Use API**
- Decorators for automatic capture
- Manual capture with context
- Breadcrumbs for debugging
- Performance tracing

## Files Created

1. **`shared/utils/sentry.py`** - Main Sentry integration module
   - `init_sentry()` - Initialize Sentry for your service
   - `capture_exception()` - Manually capture exceptions
   - `trace_function()` - Decorator for performance tracing
   - `set_user_context()` - Set user information
   - `add_breadcrumb()` - Add debugging breadcrumbs
   - And more...

2. **`shared/config.py`** - Updated with Sentry config
   - `SENTRY_DSN` - Sentry project DSN
   - `SENTRY_ENVIRONMENT` - Environment name
   - `SENTRY_TRACES_SAMPLE_RATE` - Performance monitoring sample rate

3. **`.env.example`** - Updated with Sentry variables
   - Template for environment configuration

4. **`shared/utils/sentry_example.py`** - Complete examples
   - Shows all features with working code
   - Copy-paste ready examples

5. **`docs/SENTRY_INTEGRATION.md`** - Full documentation
   - Detailed usage guide
   - Best practices
   - Troubleshooting

## Quick Examples

### Basic Error Capture
```python
from shared.utils.sentry import capture_exception

try:
    risky_operation()
except Exception as e:
    capture_exception(e, tags={"feature": "payment"})
    raise
```

### Decorator-Based Capture
```python
from shared.utils.sentry import capture_exception_decorator

@capture_exception_decorator(tags={"endpoint": "checkout"})
async def process_checkout(order_id: str):
    # Errors automatically captured
    process_payment(order_id)
```

### Performance Tracing
```python
from shared.utils.sentry import trace_function

@trace_function(operation="db.query")
async def fetch_products():
    return await db.query(Product).all()
```

### User Context
```python
from shared.utils.sentry import set_user_context

set_user_context(
    user_id="123",
    username="john_doe",
    email="john@example.com"
)
```

### Breadcrumbs
```python
from shared.utils.sentry import add_breadcrumb

add_breadcrumb(
    message="User started checkout",
    category="user_action",
    level="info"
)
```

## Integration Checklist

- [ ] Install `sentry-sdk[fastapi]` package
- [ ] Get Sentry DSN from sentry.io
- [ ] Add `SENTRY_DSN` to `.env` file
- [ ] Add `init_sentry()` to your service startup
- [ ] Test with `/test-sentry` endpoint
- [ ] Verify errors appear in Sentry dashboard
- [ ] Review filtered fields for your use case
- [ ] Set up alerts in Sentry dashboard
- [ ] Configure sample rate for production

## Production Recommendations

### Sample Rate
For high-traffic services, reduce the sample rate:
```bash
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions
```

### Environment
Use appropriate environment names:
```bash
# Development
SENTRY_ENVIRONMENT=development

# Staging
SENTRY_ENVIRONMENT=staging

# Production
SENTRY_ENVIRONMENT=production
```

### Alerts
Set up alerts in Sentry for:
- Error rate spikes
- New errors
- Performance degradation
- Specific error types

## Next Steps

1. Read `docs/SENTRY_INTEGRATION.md` for detailed documentation
2. Check `shared/utils/sentry_example.py` for complete examples
3. Integrate into your critical services first (API Gateway, Core Gateway)
4. Monitor the Sentry dashboard
5. Set up alerts for your team

## Support Resources

- **Full Documentation**: `docs/SENTRY_INTEGRATION.md`
- **Code Examples**: `shared/utils/sentry_example.py`
- **Sentry Docs**: https://docs.sentry.io/platforms/python/guides/fastapi/
- **Python SDK**: https://docs.sentry.io/platforms/python/

## Cost

Sentry offers:
- **Free Tier**: 5,000 errors/month, 10,000 performance units/month
- **Team Plan**: $26/month for 50,000 errors, 100,000 performance units
- **Business Plan**: Custom pricing

Start with the free tier and scale as needed.

---

**Questions?** Check the full documentation in `docs/SENTRY_INTEGRATION.md`
