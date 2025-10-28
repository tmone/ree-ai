# 🎨 Cách Xem Diagram Architecture

## File Diagram Mới: `REE_AI-CTO-Architecture.drawio.xml`

Đây là diagram THEO SƠ ĐỒ GỐC CTO với:
- ✅ 10 Services
- ✅ Core Gateway + Model Routing (Ollama/OpenAI)
- ✅ TRẢ LỜI 4 câu hỏi CTO (Q1, Q2, Q3, Q4)
- ✅ Platform mapping chi tiết

---

## 🌐 Cách 1: Xem Online (Khuyến nghị)

### Bước 1: Mở draw.io
https://app.diagrams.net

### Bước 2: Chọn "Open Existing Diagram"
- Click **File** → **Open from** → **Device**
- Chọn file: `REE_AI-CTO-Architecture.drawio.xml`

### Bước 3: Xem diagram
- Zoom in/out bằng mouse wheel
- Click vào từng layer để xem chi tiết
- Export sang PNG/PDF nếu cần

---

## 💻 Cách 2: Xem trong VS Code

### Bước 1: Install Extension
```bash
# Trong VS Code:
# 1. Mở Extensions (Ctrl+Shift+X)
# 2. Search "Draw.io Integration"
# 3. Install extension by "hediet.vscode-drawio"

# Hoặc dùng command line:
code --install-extension hediet.vscode-drawio
```

### Bước 2: Mở file
```bash
# Click vào file trong VS Code
REE_AI-CTO-Architecture.drawio.xml

# Hoặc:
code REE_AI-CTO-Architecture.drawio.xml
```

### Bước 3: Edit (optional)
- Extension cho phép edit trực tiếp trong VS Code
- Save → File tự động update

---

## 📱 Cách 3: Xem trên Desktop App

### Bước 1: Download draw.io Desktop
https://github.com/jgraph/drawio-desktop/releases

### Bước 2: Install
- Windows: Download `.exe` installer
- Mac: Download `.dmg`
- Linux: Download `.AppImage`

### Bước 3: Mở file
- File → Open
- Chọn `REE_AI-CTO-Architecture.drawio.xml`

---

## 🎯 Nội Dung Diagram

### Layer 1: User Account Service
- FastAPI + PostgreSQL + JWT
- Register, Login, User management

### Layer 2: Orchestrator
- FastAPI + gRPC
- Message routing: create RE / search RE / price
- **Q2 ANSWER:** Gen conversation_id (UUID)

### Layer 3: 10 Services
1. **Semantic Chunking** (Sentence-Transformers) - 6 steps CTO
2. **Attribute Extraction** (🟢 Ollama llama3.1:8b) - LLM-driven
3. **Classification** (🟢 Ollama llama3.1:8b) - 3 modes
4. **Completeness Feedback** (🔵 OpenAI GPT-4 mini) - Score 0-100
5. **Price Suggestion** (🔵 OpenAI GPT-4 mini) - Market analysis
6. **Rerank** (cross-encoder) - FREE
7. **Core Gateway** ⭐ **Q3 ANSWER**
   - LiteLLM + Redis + Ollama
   - Rate limiting, Cost tracking, Model routing
   - 10% cost savings

### Layer 4: Storage
- **OpenSearch** (Vector DB + BM25)
- **PostgreSQL** (Context Memory) - **Q1, Q4 ANSWER**
  - Users, Conversations, Messages
  - Load history → Inject to prompt
- **Redis** (Cache, Rate limit, Queue)

### Layer 5: Data Ingestion
- **Crawl4AI** + Playwright
- nhatot.vn, batdongsan.vn
- 73% less code, 47% faster vs Scrapy

### Layer 6: External LLM
- **Ollama** (Self-hosted) - llama3.1:8b, 70b - FREE
- **OpenAI API** - GPT-4 mini, embeddings - $$

### Legend: 4 CÂU HỎI CTO
- Q1: Context Memory → PostgreSQL + conversation_id
- Q2: User mapping → Orchestrator gen UUID
- Q3: Core Service → YES (LiteLLM + Ollama routing)
- Q4: History → Load PostgreSQL → Inject prompt

---

## 🖼️ Export Diagram

### Export to PNG (high resolution):
1. File → Export as → PNG
2. Settings:
   - ✅ Transparent Background
   - ✅ Include grid: OFF
   - ✅ Zoom: 200% (for high quality)
   - ✅ Border: 10px

### Export to PDF:
1. File → Export as → PDF
2. Settings:
   - ✅ All pages
   - ✅ Fit to: 1 page width

### Export to SVG (vector):
1. File → Export as → SVG
2. Best for presentations (scalable)

---

## 📊 So Sánh 2 Diagrams

| Feature | REE_AI-CTO-Architecture.drawio.xml | REE_AI-OpenWebUI-Complete-Architecture.drawio.xml |
|---------|-----------------------------------|--------------------------------------------------|
| **Theo sơ đồ CTO** | ✅ YES | ❌ NO (theo Open WebUI) |
| **10 Services** | ✅ | ❌ (chỉ 4 services) |
| **Core Gateway** | ✅ | ❌ (chỉ có Gateway warning) |
| **Model Routing** | ✅ (Ollama/OpenAI) | ❌ |
| **Q1, Q2, Q3, Q4** | ✅ Trả lời đầy đủ | ⚠️ Auto-solved (không rõ) |
| **Orchestrator** | ✅ | ❌ (dùng LangChain Pipeline) |
| **User Account Service** | ✅ Riêng biệt | ❌ (gộp trong Open WebUI) |
| **Semantic Chunking** | ✅ 6 steps | ❌ (Crawl4AI chunking) |
| **Completeness Feedback** | ✅ | ❌ |
| **Classification 3 modes** | ✅ | ❌ (chỉ Intent Classification) |

**Kết luận:** Dùng **`REE_AI-CTO-Architecture.drawio.xml`** cho CTO review!

---

## 🔄 Update Diagram (nếu cần)

### Nếu CTO yêu cầu thay đổi:

1. Mở file trong draw.io/VS Code
2. Edit components
3. Save
4. Commit git:
```bash
git add docs/REE_AI-CTO-Architecture.drawio.xml
git commit -m "Update CTO architecture diagram"
```

### Tips:
- Giữ màu sắc consistent (mỗi layer 1 màu)
- Font size: Title 24-32, Service 14-16, Description 11-12
- Arrows: Solid = data flow, Dashed = reference
- Use emoji để highlight: ⭐ ✅ ❌ 🟢 🔵

---

## 📝 Print cho Meeting

### Recommended settings:
- **Paper:** A3 landscape (297 x 420 mm)
- **Scale:** Fit to 1 page
- **Color:** Yes (color printer)
- **Quality:** High (600 DPI)

### Nếu chỉ có A4:
- Export PDF → Print 2 pages
- Hoặc print at 70% scale (fit to 1 page nhưng nhỏ)

---

**Created:** 2025-10-29
**Diagram file:** `REE_AI-CTO-Architecture.drawio.xml`
**Size:** 27KB
**Layers:** 6 (User, Orchestrator, Services, Storage, Crawler, External)
