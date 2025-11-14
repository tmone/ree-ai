-- ================================================================
-- SEED FILIPINO/TAGALOG TRANSLATIONS FOR PHILIPPINES REGIONS
-- ================================================================
-- PURPOSE: Add Filipino/Tagalog translations and aliases for all 17 Philippines regions
-- DATE: 2025-11-14
-- COVERAGE: 17 Philippines regions with Filipino names and aliases
-- ================================================================

BEGIN;

-- Delete existing Filipino translations for Philippines (if any)
DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'tl'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'PH')
  );

-- Insert Filipino/Tagalog translations with comprehensive aliases
INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases) VALUES

-- National Capital Region (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_NCR'), 'tl', 'Kalakhang Maynila',
 ARRAY['kalakhang maynila', 'ncr', 'metro manila', 'manila', 'maynila', 'mm', 'national capital region']),

-- Luzon - Cordillera (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_CAR'), 'tl', 'Cordillera',
 ARRAY['cordillera', 'car', 'cordillera administrative region', 'baguio', 'benguet']),

-- Luzon - Ilocos Region (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_ILOCOS'), 'tl', 'Rehiyon ng Ilocos',
 ARRAY['rehiyon ng ilocos', 'ilocos', 'ilocos region', 'region i', 'region 1', 'vigan', 'laoag']),

-- Luzon - Cagayan Valley (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_CAGAYAN_VALLEY'), 'tl', 'Lambak ng Cagayan',
 ARRAY['lambak ng cagayan', 'cagayan valley', 'region ii', 'region 2', 'tuguegarao', 'isabela']),

-- Luzon - Central Luzon (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_CENTRAL_LUZON'), 'tl', 'Gitnang Luzon',
 ARRAY['gitnang luzon', 'central luzon', 'region iii', 'region 3', 'pampanga', 'angeles', 'clark']),

-- Luzon - CALABARZON (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_CALABARZON'), 'tl', 'CALABARZON',
 ARRAY['calabarzon', 'region iva', 'region 4a', 'cavite', 'laguna', 'batangas', 'rizal', 'quezon']),

-- Luzon - MIMAROPA (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_MIMAROPA'), 'tl', 'MIMAROPA',
 ARRAY['mimaropa', 'region ivb', 'region 4b', 'mindoro', 'marinduque', 'romblon', 'palawan', 'puerto princesa']),

-- Luzon - Bicol (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_BICOL'), 'tl', 'Rehiyon ng Bikol',
 ARRAY['rehiyon ng bikol', 'bicol', 'bicolandia', 'region v', 'region 5', 'naga', 'legazpi', 'albay']),

-- Visayas - Western Visayas (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_WESTERN_VISAYAS'), 'tl', 'Kanlurang Bisaya',
 ARRAY['kanlurang bisaya', 'western visayas', 'region vi', 'region 6', 'iloilo', 'bacolod', 'boracay']),

-- Visayas - Central Visayas (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_CENTRAL_VISAYAS'), 'tl', 'Gitnang Bisaya',
 ARRAY['gitnang bisaya', 'central visayas', 'region vii', 'region 7', 'cebu', 'bohol', 'dumaguete']),

-- Visayas - Eastern Visayas (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_EASTERN_VISAYAS'), 'tl', 'Silangang Bisaya',
 ARRAY['silangang bisaya', 'eastern visayas', 'region viii', 'region 8', 'leyte', 'samar', 'tacloban']),

-- Mindanao - Zamboanga Peninsula (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_ZAMBOANGA'), 'tl', 'Tangway ng Zamboanga',
 ARRAY['tangway ng zamboanga', 'zamboanga', 'region ix', 'region 9', 'zamboanga city']),

-- Mindanao - Northern Mindanao (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_NORTHERN_MINDANAO'), 'tl', 'Hilagang Mindanao',
 ARRAY['hilagang mindanao', 'northern mindanao', 'region x', 'region 10', 'cagayan de oro', 'cdo', 'bukidnon']),

-- Mindanao - Davao Region (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_DAVAO'), 'tl', 'Rehiyon ng Davao',
 ARRAY['rehiyon ng davao', 'davao', 'davao region', 'region xi', 'region 11', 'davao city']),

-- Mindanao - SOCCSKSARGEN (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_SOCCSKSARGEN'), 'tl', 'SOCCSKSARGEN',
 ARRAY['soccsksargen', 'region xii', 'region 12', 'south cotabato', 'general santos', 'gensan']),

-- Mindanao - Caraga (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_CARAGA'), 'tl', 'Rehiyon ng Caraga',
 ARRAY['rehiyon ng caraga', 'caraga', 'region xiii', 'region 13', 'agusan', 'surigao', 'butuan']),

-- Mindanao - BARMM (Autonomous) (1)
((SELECT id FROM ree_common.provinces WHERE code = 'PH_BARMM'), 'tl', 'BARMM',
 ARRAY['barmm', 'bangsamoro', 'autonomous region', 'muslim mindanao', 'cotabato city', 'maguindanao'])

ON CONFLICT (province_id, lang_code) DO UPDATE
SET translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

-- Count Filipino translations
SELECT
    'Filipino translations added' as metric,
    COUNT(*) as count
FROM ree_common.provinces_translation
WHERE lang_code = 'tl'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'PH')
  );

-- Show sample Filipino regions
SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_tl,
    array_length(t.aliases, 1) as alias_count
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'tl'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'PH')
ORDER BY p.sort_order
LIMIT 10;
