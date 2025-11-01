# Fix: Open WebUI Không Có Model Để Chọn

## Vấn Đề
Bạn mở http://localhost:3000, đăng nhập OK, nhưng không có model nào trong dropdown để chọn → không gửi message được.

## Giải Pháp: Add OpenAI Connection Thủ Công

### Bước 1: Vào Admin Settings

1. Mở http://localhost:3000
2. Đăng nhập
3. Click vào **avatar/icon** ở góc trên bên phải
4. Chọn **"Admin Panel"** (hoặc "Settings")

### Bước 2: Add OpenAI Connection

1. Trong Admin Panel, tìm **"Connections"** hoặc **"External Connections"**
2. Hoặc tìm **"Settings" → "Connections" → "OpenAI"**
3. Click **"Add OpenAI Connection"** hoặc **"+"**

### Bước 3: Nhập Thông Tin

Điền các thông tin sau:

**API Base URL:**
```
http://orchestrator:8080/v1
```

**API Key:**
```
dummy-key-not-needed
```
(hoặc bất kỳ text nào, vì orchestrator không check key)

**Name/Label:** (optional)
```
REE AI Orchestrator
```

### Bước 4: Save và Verify

1. Click **"Save"** hoặc **"Add"**
2. Open WebUI sẽ fetch models từ `http://orchestrator:8080/v1/models`
3. Quay lại chat interface
4. Bây giờ dropdown **"Select a model"** sẽ có **"ree-ai-assistant"**

---

## Nếu Không Tìm Thấy "Connections" Setting

### Alternative 1: Environment Variable (Đã Set)

Check xem có đúng không:
```bash
docker exec ree-ai-open-webui env | grep OPENAI
```

Kết quả mong đợi:
```
OPENAI_API_BASE_URL=http://orchestrator:8080
OPENAI_API_KEY=dummy-key-not-needed
ENABLE_OPENAI_API=true
```

Nếu đúng nhưng vẫn không có model → cần restart:
```bash
docker-compose restart open-webui
```

### Alternative 2: Check Open WebUI Version

Có thể version của Open WebUI yêu cầu thêm config khác.

Xem logs:
```bash
docker logs ree-ai-open-webui --tail 100 | grep -i "openai\|model"
```

---

## Nếu Vẫn Không Được

### Quick Fix: Dùng Python Script Test

Thay vì dùng Open WebUI, test ReAct Agent trực tiếp qua script:

```bash
cd /Users/tmone/ree-ai
python3 test_react_manual.py --quick
```

Cái này sẽ test ReAct Agent ngay lập tức mà không cần UI.

---

## Debug: Check Models API Từ Browser

Mở browser console (F12) và gõ:

```javascript
fetch('http://localhost:8090/v1/models')
  .then(r => r.json())
  .then(d => console.log(d))
```

Nếu thấy CORS error → cần config CORS cho orchestrator.

---

## Tôi Cần Thông Tin Thêm

Để giúp bạn tốt hơn, bạn có thể:

1. **Screenshot** dropdown model trong Open WebUI (nếu có)
2. **Screenshot** Admin Panel → Connections (nếu tìm thấy)
3. Hoặc cho tôi biết Open WebUI version:
   ```bash
   docker logs ree-ai-open-webui --tail 5 | head -20
   ```

Tôi sẽ fix chính xác hơn!
