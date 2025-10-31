# REE AI - Custom Open WebUI Frontend

## Overview

This is a customized version of Open WebUI specifically tailored for REE AI real estate intelligence platform.

## Custom Features

### 1. Real Estate Property Search
- Integrated with REE AI Storage service (OpenSearch)
- Property listing display with Vietnamese text support
- Advanced filters (type, location, price, area)

### 2. AI-Powered Chat
- Connected to REE AI Orchestrator (LangChain-powered routing)
- Intent detection for property queries
- Multi-modal responses (text + property cards)

### 3. Data Pipeline Integration
- Crawl4AI integration for real-time property data
- Classification service for property categorization
- RAG-enabled search with semantic understanding

## Architecture

```
┌─────────────────────────────────────┐
│   REE AI Open WebUI (Port 3000)    │
│   - SvelteKit Frontend               │
│   - Real Estate UI Components        │
└──────────────────┬──────────────────┘
                   │
                   ↓
┌─────────────────────────────────────┐
│   Orchestrator (Port 8090)          │
│   - Intent Detection                 │
│   - Service Routing                  │
└──────────────────┬──────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
┌───────────────┐    ┌────────────────┐
│ Crawler       │    │ Storage        │
│ (Port 8100)   │    │ (Port 8103)    │
└───────────────┘    └────────────────┘
```

## Quick Start

### Prerequisites
- **Docker** 20.10+ (for production build)
- **Node.js** 18+ (for local development)
- **npm** or **pnpm**
- REE AI backend services running

### Installation

#### Option 1: Docker Build (Recommended for Production)

```bash
# From project root
./scripts/build-frontend.sh

# Or on Windows
scripts\build-frontend.bat

# Start the frontend
docker compose --profile real up -d open-webui

# Access at http://localhost:3000
```

#### Option 2: Local Development

```bash
# Install dependencies
npm ci --force

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

See [Frontend Build Guide](../../docs/FRONTEND_BUILD_GUIDE.md) for detailed instructions.

### Environment Variables

See `.env` file for configuration. Key variables:

- `OPENAI_API_BASE_URL`: Points to Orchestrator (default: http://localhost:8090/v1)
- `REE_AI_STORAGE_URL`: Storage service URL
- `WEBUI_NAME`: Application name (REE AI)

## Development

### Running with Backend Services

1. Start all backend services:
```bash
# From project root
docker-compose up -d postgres opensearch redis
python3 -m services.crawler.main &
python3 -m services.classification.main &
python3 -m services.storage.main &
python3 -m services.orchestrator.main &
```

2. Start frontend:
```bash
cd frontend/open-webui
npm run dev
```

3. Access at http://localhost:3000

## Customizations

### 1. Theme & Branding
- Updated app name to "REE AI"
- Custom color scheme for real estate
- Vietnamese language support

### 2. Property Components
Location: `src/lib/components/property/`
- `PropertyCard.svelte` - Property listing card
- `PropertySearch.svelte` - Search interface
- `PropertyDetails.svelte` - Detailed view

### 3. API Integration
Location: `src/lib/apis/ree-ai/`
- `orchestrator.ts` - Orchestrator service API (intent detection & routing)
- `storage.ts` - Storage/search API (OpenSearch property search)
- `classification.ts` - Classification API (property type & attributes)
- `rag.ts` - RAG service API (retrieval-augmented generation)

**Usage Example:**
```typescript
import { searchProperties } from '$lib/apis/ree-ai';

const results = await searchProperties(token, {
  query: "căn hộ 2 phòng ngủ",
  filters: {
    property_type: ["apartment"],
    min_price: 2000000000
  }
});
```

### 4. Chat Enhancements
- Property-aware responses
- Inline property cards in chat
- Smart suggestions based on context

## Testing

```bash
# Run unit tests
npm run test

# Run E2E tests
npm run test:e2e

# Lint
npm run lint
```

## Docker Build

### Quick Build
```bash
# From project root
./scripts/build-frontend.sh

# This will build and show next steps
```

### Manual Build
```bash
# Build custom image
docker compose build open-webui

# Or with custom args
docker compose build --build-arg USE_CUDA=true open-webui

# Run
docker compose --profile real up -d open-webui

# View logs
docker compose logs -f open-webui
```

### Environment Configuration

Key environment variables in `docker-compose.yml`:

```yaml
environment:
  - OPENAI_API_BASE_URL=http://orchestrator:8080
  - WEBUI_NAME=REE AI - Real Estate Assistant
  - DATABASE_URL=postgresql://user:pass@postgres:5432/ree_ai
  - ENABLE_OPENAI_API=true
  - ENABLE_OLLAMA_API=false
```

## Production Deployment

1. Build optimized production bundle:
```bash
npm run build
```

2. Deploy using Docker or static hosting
3. Configure environment variables for production
4. Enable authentication (set `WEBUI_AUTH=true`)

## Troubleshooting

### Connection Issues
- Ensure all backend services are running
- Check `OPENAI_API_BASE_URL` points to correct Orchestrator
- Verify CORS settings if running on different domains

### Build Errors
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version (18+ required)
- Ensure all environment variables are set

## Contributing

This is a customized fork. For general Open WebUI issues, refer to upstream repo.
For REE AI specific features, contact the development team.

## License

Based on Open WebUI (MIT License)
Custom modifications © 2025 REE AI
