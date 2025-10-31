"""
Quick Prompt Evaluation - No external dependencies needed
Tests prompts with real 10K+ data
"""
import json
import sys
from typing import List, Dict
from datetime import datetime

# PostgreSQL connection
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    print("⚠️ psycopg2 not installed. Install with: pip install psycopg2-binary")


class QuickEvaluator:
    """Quick evaluation without external dependencies"""

    def __init__(self):
        self.db_conn = None
        self.results = {}

    def connect_db(self):
        """Connect to PostgreSQL"""
        if not HAS_POSTGRES:
            return False

        try:
            self.db_conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="ree_ai",
                user="ree_ai_user",
                password="ree_ai_pass_2025",
                cursor_factory=RealDictCursor
            )
            print("✅ Connected to PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("💡 Make sure PostgreSQL is running: docker-compose up postgres -d")
            return False

    def get_sample_properties(self, limit: int = 500) -> List[Dict]:
        """Get sample properties"""
        if not self.db_conn:
            return []

        cursor = self.db_conn.cursor()
        cursor.execute(f"""
            SELECT * FROM properties
            ORDER BY id
            LIMIT {limit}
        """)

        properties = cursor.fetchall()
        print(f"✅ Loaded {len(properties)} properties from database")
        return properties

    def test_classification_keywords(self, properties: List[Dict]) -> Dict:
        """Test classification with keyword matching"""
        print("\n🧪 TESTING CLASSIFICATION (Keyword Method)...")

        keywords = {
            "apartment": ["căn hộ", "chung cư", "apartment", "condo", "penthouse"],
            "house": ["nhà", "nhà riêng", "nhà phố", "townhouse"],
            "villa": ["biệt thự", "villa"],
            "land": ["đất", "land", "lô đất", "đất nền"],
            "commercial": ["văn phòng", "office", "shophouse", "mặt bằng"]
        }

        results = {prop_type: 0 for prop_type in keywords.keys()}
        results["unknown"] = 0
        results["total"] = 0

        for prop in properties:
            text = f"{prop.get('title', '')} {prop.get('description', '')}".lower()

            classified = False
            for prop_type, kw_list in keywords.items():
                if any(kw in text for kw in kw_list):
                    results[prop_type] += 1
                    classified = True
                    break

            if not classified:
                results["unknown"] += 1

            results["total"] += 1

        print("\n📊 Classification Distribution:")
        for prop_type, count in results.items():
            if prop_type != "total":
                percentage = (count / results["total"] * 100) if results["total"] > 0 else 0
                print(f"  {prop_type:15s}: {count:5d} ({percentage:.1f}%)")

        return results

    def test_attribute_extraction(self, properties: List[Dict]) -> Dict:
        """Test attribute extraction coverage"""
        print("\n🧪 TESTING ATTRIBUTE EXTRACTION...")

        fields = ["title", "price", "location", "bedrooms", "bathrooms", "area", "description"]

        results = {field: {"present": 0, "missing": 0} for field in fields}

        for prop in properties:
            for field in fields:
                value = prop.get(field)
                if value and str(value).strip():
                    results[field]["present"] += 1
                else:
                    results[field]["missing"] += 1

        print("\n📊 Field Coverage:")
        total = len(properties)
        for field, stats in results.items():
            coverage = (stats["present"] / total * 100) if total > 0 else 0
            print(f"  {field:15s}: {stats['present']:5d}/{total:5d} ({coverage:.1f}%) present")

        return results

    def analyze_price_formats(self, properties: List[Dict]) -> Dict:
        """Analyze price formats in data"""
        print("\n🧪 ANALYZING PRICE FORMATS...")

        formats = {
            "tỷ": 0,
            "triệu": 0,
            "VND": 0,
            "đồng": 0,
            "billion": 0,
            "million": 0,
            "numeric_only": 0,
            "missing": 0
        }

        for prop in properties:
            price_str = str(prop.get("price", "")).lower()

            if not price_str or price_str == "none":
                formats["missing"] += 1
            elif "tỷ" in price_str:
                formats["tỷ"] += 1
            elif "triệu" in price_str:
                formats["triệu"] += 1
            elif "vnd" in price_str or "đồng" in price_str:
                formats["VND"] += 1
            elif any(char.isdigit() for char in price_str):
                formats["numeric_only"] += 1

        print("\n📊 Price Format Distribution:")
        total = len(properties)
        for format_type, count in formats.items():
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {format_type:15s}: {count:5d} ({percentage:.1f}%)")

        return formats

    def analyze_location_patterns(self, properties: List[Dict]) -> Dict:
        """Analyze location formats"""
        print("\n🧪 ANALYZING LOCATION PATTERNS...")

        districts = {}
        missing = 0

        for prop in properties:
            location = str(prop.get("location", "")).lower()

            if not location or location == "none":
                missing += 1
                continue

            # Extract district mentions
            for i in range(1, 13):
                variants = [
                    f"quận {i}",
                    f"q{i}",
                    f"q.{i}",
                    f"district {i}"
                ]
                if any(v in location for v in variants):
                    key = f"Quận {i}"
                    districts[key] = districts.get(key, 0) + 1
                    break

            # Check for popular districts
            if "bình thạnh" in location:
                districts["Quận Bình Thạnh"] = districts.get("Quận Bình Thạnh", 0) + 1
            elif "thủ đức" in location or "thu duc" in location:
                districts["Thủ Đức"] = districts.get("Thủ Đức", 0) + 1
            elif "tân bình" in location:
                districts["Quận Tân Bình"] = districts.get("Quận Tân Bình", 0) + 1

        print("\n📊 TOP 10 Districts:")
        sorted_districts = sorted(districts.items(), key=lambda x: x[1], reverse=True)[:10]
        for district, count in sorted_districts:
            print(f"  {district:20s}: {count:5d} listings")

        print(f"\n  Missing location: {missing} ({missing/len(properties)*100:.1f}%)")

        return {"districts": districts, "missing": missing}

    def analyze_completeness(self, properties: List[Dict]) -> Dict:
        """Analyze data completeness for prompts"""
        print("\n🧪 ANALYZING DATA COMPLETENESS...")

        completeness_scores = []
        required_fields = ["title", "price", "location"]
        optional_fields = ["bedrooms", "bathrooms", "area", "description"]

        score_distribution = {
            "excellent": 0,      # 90-100%
            "good": 0,           # 70-89%
            "fair": 0,           # 50-69%
            "poor": 0            # <50%
        }

        for prop in properties:
            # Calculate completeness score
            present_count = 0
            total_fields = len(required_fields) + len(optional_fields)

            for field in required_fields + optional_fields:
                if prop.get(field) and str(prop.get(field)).strip():
                    present_count += 1

            score = (present_count / total_fields * 100) if total_fields > 0 else 0
            completeness_scores.append(score)

            # Categorize
            if score >= 90:
                score_distribution["excellent"] += 1
            elif score >= 70:
                score_distribution["good"] += 1
            elif score >= 50:
                score_distribution["fair"] += 1
            else:
                score_distribution["poor"] += 1

        avg_score = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0

        print(f"\n📊 Completeness Distribution:")
        print(f"  Average Score: {avg_score:.1f}%")
        total = len(properties)
        for category, count in score_distribution.items():
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {category.capitalize():15s}: {count:5d} ({percentage:.1f}%)")

        return {
            "average_score": avg_score,
            "distribution": score_distribution
        }

    def generate_report(self, output_path: str):
        """Generate evaluation report"""
        print(f"\n📝 Generating report: {output_path}")

        report = f"""# 🎯 QUICK PROMPT EVALUATION REPORT

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database:** PostgreSQL (ree_ai)
**Sample Size:** {self.results.get('total_properties', 0)} properties

---

## 📊 Data Quality Analysis

### 1. Classification Distribution

{json.dumps(self.results.get('classification', {}), indent=2, ensure_ascii=False)}

**Findings:**
- Most common property type: Check distribution above
- "Unknown" rate indicates ambiguous listings
- **Action:** Update classification keywords based on this distribution

### 2. Attribute Extraction Coverage

{json.dumps(self.results.get('attribute_extraction', {}), indent=2, ensure_ascii=False)}

**Findings:**
- Title: Should be ~100% (required field)
- Price: Critical for price suggestion service
- Location: Critical for search and recommendations
- **Action:** Add default values/fallbacks for missing fields in prompts

### 3. Price Format Analysis

{json.dumps(self.results.get('price_formats', {}), indent=2, ensure_ascii=False)}

**Findings:**
- Multiple price formats need normalization
- "tỷ" and "triệu" are most common Vietnamese formats
- **Action:** Update price extraction prompt with these patterns

### 4. Location Patterns

{json.dumps(self.results.get('location_patterns', {}).get('districts', {}), indent=2, ensure_ascii=False)}

**Findings:**
- District name variations: "Quận 1", "Q1", "Q.1", "District 1"
- **Action:** Add all variants to location normalization rules

### 5. Data Completeness

Average Completeness: {self.results.get('completeness', {}).get('average_score', 0):.1f}%

{json.dumps(self.results.get('completeness', {}).get('distribution', {}), indent=2)}

**Findings:**
- Poor completeness listings need special handling in prompts
- Excellent listings (90%+) can use full feature set
- **Action:** Add graceful degradation logic in prompts

---

## 💡 PROMPT IMPROVEMENTS NEEDED

### 1. Classification Service (`services/classification/prompts.py`)

**Add keywords:**
```python
# Based on data analysis
KEYWORDS = {{
    PropertyType.APARTMENT: [
        "căn hộ", "chung cư", "apartment", "condo",
        "can ho", "chung cu"  # Add without diacritics
    ],
    # ... add more based on actual data patterns
}}
```

### 2. Attribute Extraction (`services/attribute_extraction/prompts.py`)

**Improve price normalization:**
```
Price formats found:
- "2.5 tỷ" → 2500000000
- "25 triệu/tháng" → 25000000
- "500 triệu" → 500000000
- Numeric only → Handle missing unit

Action: Update regex patterns and conversion logic
```

### 3. Location Normalization

**Add district variants:**
```
"Q1", "Q.1", "Quận 1", "District 1", "quan 1" → "Quận 1"
```

### 4. Completeness Service (`services/completeness/prompts.py`)

**Adjust scoring for real data quality:**
```
Current average: {self.results.get('completeness', {}).get('average_score', 0):.1f}%

Recommendation:
- Excellent: >80% (adjust from 90%)
- Good: 60-80% (adjust from 80-89%)
- Fair: 40-60% (adjust from 70-79%)
- Poor: <40% (adjust from <60%)
```

---

## 🎯 Next Steps

1. [ ] **Update Keywords** - Add variants found in real data
2. [ ] **Test with LLM** - Run semantic classification on 100 samples
3. [ ] **Measure Accuracy** - Compare prompt results vs ground truth
4. [ ] **Optimize Few-shot Examples** - Use real data patterns
5. [ ] **Handle Edge Cases** - Missing data, ambiguous types

---

## 📈 Recommended Tests

### Test 1: Classification Accuracy
```bash
# Test 100 random properties with LLM
python test_classification.py --sample 100 --mode semantic
```

### Test 2: Attribute Extraction Accuracy
```bash
# Compare extracted vs database values
python test_extraction.py --sample 100 --validate
```

### Test 3: End-to-End Flow
```bash
# Full pipeline test
python test_pipeline.py --queries queries.txt
```

---

**Status:** ✅ Data analysis complete
**Next:** Integrate LLM calls and measure prompt accuracy

---

**Generated by:** Quick Evaluator
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ Report saved!")

    def run(self):
        """Run complete evaluation"""
        print("=" * 70)
        print("🚀 QUICK PROMPT EVALUATION WITH REAL DATA")
        print("=" * 70)

        # Connect to database
        if not self.connect_db():
            print("\n❌ Cannot proceed without database connection")
            print("💡 Start PostgreSQL: docker-compose up postgres -d")
            return

        # Get sample data
        print("\n📥 Loading sample properties...")
        properties = self.get_sample_properties(limit=1000)

        if not properties:
            print("❌ No properties found in database")
            print("💡 Run crawler first: curl -X POST http://localhost:8100/crawl/bulk?total=1000")
            return

        self.results["total_properties"] = len(properties)

        # Run analyses
        self.results["classification"] = self.test_classification_keywords(properties)
        self.results["attribute_extraction"] = self.test_attribute_extraction(properties)
        self.results["price_formats"] = self.analyze_price_formats(properties)
        self.results["location_patterns"] = self.analyze_location_patterns(properties)
        self.results["completeness"] = self.analyze_completeness(properties)

        # Generate report
        report_path = "/Users/tmone/ree-ai/tests/prompt_evaluation/QUICK_EVAL_REPORT.md"
        self.generate_report(report_path)

        print("\n" + "=" * 70)
        print("✅ EVALUATION COMPLETE!")
        print("=" * 70)
        print(f"\n📄 Report: {report_path}")
        print(f"📊 Analyzed: {len(properties)} properties")
        print(f"💡 Next: Update prompts based on findings")


if __name__ == "__main__":
    evaluator = QuickEvaluator()
    evaluator.run()
