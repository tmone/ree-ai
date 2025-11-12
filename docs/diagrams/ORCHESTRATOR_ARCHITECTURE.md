# Orchestrator Architecture Diagram

## High-Level Architecture (CTO Design)

```mermaid
graph TB
    %% Styling
    classDef userClass fill:#90EE90,stroke:#333,stroke-width:2px
    classDef orchestratorClass fill:#FFD700,stroke:#333,stroke-width:3px
    classDef layer3Class fill:#FFEB99,stroke:#333,stroke-width:2px
    classDef storageClass fill:#B0E0B0,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    classDef flowClass fill:#FFF,stroke:#999,stroke-width:1px,stroke-dasharray: 3 3

    %% Entry Point
    USER((USER)):::userClass
    WEBUI[Open WebUI]:::userClass

    %% Central Orchestrator
    ORCH[Orchestrator<br/>Layer 2]:::orchestratorClass

    %% Layer 3 Services (AI Services)
    CLASS[Classification<br/>:8083]:::layer3Class
    EXTRACT[Attribute Extraction<br/>:8084]:::layer3Class
    COMPLETE[Completeness Check<br/>:8086]:::layer3Class
    CHUNK[Semantic Chunking<br/>:8082]:::layer3Class
    RERANK[Reranking<br/>:8088]:::layer3Class
    PRICE[Price Suggestion<br/>:8087]:::layer3Class

    %% Layer 4 Storage
    DBGW[DB Gateway<br/>:8081]:::layer3Class
    POSTGRES[(PostgreSQL<br/>Relational)]:::storageClass
    OPENSEARCH[(OpenSearch<br/>Vector + BM25)]:::storageClass

    %% Layer 5 LLM Gateway
    COREGW[Core Gateway<br/>:8080]:::layer3Class

    %% Main Flow
    USER --> WEBUI
    WEBUI --> ORCH

    %% Orchestrator to Layer 3 (Solid lines - direct calls)
    ORCH -->|1. Detect Intent| CLASS
    ORCH -->|2. Extract Attributes| EXTRACT
    ORCH -->|3. Check Completeness| COMPLETE
    ORCH -->|4. Chunk Text| CHUNK
    ORCH -->|5. Rerank Results| RERANK
    ORCH -->|6. Suggest Price| PRICE
    ORCH -->|7. Search/Save| DBGW
    ORCH -->|8. LLM Call| COREGW

    %% Storage connections
    DBGW --> POSTGRES
    DBGW --> OPENSEARCH
    CHUNK --> OPENSEARCH

    %% Legend
    subgraph Legend
        L1[Solid Line: Direct Service Call]
        L2[Dashed Box: Storage Layer]
        style L1 fill:#FFF,stroke:#333,stroke-width:2px
        style L2 fill:#B0E0B0,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    end
```

---

## Case 1: Property Posting Flow (POST_SALE / POST_RENT)

```mermaid
graph TB
    %% Styling
    classDef orchestratorClass fill:#FFD700,stroke:#333,stroke-width:3px
    classDef serviceClass fill:#FFEB99,stroke:#333,stroke-width:2px
    classDef stepClass fill:#E8F4F8,stroke:#4A90E2,stroke-width:2px,stroke-dasharray: 3 3

    %% Entry
    START([User: Toi can dang tin ban nha])
    ORCH[Orchestrator]:::orchestratorClass

    %% Services (called by Orchestrator)
    CLASS[Classification Service]:::serviceClass
    EXTRACT[Extraction Service]:::serviceClass
    COMPLETE[Completeness Service]:::serviceClass

    %% Internal Flow Steps (dashed vertical)
    STEP1[Step 1: Attribute Extraction<br/>Extract property info]:::stepClass
    STEP2[Step 2: Completeness Assessment<br/>Score: 0-100]:::stepClass
    STEP3[Step 3: Feedback Generation<br/>Missing fields + Suggestions]:::stepClass
    RESPONSE([Response: Can bo sung<br/>dien tich, hinh anh...])

    %% Main Flow
    START --> ORCH

    %% Solid lines: Service calls
    ORCH ==>|Classify Intent| CLASS
    CLASS -.->|POST_SALE| ORCH

    ORCH ==>|Call Service| EXTRACT
    ORCH ==>|Call Service| COMPLETE

    %% Internal flow (dashed vertical)
    ORCH -.Step 1.-> STEP1
    STEP1 -.->|entities| STEP2
    STEP2 -.->|score, missing| STEP3
    STEP3 -.-> RESPONSE

    %% Layout
    START --> ORCH --> STEP1
    STEP1 --> STEP2
    STEP2 --> STEP3
    STEP3 --> RESPONSE
```

**Flow Description:**
1. **Orchestrator calls Classification** → Intent: `POST_SALE`
2. **Internal Step 1** (dashed): Call Extraction Service → Extract attributes
3. **Internal Step 2** (dashed): Call Completeness Service → Score 0-100
4. **Internal Step 3** (dashed): Generate feedback response
5. **Return** to user with completeness feedback

---

## Case 2: Property Search Flow (SEARCH_BUY / SEARCH_RENT)

```mermaid
graph TB
    %% Styling
    classDef orchestratorClass fill:#FFD700,stroke:#333,stroke-width:3px
    classDef serviceClass fill:#FFEB99,stroke:#333,stroke-width:2px
    classDef stepClass fill:#E8F4F8,stroke:#4A90E2,stroke-width:2px,stroke-dasharray: 3 3
    classDef decisionClass fill:#FFE6CC,stroke:#D79B00,stroke-width:2px

    %% Entry
    START([User: Tim can ho 2PN o Q2])
    ORCH[Orchestrator<br/>ReAct Agent]:::orchestratorClass

    %% Services
    CLASS[Classification Service]:::serviceClass
    EXTRACT[Extraction Service]:::serviceClass
    DBGW[DB Gateway]:::serviceClass
    OPENSEARCH[(OpenSearch)]:::serviceClass

    %% Internal Flow Steps (dashed vertical)
    STEP1[REASONING<br/>Analyze requirements]:::stepClass
    STEP2[ACT<br/>Execute search]:::stepClass
    STEP3[EVALUATE<br/>Quality check]:::stepClass
    DECISION{Quality OK?}:::decisionClass
    STEP4A[ITERATE<br/>Refine query]:::stepClass
    STEP4B[Strategy 1: Location only<br/>Strategy 2: Semantic<br/>Strategy 3: Give up]:::stepClass
    RESPONSE([Response: 8 properties found])

    %% Main Flow
    START --> ORCH

    %% Service calls (solid)
    ORCH ==>|Classify| CLASS
    ORCH ==>|Extract filters| EXTRACT
    ORCH ==>|Search| DBGW
    DBGW ==> OPENSEARCH

    %% Internal ReAct Loop (dashed vertical)
    ORCH -.Iteration 1.-> STEP1
    STEP1 -.-> STEP2
    STEP2 -.-> STEP3
    STEP3 -.-> DECISION

    DECISION -.YES.-> RESPONSE
    DECISION -.NO.-> STEP4A
    STEP4A -.Retry.-> STEP1

    STEP4A -.2 failures.-> STEP4B
    STEP4B -.-> RESPONSE

    %% Layout
    START --> ORCH --> STEP1
    STEP1 --> STEP2
    STEP2 --> STEP3
    STEP3 --> DECISION
    DECISION -->|Yes| RESPONSE
    DECISION -->|No| STEP4A
    STEP4A --> STEP1
    STEP4A --> STEP4B
    STEP4B --> RESPONSE
```

**Flow Description:**
1. **Orchestrator calls Classification** → Intent: `SEARCH_BUY`, Mode: `filter`
2. **ReAct Loop (dashed vertical)**:
   - **REASONING**: Analyze query requirements
   - **ACT**: Call Extraction + DB Gateway → Search OpenSearch
   - **EVALUATE**: Check result quality (count, relevance)
   - **DECIDE**:
     - If quality OK → Generate response
     - If NOT OK → Refine query (max 2 iterations)
     - If 2 failures → Progressive relaxation strategies
3. **Return** natural language response with properties

---

## Case 3: Price Consultation Flow (PRICE_CONSULTATION) - Proposed

```mermaid
graph TB
    %% Styling
    classDef orchestratorClass fill:#FFD700,stroke:#333,stroke-width:3px
    classDef serviceClass fill:#FFEB99,stroke:#333,stroke-width:2px
    classDef stepClass fill:#E8F4F8,stroke:#4A90E2,stroke-width:2px,stroke-dasharray: 3 3
    classDef proposedClass fill:#FFE6E6,stroke:#E74C3C,stroke-width:2px,stroke-dasharray: 5 5

    %% Entry
    START([User: Can ho 2PN o Q2 gia bao nhieu?])
    ORCH[Orchestrator]:::orchestratorClass

    %% Services
    CLASS[Classification Service]:::serviceClass
    EXTRACT[Extraction Service]:::serviceClass
    PRICE[Price Suggestion Service<br/>NOT INTEGRATED YET]:::proposedClass

    %% Internal Flow Steps
    STEP1[Step 1: Extract Property<br/>Type, district, bedrooms]:::stepClass
    STEP2[Step 2: Market Analysis<br/>Historical prices, trends]:::stepClass
    STEP3[Step 3: Generate Consultation<br/>Price range + insights]:::stepClass
    RESPONSE([Response: Gia 5.0-5.5 ty<br/>+ market insights])

    %% Main Flow
    START --> ORCH

    %% Service calls
    ORCH ==>|Classify| CLASS
    CLASS -.->|PRICE_CONSULTATION| ORCH

    ORCH ==>|Call| EXTRACT
    ORCH ==>|Call<br/>NOT READY| PRICE

    %% Internal flow
    ORCH -.Step 1.-> STEP1
    STEP1 -.-> STEP2
    STEP2 -.-> STEP3
    STEP3 -.-> RESPONSE

    %% Layout
    START --> ORCH --> STEP1
    STEP1 --> STEP2
    STEP2 --> STEP3
    STEP3 --> RESPONSE

    %% Note
    NOTE[⚠️ NOT IMPLEMENTED<br/>Need to add routing logic]:::proposedClass
    PRICE -.-> NOTE
```

**Status:** ⚠️ **Not implemented yet**

**Proposed Flow:**
1. **Orchestrator calls Classification** → Intent: `PRICE_CONSULTATION`
2. **Internal Step 1** (dashed): Call Extraction Service → Extract property attributes
3. **Internal Step 2** (dashed): Call Price Suggestion Service → Market analysis
4. **Internal Step 3** (dashed): Generate consultation with price range + insights
5. **Return** price consultation response

---

## Case 4: General Chat Flow (CHAT)

```mermaid
graph TB
    %% Styling
    classDef orchestratorClass fill:#FFD700,stroke:#333,stroke-width:3px
    classDef serviceClass fill:#FFEB99,stroke:#333,stroke-width:2px
    classDef stepClass fill:#E8F4F8,stroke:#4A90E2,stroke-width:2px,stroke-dasharray: 3 3
    classDef decisionClass fill:#FFE6CC,stroke:#D79B00,stroke-width:2px

    %% Entry
    START([User: Xin chao / Can ho nay the nao? + image])
    ORCH[Orchestrator]:::orchestratorClass

    %% Services
    CLASS[Classification Service]:::serviceClass
    COREGW[Core Gateway<br/>LiteLLM]:::serviceClass
    LLM[GPT-4o / GPT-4o-mini]:::serviceClass

    %% Internal Flow Steps
    HASFILES{Has Files?}:::decisionClass
    STEP1A[Multimodal Path<br/>Vision analysis]:::stepClass
    STEP1B[Text-only Path<br/>Conversation]:::stepClass
    STEP2[Build Messages<br/>+ History context]:::stepClass
    STEP3[Generate Response<br/>Natural language]:::stepClass
    RESPONSE([Response: Chat answer])

    %% Main Flow
    START --> ORCH

    %% Service calls
    ORCH ==>|Classify| CLASS
    CLASS -.->|CHAT| ORCH

    ORCH ==>|LLM Call| COREGW
    COREGW ==> LLM

    %% Internal flow
    ORCH -.-> HASFILES
    HASFILES -.Has Files.-> STEP1A
    HASFILES -.Text Only.-> STEP1B

    STEP1A -.-> STEP2
    STEP1B -.-> STEP2
    STEP2 -.-> STEP3
    STEP3 -.-> RESPONSE

    %% Layout
    START --> ORCH --> HASFILES
    HASFILES -->|Yes| STEP1A
    HASFILES -->|No| STEP1B
    STEP1A --> STEP2
    STEP1B --> STEP2
    STEP2 --> STEP3
    STEP3 --> RESPONSE
```

**Flow Description:**
1. **Orchestrator calls Classification** → Intent: `CHAT`
2. **Decision**: Has files (images)?
   - **YES** → Multimodal path (vision analysis with GPT-4o)
   - **NO** → Text-only path (conversation with GPT-4o-mini)
3. **Internal Steps** (dashed):
   - Build messages with conversation history
   - Call Core Gateway → LLM
   - Generate natural language response
4. **Return** chat response

---

## Service Communication Matrix

| From | To | Line Type | Purpose |
|------|----|-----------| --------|
| Orchestrator | Classification | **Solid** | Intent detection for all cases |
| Orchestrator | Extraction | **Solid** | Extract attributes (POST, SEARCH, PRICE) |
| Orchestrator | Completeness | **Solid** | Assess listing quality (POST) |
| Orchestrator | DB Gateway | **Solid** | Search/save operations |
| Orchestrator | Core Gateway | **Solid** | LLM calls (CHAT, response generation) |
| Orchestrator | Semantic Chunking | **Solid** | Text preprocessing (if needed) |
| Orchestrator | Reranking | **Solid** | Optimize search results (SEARCH) |
| Orchestrator | Price Suggestion | **Solid** | Price analysis (PRICE - future) |
| **Internal Steps** | **Within Case** | **Dashed** | Processing logic before response |

---

## Layer Architecture Summary

```mermaid
graph TB
    %% Styling
    classDef layer0 fill:#90EE90,stroke:#333,stroke-width:2px
    classDef layer2 fill:#FFD700,stroke:#333,stroke-width:3px
    classDef layer3 fill:#FFEB99,stroke:#333,stroke-width:2px
    classDef layer4 fill:#B0E0B0,stroke:#333,stroke-width:2px
    classDef layer5 fill:#FFB366,stroke:#333,stroke-width:2px

    subgraph Layer0[Layer 0: Frontend]
        USER[User]:::layer0
        WEBUI[Open WebUI]:::layer0
    end

    subgraph Layer2[Layer 2: Orchestration]
        ORCH[Orchestrator<br/>Central Routing]:::layer2
    end

    subgraph Layer3[Layer 3: AI Services]
        CLASS[Classification]:::layer3
        EXTRACT[Extraction]:::layer3
        COMPLETE[Completeness]:::layer3
        CHUNK[Semantic Chunking]:::layer3
        RERANK[Reranking]:::layer3
        PRICE[Price Suggestion]:::layer3
    end

    subgraph Layer4[Layer 4: Storage]
        DBGW[DB Gateway]:::layer3
        POSTGRES[(PostgreSQL)]:::layer4
        OPENSEARCH[(OpenSearch)]:::layer4
    end

    subgraph Layer5[Layer 5: LLM Gateway]
        COREGW[Core Gateway]:::layer5
        LLM[Ollama / OpenAI]:::layer5
    end

    %% Connections
    USER --> WEBUI
    WEBUI ==> ORCH

    %% Orchestrator to Layer 3 (Only solid lines from Orchestrator)
    ORCH ==> CLASS
    ORCH ==> EXTRACT
    ORCH ==> COMPLETE
    ORCH ==> CHUNK
    ORCH ==> RERANK
    ORCH ==> PRICE

    %% Orchestrator to Layer 4
    ORCH ==> DBGW
    DBGW --> POSTGRES
    DBGW --> OPENSEARCH

    %% Orchestrator to Layer 5
    ORCH ==> COREGW
    COREGW --> LLM
```

**Key Design Principle (CTO Requirement):**
- ✅ **Only Orchestrator** communicates with Layer 3 services (solid lines)
- ✅ **No cross-service calls** within Layer 3
- ✅ **Internal processing steps** within each case flow use dashed vertical lines
- ✅ **Storage layer** services can communicate with databases (dashed boxes)

---

## Implementation Checklist

### ✅ Currently Implemented
- [x] Case 1: Property Posting (POST_SALE, POST_RENT)
- [x] Case 2: Property Search (SEARCH_BUY, SEARCH_RENT)
- [x] Case 4: General Chat (CHAT)
- [x] Orchestrator → All Layer 3 services (solid lines)
- [x] ReAct Agent pattern with progressive relaxation
- [x] Multimodal support (vision analysis)

### ⚠️ To Be Implemented
- [ ] Case 3: Price Consultation (PRICE_CONSULTATION)
  - [ ] Add intent to Classification Service
  - [ ] Add routing logic in Orchestrator
  - [ ] Create `_handle_price_consultation()` method
  - [ ] Integrate with Price Suggestion Service

---

**Document Version:** 1.0
**Last Updated:** 2025-01-12
**Related Documents:**
- `ORCHESTRATOR_FLOWS.md` - Detailed flow documentation
- `CLAUDE.md` - Project overview
