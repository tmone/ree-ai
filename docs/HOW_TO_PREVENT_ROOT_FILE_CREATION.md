# How to Prevent Claude Code from Creating Files in Root Directory

**Problem:** Claude Code sometimes creates files in root directory instead of proper subdirectories.

**Solution:** Multiple layers of protection implemented.

---

## ✅ Protections Implemented

### 1. Updated CLAUDE.md with RULE #0

**File:** `CLAUDE.md`

Added **RULE #0** at the very top of CRITICAL RULES:

```markdown
### ⛔ RULE #0: NEVER CREATE FILES IN ROOT DIRECTORY WITHOUT EXPLICIT USER PERMISSION

**ROOT DIRECTORY IS RESTRICTED - ASK FIRST!**

**FORBIDDEN in root directory:**
- ❌ Test files (→ use `tests/`)
- ❌ Documentation files (→ use `docs/` or `docs/claude/`)
- ❌ Temporary files (→ use `tests/results/` or `temp/`)
- ❌ Scripts (→ use `scripts/` or `tools/`)
- ❌ Any `.md`, `.txt`, `.json`, `.py`, `.sh`, `.bat` files

**ALLOWED in root directory (ONLY these):**
- ✅ `README.md` (project overview)
- ✅ `CLAUDE.md` (this file)
- ✅ `.env.example`, `.gitignore`, `docker-compose.yml`
- ✅ `requirements.txt`, `package.json`
- ✅ Config files that MUST be in root

**BEFORE creating ANY file, you MUST:**
1. ✅ Check if it belongs in a subdirectory (99% do!)
2. ✅ If unsure, ASK USER: "Should this go in `tests/`, `docs/`, or root?"
3. ✅ NEVER assume root is correct
```

### 2. Created .clauderules File

**File:** `.clauderules`

Explicit rules file that Claude Code reads automatically:
- Lists forbidden file types in root
- Specifies required directory structure
- Forces asking user before creating files

### 3. Organized Deployment Files

**Moved all deployment files to proper directories:**

Before (❌ Wrong):
```
/DEPLOYMENT_TO_DEV.md
/DEPLOYMENT_SUCCESS_REPORT.md
/FINAL_SUMMARY.md
/deploy-to-dev.sh
/deploy-to-dev.bat
```

After (✅ Correct):
```
/docs/deployment/DEPLOYMENT_TO_DEV.md
/docs/deployment/DEPLOYMENT_SUCCESS_REPORT.md
/docs/deployment/FINAL_SUMMARY.md
/scripts/deploy-to-dev.sh
/scripts/deploy-to-dev.bat
```

---

## 📁 Correct Directory Structure

```
ree-ai/
├── README.md                    ✅ Root (allowed)
├── CLAUDE.md                    ✅ Root (allowed)
├── .clauderules                 ✅ Root (config)
├── docker-compose.yml           ✅ Root (required)
├── .env.example                 ✅ Root (required)
├── .gitignore                   ✅ Root (required)
│
├── docs/                        ✅ Documentation
│   ├── deployment/              → Deployment guides
│   │   ├── DEPLOYMENT_TO_DEV.md
│   │   ├── DEPLOYMENT_SUCCESS_REPORT.md
│   │   └── FINAL_SUMMARY.md
│   └── claude/                  → Claude-specific docs
│
├── tests/                       ✅ All test files
│   ├── test_*.py
│   ├── verify_*.py
│   └── results/                 → Test results
│
├── scripts/                     ✅ Scripts
│   ├── deploy-to-dev.sh
│   └── deploy-to-dev.bat
│
├── services/                    ✅ Service code
├── shared/                      ✅ Shared utilities
└── tools/                       ✅ Development tools
```

---

## 🛡️ How It Works

### When Claude Code Starts a Task:

1. **Reads `CLAUDE.md`** → Sees RULE #0 at the top
2. **Reads `.clauderules`** → Understands forbidden patterns
3. **Before creating files** → Checks directory rules
4. **If unsure** → MUST ask user

### Example Interaction:

**Before (❌ Bad):**
```
Claude: *Creates test_something.py in root*
```

**After (✅ Good):**
```
Claude: "I need to create a test file. Should this go in `tests/` directory?"
User: "Yes, use tests/"
Claude: *Creates tests/test_something.py*
```

---

## 📋 File Type → Directory Mapping

| File Type | Correct Directory | Examples |
|-----------|------------------|----------|
| `test_*.py` | `tests/` | `test_hallucination.py` |
| `*_REPORT.md` | `docs/` or `docs/deployment/` | `DEPLOYMENT_REPORT.md` |
| `*_GUIDE.md` | `docs/` or `docs/deployment/` | `DEPLOYMENT_GUIDE.md` |
| `deploy_*.sh` | `scripts/` | `deploy-to-dev.sh` |
| `verify_*.py` | `tests/` | `verify_deployment.py` |
| Documentation `.md` | `docs/` | Any markdown docs |
| Utility scripts | `scripts/` or `tools/` | Helper scripts |
| Test results | `tests/results/` | Output files |

---

## 🔧 Enforcing Rules

### Option 1: Use .gitignore (Recommended)

Add to `.gitignore`:
```gitignore
# Prevent accidental root files (except allowed ones)
/*.md
!README.md
!CLAUDE.md
/*.txt
/*.py
/*.sh
/*.bat
/*_REPORT.md
/*_GUIDE.md
```

**Benefit:** Git will warn if you try to commit disallowed files

### Option 2: Pre-commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check for disallowed files in root
forbidden_files=$(git diff --cached --name-only | grep -E '^[^/]+\.(md|txt|py|sh|bat)$' | grep -v -E '^(README|CLAUDE)\.md$')

if [ -n "$forbidden_files" ]; then
    echo "ERROR: Files not allowed in root directory:"
    echo "$forbidden_files"
    echo "Please move to proper subdirectory (tests/, docs/, scripts/)"
    exit 1
fi
```

### Option 3: Manual Review

Before committing, always check:
```bash
git status
# Look for unexpected files in root
```

---

## ✅ Testing the Rules

### Test 1: Ask Claude to Create a Test File

**User:** "Create a test for the search feature"

**Expected Behavior:**
- ✅ Claude creates `tests/test_search_feature.py`
- ❌ NOT `test_search_feature.py` in root

### Test 2: Ask Claude to Create Documentation

**User:** "Write deployment documentation"

**Expected Behavior:**
- ✅ Claude asks: "Should I create this in `docs/deployment/`?"
- ✅ After confirmation, creates `docs/deployment/DEPLOYMENT_GUIDE.md`
- ❌ NOT `DEPLOYMENT_GUIDE.md` in root

### Test 3: Ask Claude to Create a Script

**User:** "Create a deployment script"

**Expected Behavior:**
- ✅ Claude creates `scripts/deploy.sh`
- ❌ NOT `deploy.sh` in root

---

## 🎓 Training Claude Code

If Claude Code still creates files in root:

1. **Remind explicitly:**
   ```
   "Please follow RULE #0 in CLAUDE.md - do not create files in root directory"
   ```

2. **Point to rules:**
   ```
   "Check .clauderules - this file should go in tests/"
   ```

3. **Move manually and correct:**
   ```bash
   mv wrong_file.py tests/
   git add tests/wrong_file.py
   ```
   Then tell Claude: "I moved it to tests/ - please use that directory next time"

---

## 📊 Current Status

**Files in Root (Allowed):** ✅
- `README.md`
- `CLAUDE.md`
- `.clauderules`
- `docker-compose.yml`
- `.env.example`
- `.gitignore`
- `requirements.txt`

**Files Moved to Correct Directories:** ✅
- All deployment docs → `docs/deployment/`
- All scripts → `scripts/`
- All tests → `tests/`

**Protection Mechanisms:** ✅
- RULE #0 in `CLAUDE.md`
- `.clauderules` file
- Directory structure documented
- This guide created

---

## 🔍 Monitoring

**Check root directory regularly:**
```bash
# List all files in root (excluding directories)
ls -la | grep -v '^d' | grep -v '^total'

# Should only see allowed files
```

**Clean up if needed:**
```bash
# Move misplaced test files
mv test_*.py tests/

# Move deployment docs
mv *_GUIDE.md *_REPORT.md docs/deployment/

# Move scripts
mv *.sh *.bat scripts/
```

---

## ✅ Success Criteria

Claude Code file creation is considered "correct" when:

1. ✅ No unexpected `.md` files in root
2. ✅ All test files in `tests/`
3. ✅ All docs in `docs/` or `docs/deployment/`
4. ✅ All scripts in `scripts/`
5. ✅ Claude asks before creating files when unsure
6. ✅ Root only contains explicitly allowed files

---

## 📚 References

- `CLAUDE.md` - Project rules for Claude Code
- `.clauderules` - File creation rules
- `docs/claude/01-critical-rules.md` - Detailed file placement guide
- `PROJECT_STRUCTURE.md` - Complete directory structure

---

**Last Updated:** 2025-11-21
**Status:** ✅ Rules implemented and enforced
