-- ================================================================
-- SEED JAPANESE TRANSLATIONS FOR JAPAN PREFECTURES
-- ================================================================
-- PURPOSE: Add Japanese language translations and aliases for all 18 Japan prefectures
-- DATE: 2025-11-14
-- COVERAGE: 18 major Japan prefectures with Japanese names (Kanji, Hiragana, Romaji)
-- LANGUAGE: Japanese (日本語) - Multiple writing systems supported
-- ================================================================

BEGIN;

-- Delete existing Japanese translations for Japan (if any)
DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'ja'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'JP')
  );

-- Create temporary table for Japanese translations
CREATE TEMP TABLE japanese_trans_temp (
    code VARCHAR(50),
    translated_text VARCHAR(255),
    aliases TEXT[]
);

-- Insert Japanese translations with comprehensive aliases
-- Format: Kanji, Hiragana, Katakana, Romaji variants, major cities
INSERT INTO japanese_trans_temp (code, translated_text, aliases) VALUES

-- Kanto Region (Greater Tokyo Area)
('JP_TOKYO', '東京都',
 ARRAY['東京都', '東京', 'とうきょう', 'トウキョウ', 'tokyo', 'tōkyō', 'tokio', '首都', 'しゅと', 'capital', '23区', 'tokyo metropolis', 'tokyo-to']),

('JP_KANAGAWA', '神奈川県',
 ARRAY['神奈川県', '神奈川', 'かながわ', 'カナガワ', 'kanagawa', 'kanagawa-ken', '横浜', 'よこはま', 'yokohama', '川崎', 'かわさき', 'kawasaki']),

('JP_SAITAMA', '埼玉県',
 ARRAY['埼玉県', '埼玉', 'さいたま', 'サイタマ', 'saitama', 'saitama-ken', 'saitama city', 'さいたま市']),

('JP_CHIBA', '千葉県',
 ARRAY['千葉県', '千葉', 'ちば', 'チバ', 'chiba', 'chiba-ken', 'chiba city', 'narita', '成田', 'なりた']),

('JP_IBARAKI', '茨城県',
 ARRAY['茨城県', '茨城', 'いばらき', 'イバラキ', 'ibaraki', 'ibaraki-ken', 'mito', '水戸', 'みと']),

('JP_TOCHIGI', '栃木県',
 ARRAY['栃木県', '栃木', 'とちぎ', 'トチギ', 'tochigi', 'tochigi-ken', 'utsunomiya', '宇都宮', 'うつのみや']),

('JP_GUNMA', '群馬県',
 ARRAY['群馬県', '群馬', 'ぐんま', 'グンマ', 'gunma', 'gumma', 'gunma-ken', 'maebashi', '前橋', 'まえばし']),

-- Kansai Region (Western Japan)
('JP_OSAKA', '大阪府',
 ARRAY['大阪府', '大阪', 'おおさか', 'オオサカ', 'osaka', 'ōsaka', 'oosaka', 'osaka-fu', '難波', 'なんば', 'namba', '梅田', 'うめだ', 'umeda']),

('JP_KYOTO', '京都府',
 ARRAY['京都府', '京都', 'きょうと', 'キョウト', 'kyoto', 'kyōto', 'kyouto', 'kyoto-fu', '古都', 'こと', 'ancient capital']),

('JP_HYOGO', '兵庫県',
 ARRAY['兵庫県', '兵庫', 'ひょうご', 'ヒョウゴ', 'hyogo', 'hyōgo', 'hyougo', 'hyogo-ken', '神戸', 'こうべ', 'kobe']),

('JP_NARA', '奈良県',
 ARRAY['奈良県', '奈良', 'なら', 'ナラ', 'nara', 'nara-ken', 'nara city', 'nara park']),

('JP_SHIGA', '滋賀県',
 ARRAY['滋賀県', '滋賀', 'しが', 'シガ', 'shiga', 'shiga-ken', 'otsu', '大津', 'おおつ', 'lake biwa', '琵琶湖', 'びわこ']),

('JP_WAKAYAMA', '和歌山県',
 ARRAY['和歌山県', '和歌山', 'わかやま', 'ワカヤマ', 'wakayama', 'wakayama-ken']),

-- Chubu Region (Central Japan)
('JP_AICHI', '愛知県',
 ARRAY['愛知県', '愛知', 'あいち', 'アイチ', 'aichi', 'aichi-ken', '名古屋', 'なごや', 'nagoya', 'nagoya city']),

('JP_SHIZUOKA', '静岡県',
 ARRAY['静岡県', '静岡', 'しずおか', 'シズオカ', 'shizuoka', 'shizuoka-ken', '富士山', 'ふじさん', 'mt fuji', 'fujisan']),

('JP_GIFU', '岐阜県',
 ARRAY['岐阜県', '岐阜', 'ぎふ', 'ギフ', 'gifu', 'gifu-ken', 'gifu city', 'takayama', '高山', 'たかやま']),

-- Kyushu Region (Southern Island)
('JP_FUKUOKA', '福岡県',
 ARRAY['福岡県', '福岡', 'ふくおか', 'フクオカ', 'fukuoka', 'fukuoka-ken', 'fukuoka city', '博多', 'はかた', 'hakata']),

-- Hokkaido Region (Northern Island)
('JP_HOKKAIDO', '北海道',
 ARRAY['北海道', 'ほっかいどう', 'ホッカイドウ', 'hokkaido', 'hokkaidō', 'hokkaidou', 'sapporo', '札幌', 'さっぽろ', 'northern island']);

-- Insert into main table
DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'ja'
  AND province_id IN (SELECT id FROM ree_common.provinces WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'JP'));

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT p.id, 'ja', t.translated_text, t.aliases
FROM japanese_trans_temp t
JOIN ree_common.provinces p ON p.code = t.code
WHERE p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'JP');

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

-- Count Japanese translations
SELECT
    'Japanese translations added' as metric,
    COUNT(*) as count
FROM ree_common.provinces_translation
WHERE lang_code = 'ja'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'JP')
  );

-- Show sample Japanese prefectures
SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja,
    array_length(t.aliases, 1) as alias_count
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'JP')
ORDER BY p.sort_order
LIMIT 10;

-- Show major cities coverage
\echo ''
\echo '================================================================'
\echo 'MAJOR JAPANESE CITIES COVERED'
\echo '================================================================'
\echo ''
\echo 'Kanto Region:'
\echo '  - Tokyo (東京) - Capital & Largest City'
\echo '  - Yokohama (横浜) - Port City'
\echo '  - Kawasaki (川崎) - Industrial City'
\echo '  - Saitama (さいたま) - Suburban Hub'
\echo ''
\echo 'Kansai Region:'
\echo '  - Osaka (大阪) - Second Largest City'
\echo '  - Kyoto (京都) - Ancient Capital'
\echo '  - Kobe (神戸) - Port City'
\echo '  - Nara (奈良) - Historic City'
\echo ''
\echo 'Chubu Region:'
\echo '  - Nagoya (名古屋) - Third Largest City'
\echo '  - Shizuoka (静岡) - Mt. Fuji'
\echo ''
\echo 'Kyushu Region:'
\echo '  - Fukuoka (福岡) - Southern Hub'
\echo '  - Hakata (博多) - Historic Port'
\echo ''
\echo 'Hokkaido Region:'
\echo '  - Sapporo (札幌) - Northern Capital'
\echo ''
\echo '================================================================'
\echo 'Japanese translations deployed successfully!'
\echo '================================================================'
