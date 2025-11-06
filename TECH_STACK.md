# REE AI - Technology Stack Overview

## Executive Summary

REE AI is a production-ready, AI-powered real estate platform built on a modern microservices architecture. The system leverages advanced AI/ML technologies including LangChain, vector databases, and multiple LLM providers to deliver intelligent property search and recommendations.

**Core Innovation:** Flexible document storage (OpenSearch) combined with AI-powered Retrieval-Augmented Generation (RAG) enables semantic understanding of diverse property attributes, solving the rigid schema problem that plagues traditional real estate platforms.

---

## Architecture Overview

- **Architecture Pattern:** 7-Layer Microservices Architecture
- **Total Services:** 18+ specialized microservices
- **Communication Protocol:** RESTful APIs with async HTTP
- **Deployment:** Docker containerization with Docker Compose orchestration
- **Development Language:** Python (backend), TypeScript (frontend)

---

## Technology Stack by Category

### 1. Frontend Technologies

#### Primary Web Application
- **Next.js 14.0.4** - React framework with server-side rendering (SSR) and static site generation (SSG)
- **React 18.2** - UI component library
- **TypeScript 5.3** - Type-safe JavaScript development
- **Tailwind CSS 3.4** - Utility-first CSS framework for responsive design

#### UI Components & Libraries
- **Lucide React** - Modern icon library (300+ icons)
- **Tailwind Forms & Typography** - Enhanced form and text styling

#### State Management & Data Fetching
- **Zustand 4.4** - Lightweight state management
- **SWR 2.2** - React Hooks library for data fetching with caching
- **Axios 1.6** - HTTP client for API requests

#### Form Handling & Validation
- **React Hook Form 7.49** - Performant form validation
- **Zod 3.22** - TypeScript-first schema validation
- **@hookform/resolvers** - Form validation integration

#### Chat Interface
- **Open WebUI (Custom Build)** - Advanced chat interface for AI interactions
  - Features: Multi-model support, conversation history, markdown rendering
  - Integration: Direct connection to orchestrator layer

### 2. Backend Technologies

#### Core Framework
- **FastAPI 0.109** - Modern, high-performance Python web framework
  - Async/await support for non-blocking I/O
  - Automatic OpenAPI documentation generation
  - Built-in data validation with Pydantic
- **Uvicorn 0.27** - Lightning-fast ASGI server

#### Data Validation & Configuration
- **Pydantic 2.5** - Data validation using Python type annotations
- **Pydantic Settings 2.1** - Settings management from environment variables
- **Python Dotenv 1.0** - Environment configuration management

#### HTTP & Networking
- **HTTPX 0.26** - Async HTTP client for inter-service communication
- **Python Multipart 0.0.6** - Multipart form data handling

### 3. AI & Machine Learning

#### LLM Orchestration & Routing
- **LangChain 0.1.6** - Framework for building LLM applications
  - Intent detection and routing
  - Prompt templating
  - Chain-of-thought reasoning
- **LangChain OpenAI 0.0.5** - OpenAI integration for LangChain
- **LangChain Community 0.0.20** - Community-contributed LangChain tools

#### LLM Providers & Gateway
- **LiteLLM 1.17** - Unified API gateway for multiple LLM providers
  - Routes requests to OpenAI, Ollama, or custom models
  - Load balancing and fallback handling
- **OpenAI 1.10** - Official OpenAI Python client
  - Primary model: GPT-4 and GPT-4-mini
- **Ollama** - Local LLM deployment (self-hosted alternative)
  - Models: Llama 2, Llama 3.2, and custom fine-tuned models

#### RAG (Retrieval-Augmented Generation) Pipeline
- **Custom RAG Service** with advanced features:
  - Modular RAG architecture
  - Memory consolidation and reflection
  - Multi-agent supervisor pattern
  - Document grading and relevance scoring

### 4. Databases & Storage

#### Vector Database (PRIMARY - Property Data)
- **OpenSearch 2.11.0** - Distributed search and analytics engine
  - **Role:** Stores ALL property data as flexible JSON documents
  - **Features:**
    - Vector embeddings for semantic search
    - BM25 full-text search algorithm
    - Hybrid search (vector + keyword)
    - Dynamic schema (unlimited property attributes)
  - **Why:** Enables AI to understand diverse property variations without rigid table schemas

#### Relational Database (SECONDARY - User Data)
- **PostgreSQL 15** - Advanced open-source relational database
  - **Role:** Stores structured data only:
    - User accounts and authentication
    - Conversation history
    - Chat messages
    - System configuration
  - **ORM:** SQLAlchemy 2.0.25 for database operations
  - **Migration Tool:** Alembic 1.13.1 for schema versioning
  - **Driver:** psycopg2-binary 2.9.9 (PostgreSQL adapter)

#### Caching Layer
- **Redis 7 (Alpine)** - In-memory data store
  - Session management
  - Frequently accessed property listings
  - Search result caching
  - Rate limiting counters
  - **Client:** redis[hiredis] 5.0.1 with high-performance C parser

### 5. Infrastructure & DevOps

#### Containerization
- **Docker** - Application containerization
- **Docker Compose** - Multi-container orchestration
- **Docker Networks:** Custom bridge network (`ree-ai-network`) for service communication

#### Service Discovery & Routing
- **Custom Service Registry** - Dynamic service discovery
  - Auto-registration on service startup
  - Health check monitoring
  - Capability-based routing

#### API Gateway & Authentication
- **Custom API Gateway** - Centralized entry point
  - Rate limiting
  - Request routing
  - JWT validation
- **Authentication Service:**
  - JWT (JSON Web Tokens) - Stateless authentication
  - Python-jose 3.3 - JWT encoding/decoding
  - Passlib[bcrypt] 1.7 - Password hashing

### 6. Monitoring & Observability

#### Metrics & Monitoring
- **Prometheus Client 0.19** - Application metrics collection
  - Request latency tracking
  - Error rate monitoring
  - Service health metrics
- **Custom Monitoring Service** - Real-time system health dashboard
  - Docker container monitoring
  - Service registry integration
  - Web UI at port 9999

#### Error Tracking
- **Sentry SDK[FastAPI] 1.40** - Error tracking and performance monitoring
  - Automatic error capture
  - Performance profiling
  - Release tracking

#### Logging
- **Custom Structured Logging** - Consistent log formatting across all services
  - Emoji indicators for log levels
  - JSON-structured logs for analysis
  - Contextual logging with request IDs

### 7. Reliability & Performance

#### Resilience Patterns
- **Tenacity 8.2** - Retry logic with exponential backoff
  - Automatic retry on network failures
  - Configurable retry strategies
- **PyBreaker 1.0** - Circuit breaker pattern implementation
  - Prevents cascading failures
  - Automatic recovery detection
- **Cachetools 5.3** - In-memory caching utilities
  - LRU (Least Recently Used) cache
  - TTL (Time To Live) cache

#### Connection Pooling
- **AsyncPG 0.29** - High-performance PostgreSQL async driver
  - Connection pooling
  - Binary protocol for faster queries

### 8. Development & Testing

#### Testing Framework
- **Pytest 7.4** - Python testing framework
- **Pytest-Asyncio 0.21** - Async test support
- **Pytest-Cov 4.1** - Code coverage reporting

#### Code Quality
- **ESLint 8.56** - JavaScript/TypeScript linting
- **TypeScript Compiler** - Static type checking
- **Pydantic** - Runtime type validation for Python

---

## Microservices Architecture (7 Layers)

### Layer 0: Frontend & Gateway
1. **Open WebUI** (Port 3000) - Chat interface
2. **Next.js Frontend** (Port 3001) - Main web application (seller/buyer dashboards)
3. **API Gateway** (Port 8888) - Rate limiting, JWT auth, request routing
4. **Auth Service** (Port 8085) - User authentication and authorization
5. **Admin Dashboard** (Port 3002) - System administration interface

### Layer 1: Service Discovery
6. **Service Registry** (Port 8000) - Service catalog and health checks

### Layer 2: Orchestration
7. **Orchestrator** (Port 8090) - LangChain-powered intent detection and routing

### Layer 3: AI Specialized Services
8. **Semantic Chunking** (Port 8082) - Intelligent text segmentation
9. **Classification** (Port 8083) - Property type and intent classification
10. **Attribute Extraction** (Port 8084) - Extract structured data from text
11. **Completeness Check** (Port 8086) - Property listing quality validation
12. **Price Suggestion** (Port 8087) - AI-powered property valuation
13. **Reranking** (Port 8088) - Search result optimization

### Layer 4: Storage Gateway
14. **DB Gateway** (Port 8081) - Database abstraction layer
    - OpenSearch operations (property search, indexing)
    - PostgreSQL operations (user data, conversations)

### Layer 5: LLM Gateway
15. **Core Gateway** (Port 8080) - LiteLLM routing to Ollama/OpenAI

### Layer 6: RAG Pipeline
16. **RAG Service** (Port 8091) - Full retrieval-augmented generation pipeline
    - Advanced features: Memory, Multi-Agent, Document grading

### Supporting Services
17. **Monitoring Service** (Port 9999) - System health monitoring and alerting
18. **User Management Service** - User profile and preferences management

---

## Key Technical Features

### 1. Flexible Data Architecture
- **Problem Solved:** Traditional databases cannot handle diverse property attributes (villa vs. apartment vs. land)
- **Solution:** OpenSearch stores properties as flexible JSON documents with vector embeddings
- **Benefit:** AI can understand and search infinite property variations without schema changes

### 2. Hybrid Search Strategy
- **Vector Search:** Semantic understanding ("find homes near international schools")
- **BM25 Search:** Keyword matching for precise queries
- **Hybrid Fusion:** Combines both approaches for optimal results

### 3. AI-Powered Personalization
- **Memory System:** Tracks user preferences across conversations
- **Reflection:** AI analyzes conversation quality and adapts
- **Multi-Agent:** Specialized agents collaborate on complex queries

### 4. High Availability Design
- **Circuit Breakers:** Prevent cascading failures
- **Retry Logic:** Automatic recovery from transient failures
- **Caching:** Redis caching reduces database load
- **Health Checks:** Continuous service monitoring

### 5. Type-Safe API Contracts
- **Pydantic Models:** Shared type definitions across all services
- **Automatic Validation:** Invalid requests rejected at API boundary
- **Auto-Generated Docs:** FastAPI generates OpenAPI specs automatically

---

## Development Workflow

### Feature Flags
- **Mock Services:** Enable parallel development without dependencies
- **Real Services:** Gradual integration by switching feature flags
- **Environment Variables:** Configure in `.env` file

### Service Communication
- **Pattern:** HTTP REST APIs with async/await
- **Timeout Handling:** 30-90 second timeouts based on operation complexity
- **Error Propagation:** Structured error responses with logging

### Testing Strategy
- **Unit Tests:** Service-level logic testing
- **Integration Tests:** End-to-end API testing
- **Health Checks:** All services expose `/health` endpoints
- **Automated Testing:** Docker Compose test environment

---

## Scalability & Performance

### Horizontal Scaling
- **Stateless Services:** All services can scale horizontally
- **Load Balancing:** LiteLLM routes LLM requests across providers
- **Database Sharding:** OpenSearch supports horizontal scaling

### Performance Optimizations
- **Async I/O:** Non-blocking operations throughout the stack
- **Connection Pooling:** Reuse database connections
- **Caching Strategy:** Multi-layer caching (Redis + in-memory)
- **Lazy Loading:** Services load dependencies on-demand

### Resource Efficiency
- **Docker Alpine Images:** Minimal container size
- **Java Heap Tuning:** OpenSearch optimized for 512MB-1GB
- **Connection Limits:** Configured per service requirements

---

## Security Features

### Authentication & Authorization
- **JWT Tokens:** Stateless authentication with configurable expiration
- **Password Hashing:** bcrypt with salt for secure password storage
- **Role-Based Access Control:** Planned for future releases

### API Security
- **Rate Limiting:** Prevent API abuse
- **Request Validation:** Pydantic validates all incoming data
- **CORS Configuration:** Cross-origin request controls

### Data Privacy
- **Environment Variables:** Sensitive data never committed to code
- **Secret Management:** JWT keys and API keys stored in `.env`
- **Database Encryption:** PostgreSQL supports encryption at rest (configurable)

---

## Deployment & Operations

### Local Development
```bash
# Start all services
docker-compose --profile all up -d

# View logs
docker-compose logs -f orchestrator

# Run tests
./scripts/run-tests.sh
```

### Production Considerations
- **Environment Separation:** Different `.env` for dev/staging/production
- **Secret Rotation:** Regular JWT key and API key updates
- **Backup Strategy:** PostgreSQL automated backups, OpenSearch snapshots
- **Monitoring Alerts:** Sentry for errors, Prometheus for metrics

### CI/CD Recommendations
- **Container Registry:** Push Docker images to registry
- **Automated Testing:** Run test suite before deployment
- **Rolling Deployments:** Zero-downtime service updates
- **Health Check Gates:** Only deploy if health checks pass

---

## Future Technology Roadmap

### Planned Enhancements
1. **Message Queue Integration:** RabbitMQ or Kafka for async processing
2. **Graph Database:** Neo4j for relationship-based property recommendations
3. **Mobile Applications:** React Native for iOS/Android
4. **Real-time Updates:** WebSocket support for live chat
5. **Advanced Analytics:** Apache Spark for big data processing

### AI Model Expansion
1. **Custom Fine-tuned Models:** Domain-specific real estate models
2. **Multi-modal AI:** Image recognition for property photos
3. **Voice Interface:** Speech-to-text for voice search
4. **Predictive Analytics:** Market trend predictions

---

## Summary

REE AI leverages a modern, cloud-native technology stack designed for:
- **Scalability:** Microservices can scale independently
- **Flexibility:** OpenSearch enables unlimited property attributes
- **Intelligence:** LangChain + RAG delivers context-aware responses
- **Reliability:** Circuit breakers, retries, and health checks ensure uptime
- **Developer Experience:** Type-safe APIs, auto-generated docs, comprehensive testing

The platform solves the fundamental challenge of traditional real estate platforms—rigid data schemas—by combining flexible document storage with advanced AI to understand natural language queries and diverse property attributes.

---

**Tech Stack Version:** 1.0 (January 2025)
**Last Updated:** 2025-01-06
**Architecture:** 7-Layer Microservices (18+ services)
**Primary Language:** Python 3.11+ (Backend), TypeScript 5.3+ (Frontend)
