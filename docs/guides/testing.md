# 🧪 REE AI - Automated Testing Guide

**Complete testing infrastructure for microservices architecture**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Writing Tests](#writing-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

REE AI has comprehensive automated testing for the microservices architecture:

- **Unit Tests** - Fast, no external dependencies
- **Integration Tests** - Test service interactions
- **End-to-End Tests** - Full workflow validation
- **CI/CD Pipeline** - Automated testing on every commit

### Test Coverage

✅ **Service Registry**
- Service registration/deregistration
- Service discovery by capability
- Health monitoring
- Statistics tracking

✅ **BaseService Auto-Registration**
- Service initialization
- Auto-registration on startup
- Default routes (/, /health, /info)

✅ **Orchestrator**
- Intent detection
- Dynamic service discovery
- Service routing
- Error handling

✅ **End-to-End Workflows**
- Complete request flow
- Multi-service orchestration
- Service lifecycle

---

## 📁 Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures & utilities
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Test dependencies
├── Dockerfile                  # Test runner container
│
├── test_service_registry.py    # Service Registry tests
├── test_base_service.py        # BaseService tests
├── test_orchestrator.py        # Orchestrator tests
└── test_end_to_end.py          # E2E workflow tests
```

### Test Configuration Files

```
docker-compose.test.yml         # Test environment Docker Compose
scripts/
├── run-tests.sh               # Linux/Mac test runner
└── run-tests.bat              # Windows test runner
.github/workflows/ci.yml       # GitHub Actions CI/CD
```

---

## 🚀 Running Tests

### Method 1: Quick Test (Recommended)

**Linux/Mac:**
```bash
chmod +x scripts/run-tests.sh
./scripts/run-tests.sh
```

**Windows:**
```cmd
scripts\run-tests.bat
```

This will:
1. ✅ Start all required services
2. ✅ Wait for services to be healthy
3. ✅ Run all tests
4. ✅ Generate test report
5. ✅ Cleanup automatically

### Method 2: Docker Compose

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be ready (30 seconds)
sleep 30

# Run tests
docker-compose -f docker-compose.test.yml run --rm test-runner

# Cleanup
docker-compose -f docker-compose.test.yml down -v
```

### Method 3: Local Pytest (Development)

**Prerequisites:**
- Services running (via `docker-compose up`)
- Python 3.11+

```bash
# Install dependencies
pip install -r tests/requirements.txt
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_service_registry.py -v

# Run with markers
pytest tests/ -m integration -v
```

---

## 🏷️ Test Categories

Tests are organized with pytest markers:

### Unit Tests (Fast)

```bash
# Run only unit tests (no external dependencies)
pytest tests/ -m unit -v
```

### Integration Tests

```bash
# Run integration tests (requires running services)
pytest tests/ -m integration -v
```

### End-to-End Tests

```bash
# Run E2E tests (full workflows)
pytest tests/ -m e2e -v
```

### Slow Tests

```bash
# Skip slow tests
pytest tests/ -m "not slow" -v
```

---

## 📝 Test Examples

### 1. Service Registry Tests

**File:** `tests/test_service_registry.py`

```python
@pytest.mark.asyncio
async def test_register_service(registry_client, sample_service_data):
    """Test service registration"""
    response = await registry_client.register_service(sample_service_data)

    assert response["status"] == "registered"
    assert response["service"]["name"] == sample_service_data["name"]
```

**What it tests:**
- Service registration endpoint
- Service data validation
- Service appears in registry

### 2. Auto-Registration Tests

**File:** `tests/test_base_service.py`

```python
@pytest.mark.asyncio
async def test_service_auto_registration(registry_client):
    """Test that services automatically register on startup"""
    service_info = await registry_client.get_service("semantic_chunking")

    assert service_info["name"] == "semantic_chunking"
    assert "chunking" in service_info["capabilities"]
```

**What it tests:**
- Services inherit from BaseService correctly
- Auto-registration happens on startup
- Services have correct capabilities

### 3. Orchestrator Discovery Tests

**File:** `tests/test_orchestrator.py`

```python
@pytest.mark.asyncio
async def test_orchestrator_dynamic_discovery(http_client, registry_client):
    """Test dynamic service discovery via Service Registry"""

    # Verify service is registered
    services = await registry_client.list_services(capability="chunking")
    assert services["count"] > 0

    # Send request to Orchestrator
    response = await http_client.post(
        "http://localhost:8090/orchestrate",
        json={"user_id": "test", "query": "Chunk this text"}
    )

    data = response.json()
    assert data["service_used"] == "semantic_chunking"
```

**What it tests:**
- Orchestrator queries Service Registry
- Correct service is discovered
- Request is routed to service
- Response is returned

### 4. End-to-End Tests

**File:** `tests/test_end_to_end.py`

```python
@pytest.mark.asyncio
async def test_complete_chunking_workflow(http_client, registry_client):
    """Test complete workflow from request to response"""

    # Step 1: Verify service registered
    service_info = await registry_client.get_service("semantic_chunking")
    assert service_info["status"] == "healthy"

    # Step 2: Send orchestration request
    response = await http_client.post(
        "http://localhost:8090/orchestrate",
        json={"user_id": "test", "query": "Chunk this text"}
    )

    # Step 3: Verify response
    data = response.json()
    assert data["service_used"] == "semantic_chunking"
    assert data["took_ms"] > 0
```

**What it tests:**
- Complete workflow: Registration → Discovery → Execution → Response
- All services working together
- Realistic user scenarios

---

## ✍️ Writing Tests

### Test Template

```python
import pytest

@pytest.mark.asyncio
async def test_my_feature(registry_client, http_client, cleanup_test_services):
    """Test description here"""

    # Arrange - Setup test data
    test_service = {
        "name": "test_service",
        "host": "test-host",
        "port": 8080,
        "version": "1.0.0",
        "capabilities": ["test"]
    }

    # Act - Perform action
    response = await registry_client.register_service(test_service)
    cleanup_test_services.append(test_service["name"])

    # Assert - Verify result
    assert response["status"] == "registered"

    # Cleanup happens automatically via fixture
```

### Available Fixtures (from `conftest.py`)

**`registry_client`** - Service Registry client
```python
async def test_example(registry_client):
    await registry_client.register_service(data)
    services = await registry_client.list_services()
```

**`http_client`** - General HTTP client
```python
async def test_example(http_client):
    response = await http_client.get("http://localhost:8090/health")
```

**`sample_service_data`** - Sample service registration data
```python
def test_example(sample_service_data):
    assert sample_service_data["name"] == "test_service"
```

**`cleanup_test_services`** - Auto-cleanup for test services
```python
async def test_example(registry_client, cleanup_test_services):
    await registry_client.register_service(data)
    cleanup_test_services.append("test_service")
    # Automatic cleanup on test end
```

---

## 🔄 CI/CD Integration

### GitHub Actions Workflow

**File:** `.github/workflows/ci.yml`

Automated on every push/PR:

1. **Unit Tests** (10 min)
   - Fast tests, no Docker
   - Python 3.11 environment

2. **Integration Tests** (30 min)
   - Start all services
   - Test service interactions
   - Upload test results

3. **End-to-End Tests** (45 min)
   - Full workflow validation
   - Complete system test

4. **Build Check** (20 min)
   - Ensure all services build
   - Docker image validation

### CI/CD Pipeline Flow

```
Push/PR → GitHub Actions
    ↓
Unit Tests (parallel)
    ↓
Integration Tests (parallel)
    ↓
E2E Tests
    ↓
Build Check
    ↓
✅ All Pass → Merge allowed
❌ Any Fail → Blocks merge
```

### Viewing CI Results

1. Go to GitHub repository
2. Click **Actions** tab
3. Select workflow run
4. View test results and logs

---

## 🧐 Test Results

### Test Output Format

```
============================== test session starts ==============================
tests/test_service_registry.py::test_service_registry_health PASSED       [ 10%]
tests/test_service_registry.py::test_register_service PASSED              [ 20%]
tests/test_base_service.py::test_service_auto_registration PASSED         [ 30%]
tests/test_orchestrator.py::test_orchestrator_dynamic_discovery PASSED    [ 40%]
tests/test_end_to_end.py::test_complete_chunking_workflow PASSED          [ 50%]

============================== 5 passed in 12.34s ===============================
```

### JUnit XML Report

Generated at: `test-results/junit.xml`

Can be imported into:
- Jenkins
- GitLab CI
- Azure DevOps
- Any CI/CD tool supporting JUnit format

---

## 🐛 Troubleshooting

### Tests Fail: "Service Registry not healthy"

**Problem:** Service Registry didn't start or is unhealthy

**Solution:**
```bash
# Check Service Registry logs
docker-compose -f docker-compose.test.yml logs service-registry

# Restart Service Registry
docker-compose -f docker-compose.test.yml restart service-registry

# Wait longer for startup
sleep 30
```

### Tests Fail: "Service not found"

**Problem:** Service didn't register with Service Registry

**Solution:**
```bash
# Check service logs
docker-compose -f docker-compose.test.yml logs semantic-chunking

# Check Service Registry
curl http://localhost:8000/services

# Verify service health
curl http://localhost:8082/health
```

### Tests Timeout

**Problem:** Service takes too long to respond

**Solution:**
1. Increase timeout in `pytest.ini`:
   ```ini
   timeout = 60  # Increase from 30 to 60
   ```

2. Check if Ollama is running (some tests need LLM):
   ```bash
   docker-compose -f docker-compose.test.yml logs ollama
   ```

### Port Conflicts

**Problem:** Ports already in use

**Solution:**
```bash
# Check what's using the port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Stop conflicting services
docker-compose down
docker-compose -f docker-compose.test.yml down
```

### Docker Cleanup

**Problem:** Old test containers interfering

**Solution:**
```bash
# Full cleanup
docker-compose -f docker-compose.test.yml down -v
docker system prune -f

# Remove test volumes
docker volume prune -f
```

---

## 📊 Test Metrics

### Expected Test Counts

- **Service Registry Tests:** 8 tests
- **BaseService Tests:** 3 tests
- **Orchestrator Tests:** 5 tests
- **End-to-End Tests:** 4 tests

**Total:** ~20 tests

### Expected Timing

- **Unit Tests:** < 5 seconds
- **Integration Tests:** 1-2 minutes
- **E2E Tests:** 2-5 minutes
- **Full Suite:** 5-10 minutes

---

## 🎯 Best Practices

### 1. Test Isolation

Each test should be independent:
```python
# ✅ GOOD - Uses cleanup fixture
async def test_register(registry_client, cleanup_test_services):
    await registry_client.register_service(data)
    cleanup_test_services.append("test_service")

# ❌ BAD - Leaves test data behind
async def test_register(registry_client):
    await registry_client.register_service(data)
    # No cleanup!
```

### 2. Descriptive Test Names

```python
# ✅ GOOD
async def test_orchestrator_routes_to_chunking_service_when_chunking_capability_requested()

# ❌ BAD
async def test_orchestrator()
```

### 3. Arrange-Act-Assert Pattern

```python
async def test_example():
    # Arrange - Setup
    data = {"name": "test"}

    # Act - Execute
    result = await function(data)

    # Assert - Verify
    assert result["status"] == "success"
```

### 4. Use Markers

```python
@pytest.mark.integration  # Requires running services
@pytest.mark.slow        # Takes > 5 seconds
@pytest.mark.asyncio     # Async test
async def test_slow_integration():
    pass
```

---

## 📚 Additional Resources

- **Pytest Documentation:** https://docs.pytest.org/
- **pytest-asyncio:** https://pytest-asyncio.readthedocs.io/
- **Docker Compose Testing:** https://docs.docker.com/compose/
- **GitHub Actions:** https://docs.github.com/actions

---

## ✅ Quick Reference

### Run All Tests
```bash
./scripts/run-tests.sh              # Linux/Mac
scripts\run-tests.bat               # Windows
```

### Run Specific Tests
```bash
pytest tests/test_service_registry.py -v
pytest tests/ -k "test_register" -v
pytest tests/ -m integration -v
```

### Debug Tests
```bash
pytest tests/ -v --tb=long -s      # Show print statements
pytest tests/ --pdb                # Drop to debugger on failure
```

### Check Test Coverage
```bash
pip install pytest-cov
pytest tests/ --cov=core --cov=services --cov-report=html
# Open htmlcov/index.html
```

---

**Status:** ✅ Complete Testing Infrastructure
**Coverage:** Service Registry, BaseService, Orchestrator, E2E
**CI/CD:** GitHub Actions integrated
**Documentation:** Complete

🧪 **Happy Testing!**
