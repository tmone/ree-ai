# ReAct Agent Clarification V2 - Intelligent & Helpful

## User Feedback (Excellent!)

**Problem with V1 Response:**
```
"Tìm được 5 BDS, nhưng chỉ 0 BDS phù hợp (0%).

Vấn đề:
- Không đủ BDS ở quận 2
- Không đủ BDS có 3 phòng ngủ
- Thiếu: gần trường quốc tế"
```

**Issues:**
- ❌ Too "cold" and "negative"
- ❌ No context about total available properties
- ❌ Just lists problems, doesn't offer alternatives
- ❌ Misses opportunity to help user

---

## Improved V2 Response

**New Approach:**
```
"Tôi tìm thấy **150 căn hộ** ở TP.HCM, nhưng **không có căn nào ở quận 2**.

**Bạn muốn tôi:**
- 🔍 Tìm thêm ở **các quận lân cận** (Quận 9, Thủ Đức, Bình Thạnh)
- 🌍 Mở rộng tìm kiếm **toàn TP.HCM**
- 📍 Cung cấp thông tin cụ thể hơn về "gần trường quốc tế"
- 🛏️ Điều chỉnh số phòng ngủ (3 ± 1 phòng)

**Dưới đây là 5 BĐS gần nhất có thể phù hợp:**

1. 🟡 **Căn hộ 3PN Vinhomes Central Park** (Điểm: 45/100)
   💰 Giá: 5.5 tỷ | 📐 92m² | 🛏️ 3 PN
   📍 Bình Thạnh (cách Quận 2 chỉ 5km)

2. 🟡 **Căn hộ Vista Verde 3PN** (Điểm: 42/100)
   💰 Giá: 4.8 tỷ | 📐 88m² | 🛏️ 3 PN
   📍 Thủ Đức (kế Quận 2)

...

💬 Bạn muốn tôi hỗ trợ như thế nào?"
```

**Benefits:**
- ✅ Data-driven (shows total: 150 căn hộ ở TP.HCM)
- ✅ Proactive options (expand search, adjust criteria)
- ✅ Shows alternatives with scoring (best matches first)
- ✅ Visual cards (emoji indicators, structured info)
- ✅ Helpful, not just "sorry, no results"

---

## Technical Implementation

### New Method: `_calculate_match_score()`

**Scoring System (0-100 points):**
- **District match: 40 points**
  - Exact match: 40 points
  - Partial match: 20 points
- **Bedrooms match: 30 points**
  - Exact match: 30 points
  - ±1 bedroom: 15 points
- **Property type match: 15 points**
- **Price in range: 15 points**
  - Within budget: 15 points
  - Within 20% over: 7 points

**Code:**
```python
def _calculate_match_score(self, prop: Dict, requirements: Dict) -> int:
    score = 0

    # District match (40 points)
    if requirements.get("district"):
        required_district = requirements["district"].lower()
        prop_district = str(prop.get("district", "")).lower()

        import re
        required_num = re.search(r'\d+', required_district)
        prop_num = re.search(r'\d+', prop_district)

        if required_num and prop_num and required_num.group() == prop_num.group():
            score += 40  # Exact match
        elif required_district in prop_district or prop_district in required_district:
            score += 20  # Partial match

    # Bedrooms match (30 points)
    if requirements.get("bedrooms"):
        prop_bedrooms = prop.get("bedrooms") or prop.get("bedroom")
        if prop_bedrooms:
            try:
                required_br = int(requirements["bedrooms"])
                prop_br = int(prop_bedrooms)

                if required_br == prop_br:
                    score += 30  # Exact
                elif abs(required_br - prop_br) == 1:
                    score += 15  # ±1 bedroom
            except:
                pass

    # Property type match (15 points)
    # Price in range (15 points)
    ...

    return min(100, score)
```

---

### Improved `_ask_clarification()` with Alternatives

**Features:**
1. **Statistics from DB**
   - Total properties in city
   - Total in specific district
   - Shows context: "150 căn hộ ở TP.HCM, nhưng không có ở quận 2"

2. **Proactive Suggestions**
   - Nearby districts (geographic mapping)
   - Expand to whole city
   - Clarify special requirements
   - Adjust bedroom count (±1)

3. **Scored Alternatives**
   - Calculate match score for all results
   - Sort by score (best first)
   - Show top 5 with scores
   - Visual indicators:
     - 🟢 Good match (≥70%)
     - 🟡 Partial match (40-69%)
     - 🔴 Poor match (<40%)

4. **Structured Cards**
   ```
   1. 🟡 **Title** (Điểm: 45/100)
      💰 Giá: X | 📐 Ym² | 🛏️ Z PN
      📍 Location
   ```

**Code:**
```python
async def _ask_clarification(self, requirements: Dict, evaluation: Dict, results: List[Dict] = None) -> str:
    # Get statistics
    stats = await self._get_property_statistics(requirements)

    # Calculate scores for all results
    scored_results = []
    if results:
        for prop in results:
            score = self._calculate_match_score(prop, requirements)
            scored_results.append({"property": prop, "score": score})
        scored_results.sort(key=lambda x: x["score"], reverse=True)

    # Build response
    response_parts = []

    # Part 1: Statistics
    response_parts.append(
        f"Tôi tìm thấy **{stats['total_in_city']} {property_type}** ở {city}, "
        f"nhưng **không có căn nào ở {district}**."
    )

    # Part 2: Proactive Options
    response_parts.append("\n\n**Bạn muốn tôi:**\n")
    nearby_districts = self._get_nearby_districts(district)
    response_parts.append(
        f"- 🔍 Tìm thêm ở **các quận lân cận** ({', '.join(nearby_districts[:3])})\n"
        f"- 🌍 Mở rộng tìm kiếm **toàn {city}**\n"
        ...
    )

    # Part 3: Top 5 Alternatives
    for i, item in enumerate(scored_results[:5]):
        prop = item["property"]
        score = item["score"]
        match_indicator = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"

        response_parts.append(
            f"\n{i + 1}. {match_indicator} **{title}** (Điểm: {score}/100)\n"
            f"   💰 Giá: {price} | 📐 {area}m² | 🛏️ {bedrooms} PN\n"
            f"   📍 {location}\n"
        )

    return "".join(response_parts)
```

---

### Helper Methods

**1. `_get_property_statistics()`**
- Query DB Gateway for totals
- Returns: `total_in_city`, `total_in_district`
- Currently mock data (TODO: integrate real stats)

**2. `_get_nearby_districts()`**
- Geographic mapping of nearby districts
- Example: quận 2 → [Quận 9, Thủ Đức, Bình Thạnh]
- Hardcoded map for now (can improve with geo data)

---

## Before vs After Comparison

| Aspect | V1 (Old) | V2 (New - Improved) |
|--------|----------|---------------------|
| **Tone** | "Cold", negative | Helpful, proactive |
| **Context** | None | "150 căn hộ ở TP.HCM" |
| **Alternatives** | None | Top 5 with scores |
| **Suggestions** | Generic | Specific (nearby districts) |
| **Visual** | Plain text | Cards with emojis |
| **UX** | Disappointing | Engaging, helpful |

---

## Example Responses

### Scenario 1: No Exact Match in District

**Query:** "Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế"

**V2 Response:**
```
Tôi tìm thấy **150 căn hộ** ở TP.HCM, nhưng **không có căn nào ở quận 2**.

**Bạn muốn tôi:**
- 🔍 Tìm thêm ở **các quận lân cận** (Quận 9, Thủ Đức, Bình Thạnh)
- 🌍 Mở rộng tìm kiếm **toàn TP.HCM**
- 📍 Cung cấp thông tin cụ thể hơn về "gần trường quốc tế"
- 🛏️ Điều chỉnh số phòng ngủ (3 ± 1 phòng)

**Dưới đây là 5 BĐS gần nhất có thể phù hợp:**

1. 🟡 **Căn hộ The Sun Avenue 3PN** (Điểm: 45/100)
   💰 Giá: 4.5 tỷ | 📐 90m² | 🛏️ 3 PN
   📍 Bình Thạnh

2. 🟡 **Căn hộ Masteri Thảo Điền** (Điểm: 43/100)
   💰 Giá: 5.2 tỷ | 📐 85m² | 🛏️ 3 PN
   📍 Quận 2 (chính xác!)

...

💬 Bạn muốn tôi hỗ trợ như thế nào?
```

---

### Scenario 2: Few Matches, Adjust Criteria

**Query:** "Tìm biệt thự dưới 10 tỷ ở quận 1"

**V2 Response:**
```
Tôi tìm thấy **45 biệt thự** ở TP.HCM, trong đó có **12 căn** ở quận 1.
Nhưng chỉ có **1 căn** phù hợp với ngân sách dưới 10 tỷ.

**Bạn muốn tôi:**
- 💰 Mở rộng ngân sách (10-15 tỷ để có thêm lựa chọn)
- 🔍 Tìm ở **các quận lân cận** (Quận 3, Quận 4, Quận 5)
- 🏘️ Xem **nhà phố** thay vì biệt thự (nhiều lựa chọn hơn)

**Dưới đây là 5 BĐS gần nhất có thể phù hợp:**

1. 🟢 **Biệt thự mini Quận 1** (Điểm: 85/100)
   💰 Giá: 9.5 tỷ | 📐 120m² | 🛏️ 4 PN
   📍 Quận 1

2. 🟡 **Biệt thự Thảo Điền** (Điểm: 55/100)
   💰 Giá: 12 tỷ | 📐 200m² | 🛏️ 5 PN
   📍 Quận 2 (20% over budget)

...
```

---

## Future Improvements

### 1. Real Statistics from DB
```python
async def _get_property_statistics(self, requirements: Dict) -> Dict:
    # Call DB Gateway API
    response = await self.http_client.post(
        f"{self.db_gateway_url}/statistics",
        json={
            "property_type": requirements.get("property_type"),
            "city": requirements.get("city"),
            "district": requirements.get("district")
        }
    )
    return response.json()
```

### 2. Geographic Data for Nearby Districts
- Use geo database with coordinates
- Calculate actual distance
- Sort by proximity
- Current: hardcoded map

### 3. Machine Learning Score Weights
- Learn from user interactions
- Adjust weights based on user feedback
- Personalize scoring per user

### 4. Image Cards (if UI supports)
- Show property images
- Interactive cards with "View Details" button
- Map with location markers

---

## Impact

**User Experience:**
- **Before:** Frustrated ("system said no results, useless")
- **After:** Engaged ("system shows alternatives, helpful!")

**Conversion:**
- **Before:** User leaves after "no results"
- **After:** User explores alternatives → higher engagement

**Trust:**
- **Before:** "System doesn't understand my needs"
- **After:** "System tries to help me find best match"

---

## Conclusion

V2 clarification transforms ReAct Agent from:
- ❌ "Sorry, no results" dead-end
- ✅ "Here are alternatives + options" helpful assistant

**This is the difference between:**
- A search engine (cold, mechanical)
- An AI assistant (warm, intelligent, helpful)

**Next:** Test with real users and iterate based on feedback!
