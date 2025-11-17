# Cloud-Based AI Provider Strategy for REE AI Production

## Overview
This configuration implements a **Primary-Fallback strategy** where:
- **Primary**: OpenAI (gpt-4o, gpt-4o-mini, etc.)
- **Fallback**: Ollama Cloud (llama3.1, llama3.2, etc.)

## Strategy Logic

### 1. Normal Operation (OpenAI Primary)
```
User Request → Core Gateway → OpenAI API → Response
```

### 2. Fallback Mode (When OpenAI Fails)
```
User Request → Core Gateway → OpenAI API (FAIL) → Ollama Cloud → Response
```

### 3. Circuit Breaker Pattern
- After 3 consecutive OpenAI failures → Switch to Ollama for 60 seconds
- Automatically retry OpenAI after timeout
- Prevents cascading failures

## Model Mapping Strategy

### Primary Models (OpenAI)
```
gpt-4o → Primary choice for complex tasks
gpt-4o-mini → Primary choice for simple/fast tasks
gpt-3.5-turbo → Legacy support
```

### Fallback Models (Ollama Cloud)
```
llama3.1:70b → Fallback for gpt-4o
llama3.2:3b → Fallback for gpt-4o-mini
llama3.2:3b → Default fallback
```

## Configuration

### Environment Variables
```bash
# Provider Strategy
PRIMARY_MODEL_PROVIDER=openai
FALLBACK_MODEL_PROVIDER=ollama
USE_OLLAMA_AS_FALLBACK=true

# API Keys (separate for each provider)
OPENAI_API_KEY=sk-...
OLLAMA_API_KEY=ollama-...

# Circuit Breaker Settings
CIRCUIT_BREAKER_FAILURE_THRESHOLD=3
CIRCUIT_BREAKER_TIMEOUT=60
MODEL_RETRY_COUNT=2
```

### Benefits
✅ **High Availability**: System continues working if OpenAI is down
✅ **Cost Optimization**: Use cheaper Ollama as backup
✅ **Performance**: Primary on fast OpenAI, fallback maintains functionality
✅ **No Local Models**: Both providers are cloud-based
✅ **Automatic Recovery**: Circuit breaker auto-returns to primary

### Service Behavior
- **Core Gateway**: Implements provider switching logic
- **Orchestrator**: Routes requests based on provider availability
- **Open WebUI**: Users see seamless experience regardless of active provider
- **Monitoring**: Tracks provider health and switches

This approach ensures REE AI maintains high availability while optimizing for performance and cost.