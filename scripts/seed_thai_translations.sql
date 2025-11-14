-- ================================================================
-- SEED THAI TRANSLATIONS FOR THAILAND PROVINCES
-- ================================================================
-- PURPOSE: Add Thai language translations and aliases for all 46 Thailand provinces
-- DATE: 2025-11-14
-- COVERAGE: 46 Thailand provinces with Thai names and aliases
-- ================================================================

BEGIN;

-- Delete existing Thai translations for Thailand (if any)
DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'th'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'TH')
  );

-- Insert Thai translations with comprehensive aliases
INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases) VALUES

-- Northern Region (9 provinces)
((SELECT id FROM ree_common.provinces WHERE code = 'TH_CHIANG_MAI'), 'th', 'เชียงใหม่',
 ARRAY['เชียงใหม่', 'chiangmai', 'chiang mai', 'เชียงใหม่จังหวัด']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_CHIANG_RAI'), 'th', 'เชียงราย',
 ARRAY['เชียงราย', 'chiangrai', 'chiang rai', 'เชียงรายจังหวัด']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_LAMPHUN'), 'th', 'ลำพูน',
 ARRAY['ลำพูน', 'lamphun', 'lam phun']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_LAMPANG'), 'th', 'ลำปาง',
 ARRAY['ลำปาง', 'lampang', 'lam pang']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_MAE_HONG_SON'), 'th', 'แม่ฮ่องสอน',
 ARRAY['แม่ฮ่องสอน', 'mae hong son', 'maehongson']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_NAN'), 'th', 'น่าน',
 ARRAY['น่าน', 'nan']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_PHAYAO'), 'th', 'พะเยา',
 ARRAY['พะเยา', 'phayao', 'pha yao']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_PHRAE'), 'th', 'แพร่',
 ARRAY['แพร่', 'phrae']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_UTTARADIT'), 'th', 'อุตรดิตถ์',
 ARRAY['อุตรดิตถ์', 'uttaradit', 'uttara dit']),

-- Northeastern Region (Isan) (20 provinces)
((SELECT id FROM ree_common.provinces WHERE code = 'TH_NAKHON_RATCHASIMA'), 'th', 'นครราชสีมา',
 ARRAY['นครราชสีมา', 'nakhon ratchasima', 'korat', 'โคราช', 'นครราชสีมาจังหวัด']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_BURIRAM'), 'th', 'บุรีรัมย์',
 ARRAY['บุรีรัมย์', 'buriram', 'buri ram']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_SURIN'), 'th', 'สุรินทร์',
 ARRAY['สุรินทร์', 'surin']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_SISAKET'), 'th', 'ศรีสะเกษ',
 ARRAY['ศรีสะเกษ', 'sisaket', 'si saket']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_UBON_RATCHATHANI'), 'th', 'อุบลราชธานี',
 ARRAY['อุบลราชธานี', 'ubon ratchathani', 'ubon']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_YASOTHON'), 'th', 'ยโสธร',
 ARRAY['ยโสธร', 'yasothon', 'yaso thon']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_CHAIYAPHUM'), 'th', 'ชัยภูมิ',
 ARRAY['ชัยภูมิ', 'chaiyaphum', 'chai ya phum']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_AMNAT_CHAROEN'), 'th', 'อำนาจเจริญ',
 ARRAY['อำนาจเจริญ', 'amnat charoen', 'amnart charoen']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_NONG_BUA_LAMPHU'), 'th', 'หนองบัวลำภู',
 ARRAY['หนองบัวลำภู', 'nong bua lamphu', 'nongbua lamphu']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_KHON_KAEN'), 'th', 'ขอนแก่น',
 ARRAY['ขอนแก่น', 'khon kaen', 'khonkaen']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_UDON_THANI'), 'th', 'อุดรธานี',
 ARRAY['อุดรธานี', 'udon thani', 'udonthani', 'udon']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_LOEI'), 'th', 'เลย',
 ARRAY['เลย', 'loei']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_NONG_KHAI'), 'th', 'หนองคาย',
 ARRAY['หนองคาย', 'nong khai', 'nongkhai']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_MAHA_SARAKHAM'), 'th', 'มหาสารคาม',
 ARRAY['มหาสารคาม', 'maha sarakham', 'mahasarakham']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_ROI_ET'), 'th', 'ร้อยเอ็ด',
 ARRAY['ร้อยเอ็ด', 'roi et', 'roiet']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_KALASIN'), 'th', 'กาฬสินธุ์',
 ARRAY['กาฬสินธุ์', 'kalasin', 'karasin']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_SAKON_NAKHON'), 'th', 'สกลนคร',
 ARRAY['สกลนคร', 'sakon nakhon', 'sakonnakhon']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_NAKHON_PHANOM'), 'th', 'นครพนม',
 ARRAY['นครพนม', 'nakhon phanom', 'nakhonphanom']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_MUKDAHAN'), 'th', 'มุกดาหาร',
 ARRAY['มุกดาหาร', 'mukdahan', 'muk da han']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_BUENG_KAN'), 'th', 'บึงกาฬ',
 ARRAY['บึงกาฬ', 'bueng kan', 'buengkan']),

-- Central Region (6 provinces)
((SELECT id FROM ree_common.provinces WHERE code = 'TH_BANGKOK'), 'th', 'กรุงเทพมหานคร',
 ARRAY['กรุงเทพมหานคร', 'กรุงเทพ', 'bangkok', 'bkk', 'krung thep', 'กทม']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_SAMUT_PRAKAN'), 'th', 'สมุทรปราการ',
 ARRAY['สมุทรปราการ', 'samut prakan', 'samutprakan']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_NONTHABURI'), 'th', 'นนทบุรี',
 ARRAY['นนทบุรี', 'nonthaburi', 'non tha buri']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_PATHUM_THANI'), 'th', 'ปทุมธานี',
 ARRAY['ปทุมธานี', 'pathum thani', 'pathumthani']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_AYUTTHAYA'), 'th', 'พระนครศรีอยุธยา',
 ARRAY['พระนครศรีอยุธยา', 'อยุธยา', 'ayutthaya', 'ayudhya', 'phra nakhon si ayutthaya']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_NAKHON_PATHOM'), 'th', 'นครปฐม',
 ARRAY['นครปฐม', 'nakhon pathom', 'nakhonpathom']),

-- Eastern Region (7 provinces)
((SELECT id FROM ree_common.provinces WHERE code = 'TH_CHONBURI'), 'th', 'ชลบุรี',
 ARRAY['ชลบุรี', 'chonburi', 'chon buri', 'pattaya', 'พัทยา']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_RAYONG'), 'th', 'ระยอง',
 ARRAY['ระยอง', 'rayong', 'ra yong']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_CHANTHABURI'), 'th', 'จันทบุรี',
 ARRAY['จันทบุรี', 'chanthaburi', 'chan tha buri']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_TRAT'), 'th', 'ตราด',
 ARRAY['ตราด', 'trat', 'koh chang', 'เกาะช้าง']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_CHACHOENGSAO'), 'th', 'ฉะเชิงเทรา',
 ARRAY['ฉะเชิงเทรา', 'chachoengsao', 'cha choeng sao']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_PRACHINBURI'), 'th', 'ปราจีนบุรี',
 ARRAY['ปราจีนบุรี', 'prachinburi', 'prachin buri']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_SA_KAEO'), 'th', 'สระแก้ว',
 ARRAY['สระแก้ว', 'sa kaeo', 'sakaeo']),

-- Southern Region (4 provinces)
((SELECT id FROM ree_common.provinces WHERE code = 'TH_PHUKET'), 'th', 'ภูเก็ต',
 ARRAY['ภูเก็ต', 'phuket', 'phu ket', 'ภูเก็ตจังหวัด']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_KRABI'), 'th', 'กระบี่',
 ARRAY['กระบี่', 'krabi', 'kra bi', 'ao nang', 'อ่าวนาง']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_SURAT_THANI'), 'th', 'สุราษฎร์ธานี',
 ARRAY['สุราษฎร์ธานี', 'surat thani', 'suratthani', 'koh samui', 'เกาะสมุย']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_SONGKHLA'), 'th', 'สงขลา',
 ARRAY['สงขลา', 'songkhla', 'song khla', 'hat yai', 'หาดใหญ่'])

ON CONFLICT (province_id, lang_code) DO UPDATE
SET translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

-- Count Thai translations
SELECT
    'Thai translations added' as metric,
    COUNT(*) as count
FROM ree_common.provinces_translation
WHERE lang_code = 'th'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'TH')
  );

-- Show sample Thai provinces
SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_th,
    array_length(t.aliases, 1) as alias_count
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'th'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'TH')
ORDER BY p.sort_order
LIMIT 10;
