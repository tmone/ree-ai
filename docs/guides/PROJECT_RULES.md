# PROJECT RULES - QUY ĐỊNH NGHIÊM NGẶT

## 🚨 QUY TẮC BẮT BUỘC - KHÔNG ĐƯỢC VI PHẠM

### 1. ROOT DIRECTORY - CHỈ ĐƯỢC PHÉP 4 FILES

```
ree-ai/
├── README.md              ✅ DUY NHẤT - Main documentation
├── docker-compose.yml     ✅ REQUIRED - Container orchestration
├── requirements.txt       ✅ REQUIRED - Python dependencies
└── Makefile              ✅ OPTIONAL - Build commands
```

**TUYỆT ĐỐI KHÔNG được có:**
- ❌ Bất kỳ file `.md` nào khác (trừ README.md)
- ❌ Bất kỳ file `.txt` nào khác (trừ requirements.txt)
- ❌ File config: `.ini`, `.yaml`, `.json`, `.toml` (phải vào config/)
- ❌ File script: `.sh`, `.bat`, `.ps1` (phải vào tools/ hoặc xóa)
- ❌ File test: `test_*.py`, `*_test.py` (phải vào tests/)
- ❌ File backup: `*_backup`, `*_old`, `*_v2` (XÓA - dùng Git)
- ❌ File tạm: `*.tmp`, `*.log`, `*.bak`

### 2. DOCUMENTATION - CHỈ Ở docs/

```
docs/
├── guides/              # Hướng dẫn sử dụng
├── architecture/        # Kiến trúc hệ thống
├── setup/              # Setup instructions
├── integration/        # Integration guides
├── reference/          # Reference docs
└── executive/          # Executive summaries
```

**QUY TẮC:**
- ✅ TẤT CẢ file `.md` (trừ README.md) PHẢI vào docs/
- ✅ PHẢI phân loại vào subdirectory (guides/, architecture/, etc.)
- ❌ KHÔNG được để file `.md` trực tiếp trong docs/
- ❌ KHÔNG được tạo docs/ ở root level khác

### 3. CONFIGURATION FILES

```
config/                 # Nếu cần config files
├── .env.example       # Template only (actual .env ở root - gitignored)
└── settings/          # Additional configs
```

**QUY TẮC:**
- ✅ Config files phải vào config/ hoặc service folder
- ❌ KHÔNG để config ở root (trừ .env - gitignored)

### 4. SCRIPTS & TOOLS

**KHÔNG có thư mục scripts/ ở root**

Nếu cần automation:
```
tools/                 # Nếu thực sự cần
├── build.sh
└── deploy.sh
```

**HOẶC TỐT HƠN:**
- Dùng `Makefile` cho dev commands
- Dùng `.github/workflows/` cho CI/CD
- Xóa scripts nếu không dùng

### 5. SOURCE CODE STRUCTURE

```
ree-ai/
├── core/              # Core infrastructure
├── shared/            # Shared utilities
├── services/          # Microservices
│   └── service_name/
│       ├── main.py    ✅ DUY NHẤT - NO main_v2.py!
│       ├── Dockerfile
│       └── requirements.txt (optional)
└── tests/             # All tests
    ├── pytest.ini
    ├── conftest.py
    └── docker-compose.test.yml
```

**QUY TẮC:**
- ✅ Mỗi service CHỈ có DUY NHẤT `main.py`
- ❌ KHÔNG có `main_v2.py`, `main_old.py`, `main_backup.py`
- ❌ Dùng Git branches thay vì versioned files
- ✅ Test configs (pytest.ini, docker-compose.test.yml) vào tests/

### 6. VERSION CONTROL - GIT LÀ VERSION CONTROL

**KHÔNG BAO GIỜ tạo:**
- ❌ `file_v2.py`
- ❌ `file_old.py`
- ❌ `file_backup.py`
- ❌ `file.bak`

**THAY VÀO ĐÓ:**
```bash
# Tạo branch mới
git checkout -b feature/improvement

# Edit file trực tiếp
vim main.py

# Test
pytest

# Commit
git add main.py
git commit -m "refactor: improve main.py"

# Merge hoặc discard
git checkout main
git merge feature/improvement
# HOẶC
git branch -D feature/improvement  # Discard
```

### 7. FILE NAMING CONVENTIONS

**Python files:**
- `snake_case.py` - Code files
- `test_feature.py` - Test files

**Documentation:**
- `lowercase-with-dashes.md` - Trong docs/
- `README.md` - UPPERCASE chỉ ở root

**Configs:**
- `lowercase.yml`, `lowercase.json`, `lowercase.ini`

**KHÔNG dùng:**
- ❌ `camelCase.py`
- ❌ `PascalCase.md`
- ❌ `UPPERCASE_FILE.txt` (trừ README)
- ❌ `file name with spaces.md`

## 🛡️ ENFORCEMENT - CÁCH ÁP DỤNG

### .gitignore - Ngăn Chặn Commit File Rác

File `.gitignore` ĐÃ được cập nhật với rules:
```gitignore
# Backup and versioned files
*_v2.py
*_old.py
*_backup.py
*.bak
*.tmp

# Documentation duplicates
*SUMMARY*.md
*COMPLETE*.md
*BACKUP*.md
```

### Pre-commit Check (Tùy chọn)

Tạo `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check root directory only has allowed files

ALLOWED_FILES=("README.md" "docker-compose.yml" "requirements.txt" "Makefile" ".gitignore" ".env" ".env.example")
ROOT_FILES=$(find . -maxdepth 1 -type f ! -name ".*" -exec basename {} \;)

for file in $ROOT_FILES; do
    if [[ ! " ${ALLOWED_FILES[@]} " =~ " ${file} " ]]; then
        echo "❌ ERROR: Unauthorized file in root: $file"
        echo "   Files in root must be: ${ALLOWED_FILES[@]}"
        exit 1
    fi
done

echo "✅ Root directory is clean"
```

## 📋 CHECKLIST - Trước Khi Commit

```
[ ] Root directory chỉ có: README.md, docker-compose.yml, requirements.txt, Makefile
[ ] Không có file .md khác ở root
[ ] Không có file _v2, _old, _backup
[ ] Tất cả docs ở docs/ và được phân loại
[ ] Test configs ở tests/
[ ] Không có scripts/ ở root (hoặc chuyển sang tools/)
[ ] Mỗi service chỉ có 1 main.py
```

## 🎯 WHEN IN DOUBT - KHI NGHI NGỜ

**Hỏi bản thân 3 câu:**

1. **File này có PHẢI ở root không?**
   - Nếu không phải README.md, docker-compose.yml, requirements.txt, Makefile → KHÔNG

2. **File này có phải là versioned copy không?**
   - Nếu có `_v2`, `_old`, `_backup` → XÓA, dùng Git

3. **File này có tạm thời không?**
   - Nếu `.tmp`, `.log`, `.bak`, notes, summary → XÓA hoặc vào docs/

## 🚫 EXAMPLES - VIOLATIONS

**❌ SAI:**
```
ree-ai/
├── README.md
├── CLAUDE.md                    ❌ Phải vào docs/guides/
├── PROJECT_STRUCTURE.md         ❌ Phải vào docs/guides/
├── test.sh                      ❌ Xóa hoặc vào tools/
├── pytest.ini                   ❌ Phải vào tests/
├── services/
│   └── api/
│       ├── main.py
│       └── main_v2.py          ❌ Xóa, dùng Git
```

**✅ ĐÚNG:**
```
ree-ai/
├── README.md                    ✅
├── docker-compose.yml           ✅
├── requirements.txt             ✅
├── Makefile                     ✅
├── docs/
│   └── guides/
│       ├── claude.md
│       └── project-structure.md
├── tests/
│   ├── pytest.ini
│   └── docker-compose.test.yml
└── services/
    └── api/
        └── main.py              ✅ Duy nhất
```

## 📞 ESCALATION - KHI VI PHẠM

Nếu thấy vi phạm:
1. **Stop immediately** - Dừng commit
2. **Clean up** - Di chuyển/xóa file vi phạm
3. **Update .gitignore** - Thêm pattern nếu cần
4. **Document** - Cập nhật rules này nếu cần

---

**Remember: ROOT IS SACRED - Keep it minimal and clean!**

Last updated: 2025-10-30
