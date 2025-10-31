-- Insert 1000 sample properties for prompt evaluation
-- Generated from real batdongsan.com.vn patterns

INSERT INTO properties (title, price, location, bedrooms, bathrooms, area, description, url, source, property_type)
SELECT
  CASE (random() * 5)::int
    WHEN 0 THEN 'Căn hộ ' || (1 + random() * 4)::int || 'PN, DT ' || (50 + random() * 100)::int || 'm²'
    WHEN 1 THEN 'Nhà phố ' || (3 + random() * 3)::int || ' tầng, ' || (random() * 12 + 1)::int || 'PN'
    WHEN 2 THEN 'Biệt thự cao cấp, sân vườn rộng ' || (200 + random() * 300)::int || 'm²'
    WHEN 3 THEN 'Đất nền KDC, DT ' || (80 + random() * 200)::int || 'm²'
    ELSE 'Shophouse mặt tiền, ' || (1 + random() * 3)::int || ' lầu'
  END AS title,

  CASE (random() * 4)::int
    WHEN 0 THEN ((1 + random() * 5)::numeric(10,1) || ' tỷ')
    WHEN 1 THEN ((500 + random() * 2000)::int || ' triệu')
    WHEN 2 THEN ((10 + random() * 90)::int || ' tỷ')
    ELSE ((20 + random() * 50)::int || ' triệu/tháng')
  END AS price,

  CASE (random() * 12)::int
    WHEN 0 THEN 'Quận 1, TP.HCM'
    WHEN 1 THEN 'Quận 2, TP.HCM'
    WHEN 2 THEN 'Quận 3, TP.HCM'
    WHEN 3 THEN 'Quận 7, TP.HCM'
    WHEN 4 THEN 'Q.7, TP.HCM'
    WHEN 5 THEN 'Quận Bình Thạnh, TP.HCM'
    WHEN 6 THEN 'Thủ Đức, TP.HCM'
    WHEN 7 THEN 'Thu Duc, TP.HCM'
    WHEN 8 THEN 'Quận Tân Bình, TP.HCM'
    WHEN 9 THEN 'Q1, TP.HCM'
    WHEN 10 THEN 'District 7, HCMC'
    ELSE 'Quận ' || (1 + random() * 12)::int || ', TP.HCM'
  END AS location,

  (1 + random() * 5)::int AS bedrooms,
  (1 + random() * 4)::int AS bathrooms,

  CASE (random() * 3)::int
    WHEN 0 THEN ((50 + random() * 150)::int || 'm²')
    WHEN 1 THEN ((100 + random() * 200)::int || ' m2')
    ELSE ((80 + random() * 120)::int || 'm2')
  END AS area,

  'Mô tả bất động sản. Nội thất đầy đủ, vị trí đẹp, gần trường học, chợ, siêu thị.' AS description,

  'https://batdongsan.com.vn/property-' || generate_series || '-' || md5(random()::text) AS url,

  'batdongsan' AS source,

  CASE (random() * 5)::int
    WHEN 0 THEN 'apartment'
    WHEN 1 THEN 'house'
    WHEN 2 THEN 'villa'
    WHEN 3 THEN 'land'
    ELSE 'commercial'
  END AS property_type

FROM generate_series(1, 1000);
