# REE AI Frontend Build Guide

Complete guide to building and customizing the REE AI frontend based on Open WebUI.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Build Methods](#build-methods)
5. [Custom Components](#custom-components)
6. [API Integration](#api-integration)
7. [Development Workflow](#development-workflow)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The REE AI frontend is a customized version of [Open WebUI](https://github.com/open-webui/open-webui), enhanced with real estate-specific features:

- **Property Search & Display** - Semantic search with filters
- **AI-Powered Chat** - Connected to REE AI Orchestrator
- **Property Cards** - Beautiful property listing components
- **Vietnamese Support** - Full localization for Vietnamese market

### Architecture

```
┌─────────────────────────────────────┐
│   Open WebUI Frontend (SvelteKit)  │
│   - Custom Property Components      │
│   - REE AI API Clients              │
│   - Vietnamese Localization         │
└──────────────────┬──────────────────┘
                   │
                   ↓
┌─────────────────────────────────────┐
│   Orchestrator (Port 8090)          │
│   - Intent Detection                │
│   - Service Routing                 │
└──────────────────┬──────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
┌───────────────┐    ┌────────────────┐
│ RAG Service   │    │ DB Gateway     │
│ (Port 8091)   │    │ (Port 8081)    │
└───────────────┘    └────────────────┘
```

---

## Prerequisites

### For Docker Build (Recommended)

- **Docker Desktop** or **Docker Engine** 20.10+
- **Docker Compose** 2.0+
- 8GB RAM minimum, 16GB recommended
- 20GB free disk space

### For Local Development

- **Node.js** 18+ (LTS recommended)
- **npm** or **pnpm**
- All Docker requirements above
- REE AI backend services running

---

## Quick Start

### Method 1: Build with Docker (Production)

```bash
# From project root
./scripts/build-frontend.sh

# Or on Windows
scripts\build-frontend.bat
```

This will:
1. Build the Docker image with custom frontend
2. Package both frontend (SvelteKit) and backend (Python)
3. Create optimized production build

**Start the frontend:**
```bash
docker compose --profile real up -d open-webui
```

**Access at:** http://localhost:3000

### Method 2: Local Development

```bash
# Build locally
./scripts/build-frontend.sh --local

# Or manually
cd frontend/open-webui
npm ci --force
npm run dev
```

**Access at:** http://localhost:5173 (Vite dev server)

---

## Build Methods

### Docker Build (Production)

**Full Stack Build:**
```bash
# Build frontend + all backend services
docker compose --profile real build

# Build only frontend
docker compose build open-webui
```

**Configuration:**

The Docker build uses:
- **Node.js 22 Alpine** for frontend build (SvelteKit + Vite)
- **Python 3.11 Slim** for backend runtime
- Multi-stage build to minimize image size
- Optimized caching for faster rebuilds

**Build Args:**

```bash
# Build with CUDA support (for GPU acceleration)
docker compose build --build-arg USE_CUDA=true open-webui

# Use slim build (no embedding models)
docker compose build --build-arg USE_SLIM=true open-webui

# Custom embedding model
docker compose build --build-arg USE_EMBEDDING_MODEL=intfloat/multilingual-e5-base open-webui
```

**Environment Variables:**

Set in `docker-compose.yml` or `.env`:

```env
# Open WebUI Configuration
WEBUI_NAME=REE AI - Real Estate Assistant
WEBUI_SECRET_KEY=your-secret-key-change-me

# Backend Integration
OPENAI_API_BASE_URL=http://orchestrator:8080
OPENAI_API_KEY=dummy-key-not-needed

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/ree_ai

# Features
ENABLE_OLLAMA_API=false
ENABLE_OPENAI_API=true
```

### Local Development Build

**Install Dependencies:**
```bash
cd frontend/open-webui
npm ci --force  # or: pnpm install
```

**Development Server:**
```bash
npm run dev              # Start on default port (5173)
npm run dev:5050         # Start on port 5050
```

**Production Build:**
```bash
npm run build            # Build to ./build directory
npm run preview          # Preview production build
```

**Watch Mode:**
```bash
npm run build:watch      # Auto-rebuild on changes
```

---

## Custom Components

### REE AI Custom Components

Located in `frontend/open-webui/src/lib/`:

#### 1. API Clients (`apis/ree-ai/`)

**Orchestrator Client** (`orchestrator.ts`):
```typescript
import { sendOrchestratorQuery } from '$lib/apis/ree-ai';

const response = await sendOrchestratorQuery(token, {
  query: "Tìm căn hộ 2 phòng ngủ ở Quận 1",
  user_id: "user123"
});
// Returns: { intent, response, service_used, confidence }
```

**Storage Client** (`storage.ts`):
```typescript
import { searchProperties } from '$lib/apis/ree-ai';

const results = await searchProperties(token, {
  query: "căn hộ cao cấp",
  filters: {
    property_type: ["apartment"],
    min_price: 2000000000,
    max_price: 5000000000
  },
  limit: 20
});
```

**Classification Client** (`classification.ts`):
```typescript
import { classifyProperty } from '$lib/apis/ree-ai';

const classification = await classifyProperty(token, {
  text: "Bán nhà 3 tầng 100m2 giá 5 tỷ",
  options: { extract_attributes: true }
});
// Returns: { property_type, confidence, attributes }
```

**RAG Client** (`rag.ts`):
```typescript
import { queryRAG } from '$lib/apis/ree-ai';

const answer = await queryRAG(token, {
  query: "Tư vấn về thị trường BDS quận 1",
  top_k: 5
});
// Returns: { answer, sources, context_used }
```

#### 2. Property Components (`components/property/`)

**PropertyCard** - Display property listing:
```svelte
<script>
  import { PropertyCard } from '$lib/components/property';

  let property = {
    id: "prop-123",
    title: "Căn hộ cao cấp 2PN",
    location: "Quận 1, TP.HCM",
    price: 3500000000,
    area: 75,
    property_type: "apartment",
    images: ["url1.jpg", "url2.jpg"]
  };

  function handleClick(property) {
    console.log("Selected:", property);
  }
</script>

<PropertyCard {property} onClick={handleClick} />
```

**PropertySearch** - Full search interface:
```svelte
<script>
  import { PropertySearch } from '$lib/components/property';

  let token = "user-jwt-token";

  function handlePropertySelect(property) {
    // Show property details
    console.log(property);
  }
</script>

<PropertySearch {token} onPropertySelect={handlePropertySelect} />
```

**PropertyDetails** - Detailed property modal:
```svelte
<script>
  import { PropertyDetails } from '$lib/components/property';

  let showDetails = false;
  let selectedProperty = null;
</script>

{#if showDetails && selectedProperty}
  <PropertyDetails
    property={selectedProperty}
    onClose={() => showDetails = false}
  />
{/if}
```

---

## API Integration

### Backend Proxy Configuration

Open WebUI's backend acts as a proxy to REE AI services. You need to configure routes:

**File:** `frontend/open-webui/backend/open_webui/main.py`

Add REE AI routes:

```python
from fastapi import APIRouter
import httpx

ree_ai_router = APIRouter(prefix="/api/ree-ai")

@ree_ai_router.post("/orchestrator/query")
async def orchestrator_query(request: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://orchestrator:8080/query",
            json=request,
            timeout=30.0
        )
        return response.json()

@ree_ai_router.post("/storage/search")
async def storage_search(request: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://db-gateway:8080/search",
            json=request,
            timeout=30.0
        )
        return response.json()

# Include in main app
app.include_router(ree_ai_router)
```

### CORS Configuration

If running frontend separately from backend:

```python
# backend/open_webui/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Development Workflow

### 1. Setup Development Environment

```bash
# Start backend services
docker compose --profile real up -d postgres redis opensearch
docker compose --profile real up -d service-registry core-gateway db-gateway orchestrator

# Start frontend
cd frontend/open-webui
npm install
npm run dev
```

### 2. Make Changes

**Create new component:**
```bash
# Create file
touch src/lib/components/property/MyNewComponent.svelte

# Import in parent
echo "export { default as MyNewComponent } from './MyNewComponent.svelte';" >> src/lib/components/property/index.ts
```

**Add new API endpoint:**
```typescript
// src/lib/apis/ree-ai/my-service.ts
export const myNewEndpoint = async (token: string, data: any) => {
  const res = await fetch(`${WEBUI_BASE_URL}/api/my-service/endpoint`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
  return await res.json();
};
```

### 3. Test Changes

```bash
# Lint
npm run lint

# Type check
npm run check

# Build test
npm run build
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new property filter component"
git push
```

### 5. Build Production

```bash
# Test production build locally
npm run build
npm run preview

# Or build Docker image
docker compose build open-webui
```

---

## Troubleshooting

### Common Issues

#### 1. Build Fails with "JavaScript heap out of memory"

**Solution:**
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=8192"
npm run build
```

Or in package.json (already configured):
```json
{
  "scripts": {
    "build": "NODE_OPTIONS=\"--max-old-space-size=8192\" vite build"
  }
}
```

#### 2. Docker Build Fails

**Check Docker resources:**
- Go to Docker Desktop → Settings → Resources
- Increase Memory to 8GB minimum
- Increase Disk space to 60GB

**Clear Docker cache:**
```bash
docker builder prune -a
docker compose build --no-cache open-webui
```

#### 3. Port Already in Use

**Find and kill process:**
```bash
# Linux/Mac
lsof -ti:3000 | xargs kill -9

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Change port:**
```bash
# docker-compose.yml
ports:
  - "3001:8080"  # Change 3000 to 3001
```

#### 4. Backend Connection Issues

**Check backend is running:**
```bash
curl http://localhost:8090/health  # Orchestrator
curl http://localhost:8081/health  # DB Gateway
```

**Check CORS:**
- Ensure backend allows frontend origin
- Check browser console for CORS errors

**Fix in backend:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 5. npm ci fails

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install --force
```

#### 6. Hot Reload Not Working

**Solution:**
```bash
# Increase file watchers (Linux)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Or use polling
npm run dev -- --force
```

### Performance Issues

**Slow Build:**
- Use `npm run build:watch` for incremental builds
- Clear `.svelte-kit` cache: `rm -rf .svelte-kit`
- Update dependencies: `npm update`

**Large Bundle Size:**
- Analyze bundle: `npm run build -- --mode analyze`
- Use dynamic imports for large components:
```typescript
const PropertySearch = await import('$lib/components/property/PropertySearch.svelte');
```

---

## Advanced Configuration

### Custom Theme

Edit `src/app.css` or create theme file:

```css
/* Custom REE AI theme */
:root {
  --primary-color: #3b82f6;
  --secondary-color: #10b981;
  --background-color: #f9fafb;
  --text-color: #111827;
}
```

### Environment-Specific Builds

```bash
# Development
npm run dev

# Staging
VITE_API_URL=https://staging-api.ree-ai.com npm run build

# Production
VITE_API_URL=https://api.ree-ai.com npm run build
```

### Build Optimization

```javascript
// svelte.config.js
export default {
  kit: {
    adapter: adapter({
      precompress: true,  // Gzip/Brotli compression
      strict: true
    }),
    prerender: {
      crawl: true,
      entries: ['*']  // Prerender all routes
    }
  }
};
```

---

## Deployment

### Docker Production Deployment

```bash
# Build optimized image
docker compose build open-webui

# Tag for registry
docker tag ree-ai-frontend:latest registry.example.com/ree-ai/frontend:v1.0.0

# Push to registry
docker push registry.example.com/ree-ai/frontend:v1.0.0

# Deploy
docker compose -f docker-compose.prod.yml up -d
```

### Static Hosting (Netlify/Vercel)

```bash
# Build static files
npm run build

# Output in ./build directory
# Upload to Netlify/Vercel or any static host
```

---

## Resources

- **Open WebUI Docs**: https://docs.openwebui.com
- **SvelteKit Docs**: https://kit.svelte.dev/docs
- **REE AI Architecture**: See `CLAUDE.md`
- **API Reference**: See backend service README files

---

## Getting Help

**Issues:**
- Frontend bugs: File issue in project repo
- Open WebUI issues: https://github.com/open-webui/open-webui/issues

**Support:**
- Slack: #ree-ai-frontend channel
- Email: dev@ree-ai.com

---

**Last Updated:** 2025-10-31
**Version:** 1.0.0
