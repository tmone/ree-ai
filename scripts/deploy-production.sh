#!/bin/bash

# ============================================================
# REE AI Production Deployment Script
# Portable deployment script for any production environment
# ============================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ============================================================
# CONFIGURATION
# ============================================================

# Default configuration (can be overridden by environment variables)
PROJECT_NAME="${PROJECT_NAME:-ree-ai}"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-production}"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
DOCKER_COMPOSE_PROFILE="${DOCKER_COMPOSE_PROFILE:-real}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# LOGGING FUNCTIONS
# ============================================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "curl" "timeout")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check project files
    if [[ ! -f "$PROJECT_DIR/docker-compose.yml" ]]; then
        log_error "docker-compose.yml not found in $PROJECT_DIR"
        exit 1
    fi
    
    if [[ ! -f "$PROJECT_DIR/.env.example" ]] && [[ ! -f "$PROJECT_DIR/.env" ]]; then
        log_warning ".env.example not found. Will create basic .env file"
    fi
    
    log_success "Prerequisites check passed"
}

validate_environment() {
    log "🔍 Validating deployment environment..."
    
    # Check required environment variables
    local required_vars=()
    
    if [[ "$DEPLOYMENT_ENV" == "production" ]]; then
        required_vars+=("OPENAI_API_KEY" "JWT_SECRET_KEY" "WEBUI_SECRET_KEY")
    fi
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable '$var' is not set"
            exit 1
        fi
    done
    
    log_success "Environment validation passed"
}

# ============================================================
# DEPLOYMENT FUNCTIONS
# ============================================================

stop_existing_services() {
    log "🛑 Stopping existing services..."
    
    if docker-compose ps --services &> /dev/null; then
        docker-compose down --remove-orphans || {
            log_warning "Some services failed to stop gracefully"
        }
    fi
    
    log_success "Existing services stopped"
}

setup_environment() {
    log "⚙️ Setting up environment configuration..."
    
    if [[ ! -f "$PROJECT_DIR/.env" ]]; then
        if [[ -f "$PROJECT_DIR/.env.example" ]]; then
            cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
            log "Copied .env.example to .env"
        else
            create_default_env
        fi
    fi
    
    # Override environment-specific settings
    if [[ "$DEPLOYMENT_ENV" == "production" ]]; then
        {
            echo "# Production overrides"
            echo "PRODUCTION_MODE=true"
            echo "DEBUG=false"
            echo "LOG_LEVEL=${LOG_LEVEL}"
            echo "USE_REAL_CORE_GATEWAY=true"
            echo "USE_REAL_DB_GATEWAY=true"
            echo "USE_ADVANCED_RAG=true"
        } >> "$PROJECT_DIR/.env"
    fi
    
    log_success "Environment configuration ready"
}

create_default_env() {
    log "📝 Creating default .env file..."
    
    cat > "$PROJECT_DIR/.env" << 'EOF'
# ============================================================
# REE AI Environment Configuration
# Generated automatically by deployment script
# ============================================================

# Database Configuration
POSTGRES_DB=ree_ai
POSTGRES_USER=ree_ai_user
POSTGRES_PASSWORD=changeme_secure_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# OpenAI Configuration
OPENAI_API_KEY=${OPENAI_API_KEY}

# OpenSearch Configuration
OPENSEARCH_HOST=opensearch
OPENSEARCH_PORT=9200
OPENSEARCH_PASSWORD=Admin123!@#

# Security Configuration
WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-changeme-secret-key}
JWT_SECRET_KEY=${JWT_SECRET_KEY:-changeme-jwt-secret}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Feature Flags
USE_REAL_CORE_GATEWAY=true
USE_REAL_DB_GATEWAY=true
USE_ADVANCED_RAG=true

# Application Settings
PRODUCTION_MODE=${PRODUCTION_MODE:-false}
DEBUG=${DEBUG:-true}
LOG_LEVEL=${LOG_LEVEL:-INFO}

# Auto-generation Features
ENABLE_FOLLOW_UP_GENERATION=true
ENABLE_TITLE_GENERATION=true
ENABLE_TAGS_GENERATION=true
ENABLE_AUTOCOMPLETE_GENERATION=false

# Performance Settings
MEMORY_RETENTION_DAYS=90
MEMORY_CONSOLIDATION_THRESHOLD=10
REFLECTION_QUALITY_THRESHOLD=0.7
DOCUMENT_GRADER_THRESHOLD=0.5
AGENT_TIMEOUT_SECONDS=30
SUPERVISOR_MAX_RETRIES=2

# Model Configuration
TASK_MODEL=llama3.2:latest
EOF
}

build_services() {
    log "🔨 Building services..."
    
    # Pull external images first
    log "📦 Pulling external images..."
    docker-compose pull postgres redis opensearch || {
        log_warning "Some external images failed to pull"
    }
    
    # Build application services
    log "🏗️ Building application services..."
    docker-compose build --parallel || {
        log_error "Service build failed"
        exit 1
    }
    
    log_success "Services built successfully"
}

start_infrastructure() {
    log "🏗️ Starting infrastructure services..."
    
    # Start infrastructure in order
    local infrastructure_services=("postgres" "redis" "opensearch")
    
    for service in "${infrastructure_services[@]}"; do
        log "Starting $service..."
        docker-compose up -d "$service"
        
        # Wait for service to be ready
        case $service in
            "postgres")
                wait_for_postgres
                ;;
            "redis")
                wait_for_redis
                ;;
            "opensearch")
                wait_for_opensearch
                ;;
        esac
    done
    
    log_success "Infrastructure services started"
}

wait_for_postgres() {
    log "⏳ Waiting for PostgreSQL..."
    
    local retries=30
    while [[ $retries -gt 0 ]]; do
        if docker-compose exec -T postgres pg_isready -U "${POSTGRES_USER:-ree_ai_user}" &> /dev/null; then
            log_success "PostgreSQL is ready"
            return 0
        fi
        ((retries--))
        sleep 2
    done
    
    log_error "PostgreSQL failed to start within timeout"
    docker-compose logs postgres
    exit 1
}

wait_for_redis() {
    log "⏳ Waiting for Redis..."
    
    local retries=30
    while [[ $retries -gt 0 ]]; do
        if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
            log_success "Redis is ready"
            return 0
        fi
        ((retries--))
        sleep 2
    done
    
    log_error "Redis failed to start within timeout"
    docker-compose logs redis
    exit 1
}

wait_for_opensearch() {
    log "⏳ Waiting for OpenSearch..."
    
    local retries=60
    while [[ $retries -gt 0 ]]; do
        if curl -f http://localhost:9200 &> /dev/null; then
            log_success "OpenSearch is ready"
            return 0
        fi
        ((retries--))
        sleep 2
    done
    
    log_error "OpenSearch failed to start within timeout"
    docker-compose logs opensearch
    exit 1
}

start_application_services() {
    log "🚀 Starting application services..."
    
    # Start services in dependency order
    local service_groups=(
        "service-registry"
        "core-gateway db-gateway auth-service"
        "classification attribute-extraction completeness semantic-chunking"
        "orchestrator rag-service"
        "open-webui"
    )
    
    for group in "${service_groups[@]}"; do
        log "Starting service group: $group"
        docker-compose up -d $group
        
        # Wait a bit between groups
        sleep 10
        
        # Health check for critical services
        if [[ "$group" == "service-registry" ]]; then
            wait_for_service_health "http://localhost:8000/health" "Service Registry"
        elif [[ "$group" == *"core-gateway"* ]]; then
            wait_for_service_health "http://localhost:8080/health" "Core Gateway"
        fi
    done
    
    log_success "Application services started"
}

wait_for_service_health() {
    local url=$1
    local service_name=$2
    local retries=30
    
    log "⏳ Waiting for $service_name to be healthy..."
    
    while [[ $retries -gt 0 ]]; do
        if curl -f "$url" &> /dev/null; then
            log_success "$service_name is healthy"
            return 0
        fi
        ((retries--))
        sleep 2
    done
    
    log_warning "$service_name health check failed (non-critical)"
}

verify_deployment() {
    log "🔍 Verifying deployment..."
    
    # Service health checks
    local services=(
        "http://localhost:8000/health|Service Registry"
        "http://localhost:8080/health|Core Gateway"
        "http://localhost:8081/health|DB Gateway"
        "http://localhost:8090/health|Orchestrator"
        "http://localhost:8091/health|RAG Service"
        "http://localhost:3000|Open WebUI"
    )
    
    local healthy_count=0
    local total_count=${#services[@]}
    
    for service_info in "${services[@]}"; do
        IFS='|' read -r url name <<< "$service_info"
        
        if curl -f "$url" &> /dev/null; then
            log_success "$name is healthy"
            ((healthy_count++))
        else
            log_warning "$name is not responding"
        fi
    done
    
    log "📊 Health check results: $healthy_count/$total_count services healthy"
    
    if [[ $healthy_count -eq $total_count ]]; then
        log_success "All services are healthy"
    elif [[ $healthy_count -gt $((total_count / 2)) ]]; then
        log_warning "Some services are not responding, but deployment is functional"
    else
        log_error "Too many services are failing"
        show_service_status
        exit 1
    fi
}

show_service_status() {
    log "📊 Final service status:"
    docker-compose ps
}

cleanup() {
    log "🧹 Performing cleanup..."
    
    # Remove unused Docker images
    docker image prune -f &> /dev/null || true
    
    log_success "Cleanup completed"
}

show_deployment_summary() {
    local deployment_time=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    local server_ip=$(hostname -I | awk '{print $1}' || echo "localhost")
    
    cat << EOF

========================================
🚀 REE AI Deployment Summary
========================================
Environment: $DEPLOYMENT_ENV
Project: $PROJECT_NAME
Directory: $PROJECT_DIR
Timestamp: $deployment_time
Server: $server_ip

🌐 Access URLs:
  - Open WebUI: http://$server_ip:3000
  - Core Gateway: http://$server_ip:8080
  - Service Registry: http://$server_ip:8000
  - Orchestrator: http://$server_ip:8090
  - RAG Service: http://$server_ip:8091

📊 Infrastructure:
  - PostgreSQL: port 5432
  - Redis: port 6379
  - OpenSearch: port 9200

📋 Management Commands:
  - View logs: docker-compose logs [service]
  - Stop all: docker-compose down
  - Restart: docker-compose restart [service]
  - Status: docker-compose ps

Status: ✅ DEPLOYED
========================================

EOF
}

# ============================================================
# ERROR HANDLING
# ============================================================

handle_error() {
    local exit_code=$?
    log_error "Deployment failed with exit code $exit_code"
    
    log "📋 Showing recent logs for debugging:"
    docker-compose logs --tail=50 || true
    
    exit $exit_code
}

trap handle_error ERR

# ============================================================
# MAIN DEPLOYMENT FLOW
# ============================================================

main() {
    log "🚀 Starting REE AI Production Deployment"
    log "Environment: $DEPLOYMENT_ENV"
    log "Project Directory: $PROJECT_DIR"
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Execute deployment steps
    check_prerequisites
    validate_environment
    stop_existing_services
    setup_environment
    build_services
    start_infrastructure
    start_application_services
    verify_deployment
    show_service_status
    cleanup
    show_deployment_summary
    
    log_success "🎉 Deployment completed successfully!"
}

# ============================================================
# SCRIPT EXECUTION
# ============================================================

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            DEPLOYMENT_ENV="$2"
            shift 2
            ;;
        --project-dir)
            PROJECT_DIR="$2"
            shift 2
            ;;
        --profile)
            DOCKER_COMPOSE_PROFILE="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        -h|--help)
            cat << EOF
REE AI Production Deployment Script

Usage: $0 [OPTIONS]

Options:
  --env ENV              Deployment environment (default: production)
  --project-dir DIR      Project directory (default: current directory)
  --profile PROFILE      Docker Compose profile (default: real)
  --log-level LEVEL      Log level (default: INFO)
  -h, --help            Show this help message

Environment Variables:
  PROJECT_NAME          Project name (default: ree-ai)
  DEPLOYMENT_ENV        Deployment environment
  PROJECT_DIR           Project directory
  OPENAI_API_KEY        OpenAI API key (required for production)
  JWT_SECRET_KEY        JWT secret key (required for production)
  WEBUI_SECRET_KEY      WebUI secret key (required for production)

Examples:
  $0                                    # Deploy with defaults
  $0 --env staging                      # Deploy to staging
  $0 --project-dir /opt/ree-ai         # Deploy to specific directory
  
EOF
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main deployment
main "$@"