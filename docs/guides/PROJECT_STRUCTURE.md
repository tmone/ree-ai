# REE AI - Project Structure & File Organization Rules

## 📁 Quy Định Về Cấu Trúc Thư Mục

### 1. Root Directory (/)
**Chỉ chứa:**
- `README.md` - Tài liệu chính của project
- `CLAUDE.md` - Hướng dẫn cho Claude Code
- `PROJECT_STRUCTURE.md` - File này (quy định cấu trúc)
- `.env.example` - Environment template
- `.gitignore` - Git ignore rules
- `docker-compose.yml` - Main orchestration
- `docker-compose.test.yml` - Test environment
- `requirements.txt` - Python dependencies

**KHÔNG được chứa:**
- ❌ Các file BACKUP, SUMMARY, COMPLETE
- ❌ Các file documentation trùng lặp
- ❌ Các file tạm thời hoặc versioned (_v2.py, _old.py)

### 2. /docs - Tài Liệu Chuyên Sâu
**Mục đích:** Chứa tất cả tài liệu kỹ thuật, hướng dẫn, và documentation

**Cấu trúc:**
```
docs/
├── architecture/           # Kiến trúc hệ thống
│   ├── system-design.md
│   └── service-mapping.md
├── guides/                 # Hướng dẫn sử dụng
│   ├── quickstart.md
│   ├── deployment.md
│   └── testing.md
├── team/                   # Tài liệu cho team
│   ├── collaboration-guide.md
│   └── development-workflow.md
└── api/                    # API documentation
    └── service-contracts.md
```

**Quy tắc:**
- ✅ Mỗi file phải có mục đích rõ ràng
- ✅ Đặt tên file theo format: `lowercase-with-dashes.md`
- ❌ KHÔNG tạo file backup trong docs/
- ❌ KHÔNG có file trùng tên với root directory

### 3. /core - Infrastructure Code
**Mục đích:** Shared infrastructure cho tất cả services

```
core/
├── __init__.py
├── base_service.py         # BaseService class (inheritance)
└── service_registry.py     # Service registry models
```

**Quy tắc:**
- ✅ Chỉ chứa code dùng chung cho ALL services
- ✅ Mọi service PHẢI inherit từ BaseService
- ❌ KHÔNG thêm business logic vào đây
- ❌ KHÔNG tạo file _v2.py hoặc _old.py

### 4. /shared - Shared Models & Utilities
**Mục đích:** Code và models dùng chung giữa các services

```
shared/
├── __init__.py
├── config.py               # Settings và feature flags
├── models/                 # Pydantic models (API contracts)
│   ├── __init__.py
│   ├── core_gateway.py    # LLM models
│   ├── db_gateway.py      # Database models
│   └── orchestrator.py    # Orchestration models
└── utils/                  # Shared utilities
    ├── __init__.py
    ├── logger.py          # Logging setup
    ├── cache.py           # Redis caching
    ├── metrics.py         # Prometheus metrics
    └── sentry.py          # Error tracking
```

**Quy tắc:**
- ✅ Models PHẢI là Pydantic models
- ✅ Một model cho một service contract
- ✅ Utils phải generic, không specific cho service nào
- ❌ KHÔNG thêm business logic vào models
- ❌ KHÔNG tạo file example hoặc demo ở đây

### 5. /services - Microservices
**Mục đích:** Mỗi service là một microservice độc lập

**Cấu trúc chuẩn cho mỗi service:**
```
services/
├── service_name/
│   ├── __init__.py
│   ├── main.py             # Entry point (ONLY ONE VERSION)
│   ├── Dockerfile          # Container definition
│   ├── requirements.txt    # Service-specific deps (optional)
│   └── README.md           # Service documentation (optional)
```

**Quy tắc QUAN TRỌNG:**
- ✅ Mỗi service CHỈ có DUY NHẤT một file `main.py`
- ✅ Service PHẢI inherit từ `BaseService`
- ✅ Service PHẢI có Dockerfile
- ❌ KHÔNG tạo `main_v2.py`, `main_old.py`, `main_backup.py`
- ❌ KHÔNG lưu code cũ - dùng Git để version control
- ❌ KHÔNG thêm test files trong service folder

**Khi cần thử nghiệm version mới:**
1. Tạo Git branch mới: `git checkout -b feature/service-v2`
2. Edit `main.py` trực tiếp
3. Test trên branch
4. Merge hoặc discard branch

### 6. /tests - Test Suite
**Mục đích:** Tất cả automated tests

```
tests/
├── __init__.py
├── conftest.py             # Pytest fixtures
├── pytest.ini              # Pytest config
├── requirements.txt        # Test dependencies
├── Dockerfile              # Test runner
├── unit/                   # Unit tests (nhanh, không cần external deps)
│   └── test_*.py
├── integration/            # Integration tests (cần services chạy)
│   └── test_*.py
└── e2e/                    # End-to-end tests
    └── test_*.py
```

**Quy tắc:**
- ✅ Test files PHẢI bắt đầu với `test_`
- ✅ Một test file cho một service/component
- ✅ Sử dụng fixtures từ conftest.py
- ❌ KHÔNG commit test results (junit.xml, coverage.xml)
- ❌ KHÔNG lưu test data trong tests/ (dùng fixtures)

### 7. /scripts - Automation Scripts
**Mục đích:** Scripts cho automation và DevOps

```
scripts/
├── run-tests.sh            # Test runner (Linux/Mac)
├── run-tests.bat           # Test runner (Windows)
├── deploy.sh               # Deployment script
└── setup-dev.sh            # Dev environment setup
```

**Quy tắc:**
- ✅ Scripts phải executable và có shebang
- ✅ Scripts phải có error handling
- ✅ Đặt tên theo format: `action-target.sh`
- ❌ KHÔNG commit backup scripts
- ❌ KHÔNG commit .env files (chỉ .env.example)

### 8. /k8s - Kubernetes Configs
**Mục đích:** Kubernetes deployment configs

```
k8s/
├── base/                   # Base configs
│   ├── namespace.yaml
│   ├── configmap.yaml
│   └── *.yaml
└── overlays/               # Environment-specific
    ├── dev/
    ├── staging/
    └── production/
```

**Quy tắc:**
- ✅ Sử dụng Kustomize cho overlays
- ✅ Secrets KHÔNG được commit
- ❌ KHÔNG hardcode values - dùng ConfigMap

### 9. /monitoring - Monitoring & Observability
**Mục đích:** Prometheus, Grafana configs

```
monitoring/
├── prometheus/
│   └── prometheus.yml
├── grafana/
│   ├── dashboards/
│   └── provisioning/
└── docker-compose.monitoring.yml
```

**Quy tắc:**
- ✅ Dashboards export as JSON
- ❌ KHÔNG commit data folders

### 10. /mocks - Mock Services
**Mục đích:** Mock data cho development

```
mocks/
├── core_gateway_mock.json
└── db_gateway_mock.json
```

**Quy tắc:**
- ✅ Chỉ chứa JSON mock data
- ✅ Format theo API contract từ shared/models
- ❌ KHÔNG commit sensitive data

## 🚫 File KHÔNG Được Phép

### Tuyệt Đối KHÔNG Commit:
- ❌ `*_v2.py`, `*_old.py`, `*_backup.py` - Dùng Git thay vì versioning files
- ❌ `*BACKUP*.md`, `*backup*.md` - Dùng Git history
- ❌ `*SUMMARY*.md`, `*COMPLETE*.md` - Tài liệu trùng lặp
- ❌ `.env` - Sensitive data
- ❌ `*.log` - Log files
- ❌ `__pycache__/`, `*.pyc` - Python cache
- ❌ `.DS_Store`, `Thumbs.db` - OS files
- ❌ `node_modules/`, `venv/` - Dependencies

### Cách Xóa File Đã Commit Nhầm:
```bash
# Xóa file khỏi Git nhưng giữ local
git rm --cached filename

# Xóa cả local
git rm filename

# Commit
git commit -m "Remove unnecessary files"
```

## 📝 Naming Conventions

### Python Files
- **Services:** `main.py` (ONLY ONE per service)
- **Utilities:** `snake_case.py` (e.g., `logger.py`, `cache_manager.py`)
- **Tests:** `test_feature_name.py`

### Markdown Files
- **Root docs:** `UPPERCASE.md` (README.md, CLAUDE.md)
- **Nested docs:** `lowercase-with-dashes.md`

### Docker
- **Compose files:** `docker-compose.{purpose}.yml`
- **Dockerfiles:** `Dockerfile` (in service folder)

### Environment Files
- **Template:** `.env.example` (commit this)
- **Actual:** `.env` (DO NOT commit)

## 🔄 Workflow: Khi Cần Refactor/Update Code

### ❌ CÁCH SAI:
```bash
# Tạo file mới với version
cp main.py main_v2.py
# Edit main_v2.py
# Giữ cả 2 files
```

### ✅ CÁCH ĐÚNG:
```bash
# Tạo branch mới
git checkout -b feature/refactor-main

# Edit main.py trực tiếp
vim main.py

# Test
pytest tests/

# Commit
git add main.py
git commit -m "Refactor: improve main.py logic"

# Merge hoặc discard
git checkout main
git merge feature/refactor-main
# hoặc
git branch -D feature/refactor-main  # Discard if not needed
```

## 🧹 Cleanup Commands

### Tìm và xóa file không cần thiết:
```bash
# Tìm file backup
find . -name "*_v2.py" -o -name "*_old.py" -o -name "*BACKUP*"

# Xóa (KIỂM TRA KỸ trước khi chạy)
find . -name "*_v2.py" -type f -delete
find . -name "*_old.py" -type f -delete

# Tìm markdown duplicates
find . -name "*SUMMARY*.md" -o -name "*COMPLETE*.md"

# Cleanup Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## 📋 Code Review Checklist

Trước khi commit, PHẢI kiểm tra:
- [ ] Không có file `_v2`, `_old`, `_backup`
- [ ] Không có file backup trong docs/
- [ ] Không commit `.env`
- [ ] Không commit logs hoặc test results
- [ ] Code đã format (black, isort)
- [ ] Tests pass
- [ ] Documentation updated nếu cần

## 🎯 Best Practices Summary

### DO ✅
- Dùng Git branches cho experiments
- Commit often với meaningful messages
- Một file `main.py` duy nhất per service
- Documentation trong `docs/` hoặc service `README.md`
- Sử dụng `.gitignore` hiệu quả

### DON'T ❌
- Tạo versioned files (`_v2`, `_old`)
- Commit sensitive data
- Commit generated files
- Duplicate documentation
- Keep dead code "just in case"

## 📞 Questions?

Nếu không chắc file nên đặt ở đâu:
1. Đọc lại document này
2. Xem examples trong codebase
3. Hỏi team lead
4. Khi nghi ngờ → đừng commit file rác

---

**Remember:** Git is your version control. You don't need `file_v2.py` when you have Git history!
