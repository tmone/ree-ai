# Price Consultation Service - Quick Summary

## 📋 Yêu cầu từ Orchestrator Team

**Team của bạn cần build:** Microservice tư vấn giá bất động sản

---

## 🎯 Nhiệm vụ

Build service **độc lập** xử lý:
- Input: Thông tin BĐS (loại, diện tích, vị trí, số phòng)
- Output: Phân tích giá (trung bình, min, max, xu hướng, confidence)

---

## 🔌 API Contract

### **Endpoint chính:**
```
POST http://your-service:8087/api/v1/price-consultation
```

**Request cần:**
```json
{
  "property_info": {
    "property_type": "apartment",
    "bedrooms": 2,
    "district": "District 2",
    "area": 80.0
  },
  "user_query": "Căn hộ 2PN Quận 2 giá bao nhiêu?",
  "language": "vi"
}
```

**Response trả về:**
```json
{
  "success": true,
  "data": {
    "price_analysis": {
      "average_price": 5200000000,
      "min_price": 4500000000,
      "max_price": 6800000000,
      "price_per_sqm": 65000000
    },
    "confidence": {
      "score": 0.85,
      "level": "high"
    },
    "market_data": {
      "sample_count": 12
    }
  }
}
```

---

## 📊 Data Source

**OpenSearch** có sẵn tại `opensearch:9200`

Index: `properties`

Query ví dụ:
```bash
curl http://opensearch:9200/properties/_search \
  -d '{"query": {"match": {"district": "District 2"}}}'
```

---

## 🚀 Tech Stack Gợi ý

- **Language:** Python 3.10+
- **Framework:** FastAPI
- **Port:** 8087
- **Docker:** Chạy trong `ree-ai-network`

---

## 📦 Deliverables

1. **Code:**
   - `services/price_consultation_service/main.py`
   - `services/price_consultation_service/Dockerfile`
   - `services/price_consultation_service/requirements.txt`

2. **Integration:**
   - Add service vào `docker-compose.yml`
   - Expose port 8087

3. **Documentation:**
   - README với examples
   - API usage guide

---

## ✅ Acceptance Criteria

- [ ] Endpoint `/api/v1/price-consultation` hoạt động
- [ ] Response time < 3 giây
- [ ] Confidence score 0.0-1.0 hợp lý
- [ ] OpenSearch integration OK
- [ ] Health check endpoint
- [ ] Docker build thành công
- [ ] Chạy được trong docker-compose

---

## 📄 Chi tiết đầy đủ

Xem file: **PRICE_CONSULTATION_SERVICE_SPEC.md**

Test request mẫu: **example_price_consultation_request.json**

---

## 📞 Liên hệ

- **Slack:** #ree-ai-orchestrator
- **Questions:** Create GitHub issue tag `integration/price-consultation`

---

## ⏱️ Timeline

- **Week 1-2:** Build service + OpenSearch integration
- **Week 3:** Testing, Docker setup
- **Week 4:** Integration với orchestrator, deploy staging

---

**Bắt đầu:** Đọc `PRICE_CONSULTATION_SERVICE_SPEC.md` để biết API contract chi tiết!
