#!/bin/bash

# ============================================================
# GitHub Secrets Management Script
# Setup required secrets for production deployment
# ============================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
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

show_help() {
    cat << EOF
GitHub Secrets Management for REE AI

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  setup       Setup all required secrets interactively
  list        List all configured secrets
  set KEY     Set a specific secret
  delete KEY  Delete a specific secret
  validate    Validate all required secrets are set

Options:
  --environment ENV    Target environment (production/staging)
  --help              Show this help

Examples:
  $0 setup                           # Setup all secrets interactively
  $0 list                           # List configured secrets
  $0 set OPENAI_API_KEY            # Set OpenAI API key
  $0 validate --environment production  # Validate production secrets

Required Secrets for Production:
  - OPENAI_API_KEY: OpenAI API key for LLM services
  - JWT_SECRET_KEY: JWT token signing key
  - WEBUI_SECRET_KEY: WebUI session secret
  - POSTGRES_PASSWORD: PostgreSQL database password
  - OPENSEARCH_PASSWORD: OpenSearch cluster password

EOF
}

check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        log "Install it with: sudo apt install gh"
        exit 1
    fi
    
    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI is not authenticated"
        log "Run: gh auth login"
        exit 1
    fi
}

list_secrets() {
    log "📋 Listing configured secrets..."
    
    local env="${1:-production}"
    
    echo "Environment: $env"
    echo "Repository: $(gh repo view --json nameWithOwner -q .nameWithOwner)"
    echo ""
    
    if gh secret list --env "$env" &> /dev/null; then
        log "Using environment-specific secrets:"
        gh secret list --env "$env" 2>/dev/null || {
            log_warning "No environment-specific secrets found"
        }
    else
        log "Using repository secrets:"
        gh secret list 2>/dev/null || {
            log_warning "No repository secrets found"
        }
    fi
}

generate_secure_key() {
    local length="${1:-32}"
    openssl rand -base64 "$length" | tr -d "=+/" | cut -c1-"$length"
}

set_secret() {
    local key="$1"
    local env="${2:-}"
    local value=""
    
    echo ""
    log "Setting secret: $key"
    
    case "$key" in
        "OPENAI_API_KEY")
            echo "Enter your OpenAI API key (starts with sk-):"
            read -s value
            
            if [[ ! "$value" =~ ^sk- ]]; then
                log_warning "OpenAI API key should start with 'sk-'"
                echo "Continue anyway? (y/N):"
                read -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    log "Cancelled"
                    return 1
                fi
            fi
            ;;
            
        "JWT_SECRET_KEY"|"WEBUI_SECRET_KEY")
            echo "Enter secret key (or press Enter to generate):"
            read -s value
            
            if [[ -z "$value" ]]; then
                value=$(generate_secure_key 64)
                log "Generated secure key: ${value:0:10}..."
            fi
            ;;
            
        "POSTGRES_PASSWORD"|"OPENSEARCH_PASSWORD")
            echo "Enter password (or press Enter to generate):"
            read -s value
            
            if [[ -z "$value" ]]; then
                value=$(generate_secure_key 16)
                log "Generated secure password: ${value:0:4}..."
            fi
            ;;
            
        *)
            echo "Enter value for $key:"
            read -s value
            ;;
    esac
    
    if [[ -z "$value" ]]; then
        log_error "Value cannot be empty"
        return 1
    fi
    
    # Set secret
    if [[ -n "$env" ]]; then
        echo "$value" | gh secret set "$key" --env "$env"
        log_success "Secret $key set for environment: $env"
    else
        echo "$value" | gh secret set "$key"
        log_success "Secret $key set for repository"
    fi
}

delete_secret() {
    local key="$1"
    local env="${2:-}"
    
    echo "Are you sure you want to delete secret '$key'? (y/N):"
    read -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ -n "$env" ]]; then
            gh secret delete "$key" --env "$env"
            log_success "Secret $key deleted from environment: $env"
        else
            gh secret delete "$key"
            log_success "Secret $key deleted from repository"
        fi
    else
        log "Cancelled"
    fi
}

setup_all_secrets() {
    local env="${1:-production}"
    
    log "🔐 Setting up GitHub Secrets for REE AI"
    log "Environment: $env"
    echo ""
    
    local required_secrets=(
        "OPENAI_API_KEY"
        "JWT_SECRET_KEY" 
        "WEBUI_SECRET_KEY"
        "POSTGRES_PASSWORD"
        "OPENSEARCH_PASSWORD"
    )
    
    log "Required secrets for production deployment:"
    for secret in "${required_secrets[@]}"; do
        echo "  - $secret"
    done
    echo ""
    
    echo "Do you want to setup all secrets now? (Y/n):"
    read -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log "Setup cancelled"
        return 0
    fi
    
    for secret in "${required_secrets[@]}"; do
        echo ""
        echo "----------------------------------------"
        log "Setting up: $secret"
        echo "----------------------------------------"
        
        set_secret "$secret" "$env" || {
            log_warning "Failed to set $secret, continuing..."
        }
    done
    
    echo ""
    log_success "🎉 Secret setup completed!"
    echo ""
    log "📋 Verifying secrets..."
    validate_secrets "$env"
}

validate_secrets() {
    local env="${1:-production}"
    
    log "🔍 Validating secrets for environment: $env"
    
    local required_secrets=(
        "OPENAI_API_KEY"
        "JWT_SECRET_KEY"
        "WEBUI_SECRET_KEY"
        "POSTGRES_PASSWORD"
        "OPENSEARCH_PASSWORD"
    )
    
    local missing_secrets=()
    
    for secret in "${required_secrets[@]}"; do
        if gh secret list --env "$env" 2>/dev/null | grep -q "^$secret" || gh secret list 2>/dev/null | grep -q "^$secret"; then
            log_success "$secret is configured"
        else
            log_error "$secret is missing"
            missing_secrets+=("$secret")
        fi
    done
    
    if [[ ${#missing_secrets[@]} -eq 0 ]]; then
        log_success "✅ All required secrets are configured"
        return 0
    else
        log_error "❌ Missing secrets: ${missing_secrets[*]}"
        echo ""
        echo "Setup missing secrets with:"
        for secret in "${missing_secrets[@]}"; do
            echo "  $0 set $secret --environment $env"
        done
        echo ""
        echo "Or run: $0 setup --environment $env"
        return 1
    fi
}

create_environment_template() {
    local env="${1:-production}"
    
    log "📝 Creating environment template..."
    
    cat > ".env.$env.template" << EOF
# ============================================================
# REE AI Environment Template - $env
# Copy to .env and fill in values
# ============================================================

# Database Configuration
POSTGRES_DB=ree_ai
POSTGRES_USER=ree_ai_user
POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# OpenAI Configuration
OPENAI_API_KEY=\${OPENAI_API_KEY}

# Security Configuration
JWT_SECRET_KEY=\${JWT_SECRET_KEY}
WEBUI_SECRET_KEY=\${WEBUI_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# OpenSearch Configuration
OPENSEARCH_HOST=opensearch
OPENSEARCH_PORT=9200
OPENSEARCH_PASSWORD=\${OPENSEARCH_PASSWORD}

# Feature Flags
USE_REAL_CORE_GATEWAY=true
USE_REAL_DB_GATEWAY=true
USE_ADVANCED_RAG=true

# Application Settings
PRODUCTION_MODE=true
DEBUG=false
LOG_LEVEL=INFO

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
    
    log_success "Environment template created: .env.$env.template"
}

# ============================================================
# MAIN SCRIPT
# ============================================================

main() {
    local command="${1:-help}"
    local environment="production"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment|--env)
                environment="$2"
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
    
    # Check prerequisites
    check_gh_cli
    
    # Execute command
    case "$command" in
        "setup")
            setup_all_secrets "$environment"
            ;;
        "list")
            list_secrets "$environment"
            ;;
        "set")
            if [[ $# -lt 2 ]]; then
                log_error "Secret name required"
                echo "Usage: $0 set SECRET_NAME"
                exit 1
            fi
            set_secret "$2" "$environment"
            ;;
        "delete")
            if [[ $# -lt 2 ]]; then
                log_error "Secret name required"
                echo "Usage: $0 delete SECRET_NAME"
                exit 1
            fi
            delete_secret "$2" "$environment"
            ;;
        "validate")
            validate_secrets "$environment"
            ;;
        "template")
            create_environment_template "$environment"
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"