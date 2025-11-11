-- Seed Data for Wards (Phường/Xã)
-- Description: Comprehensive ward data for major districts in Ho Chi Minh City
-- Focus on districts with high real estate activity: Q1, Q2, Q7, Binh Thanh, Tan Binh, Thu Duc

-- ============================================================
-- DISTRICT 1 (QUẬN 1) - Central Business District
-- ============================================================

INSERT INTO master_wards (code, name_vi, name_en, aliases, district_id, sort_order) VALUES
('Q1_BEN_NGHE', 'Phường Bến Nghé', 'Ben Nghe Ward', ARRAY['Bến Nghé', 'Ben Nghe', 'P. Bến Nghé'], (SELECT id FROM master_districts WHERE code = 'Q1'), 1),
('Q1_BEN_THANH', 'Phường Bến Thành', 'Ben Thanh Ward', ARRAY['Bến Thành', 'Ben Thanh', 'P. Bến Thành'], (SELECT id FROM master_districts WHERE code = 'Q1'), 2),
('Q1_NGUYEN_THAI_BINH', 'Phường Nguyễn Thái Bình', 'Nguyen Thai Binh Ward', ARRAY['Nguyễn Thái Bình', 'Nguyen Thai Binh'], (SELECT id FROM master_districts WHERE code = 'Q1'), 3),
('Q1_PHAM_NGU_LAO', 'Phường Phạm Ngũ Lão', 'Pham Ngu Lao Ward', ARRAY['Phạm Ngũ Lão', 'Pham Ngu Lao'], (SELECT id FROM master_districts WHERE code = 'Q1'), 4),
('Q1_CONG_VI', 'Phường Công Vị', 'Cong Vi Ward', ARRAY['Công Vị', 'Cong Vi'], (SELECT id FROM master_districts WHERE code = 'Q1'), 5),
('Q1_NGUYEN_CU_TRINH', 'Phường Nguyễn Cư Trinh', 'Nguyen Cu Trinh Ward', ARRAY['Nguyễn Cư Trinh', 'Nguyen Cu Trinh'], (SELECT id FROM master_districts WHERE code = 'Q1'), 6),
('Q1_CAUKHO', 'Phường Cầu Kho', 'Cau Kho Ward', ARRAY['Cầu Kho', 'Cau Kho'], (SELECT id FROM master_districts WHERE code = 'Q1'), 7),
('Q1_DA_KAO', 'Phường Đa Kao', 'Da Kao Ward', ARRAY['Đa Kao', 'Da Kao'], (SELECT id FROM master_districts WHERE code = 'Q1'), 8),
('Q1_TAN_DINH', 'Phường Tân Định', 'Tan Dinh Ward', ARRAY['Tân Định', 'Tan Dinh'], (SELECT id FROM master_districts WHERE code = 'Q1'), 9),
('Q1_NGUYEN_THIEN_THUAT', 'Phường Nguyễn Thiện Thuật', 'Nguyen Thien Thuat Ward', ARRAY['Nguyễn Thiện Thuật'], (SELECT id FROM master_districts WHERE code = 'Q1'), 10)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- DISTRICT 7 (QUẬN 7) - Phu My Hung Area
-- ============================================================

INSERT INTO master_wards (code, name_vi, name_en, aliases, district_id, sort_order) VALUES
('Q7_TAN_THUAN_DONG', 'Phường Tân Thuận Đông', 'Tan Thuan Dong Ward', ARRAY['Tân Thuận Đông', 'Tan Thuan Dong'], (SELECT id FROM master_districts WHERE code = 'Q7'), 1),
('Q7_TAN_THUAN_TAY', 'Phường Tân Thuận Tây', 'Tan Thuan Tay Ward', ARRAY['Tân Thuận Tây', 'Tan Thuan Tay'], (SELECT id FROM master_districts WHERE code = 'Q7'), 2),
('Q7_TAN_PHU', 'Phường Tân Phú', 'Tan Phu Ward', ARRAY['Tân Phú', 'Tan Phu', 'P. Tân Phú Q7'], (SELECT id FROM master_districts WHERE code = 'Q7'), 3),
('Q7_TAN_QUY', 'Phường Tân Quy', 'Tan Quy Ward', ARRAY['Tân Quy', 'Tan Quy'], (SELECT id FROM master_districts WHERE code = 'Q7'), 4),
('Q7_TAN_HUNG', 'Phường Tân Hưng', 'Tan Hung Ward', ARRAY['Tân Hưng', 'Tan Hung'], (SELECT id FROM master_districts WHERE code = 'Q7'), 5),
('Q7_BINH_THUAN', 'Phường Bình Thuận', 'Binh Thuan Ward', ARRAY['Bình Thuận', 'Binh Thuan', 'P. Bình Thuận'], (SELECT id FROM master_districts WHERE code = 'Q7'), 6),
('Q7_TAN_KIENG', 'Phường Tân Kiểng', 'Tan Kieng Ward', ARRAY['Tân Kiểng', 'Tan Kieng'], (SELECT id FROM master_districts WHERE code = 'Q7'), 7),
('Q7_TAN_PHUOC_KHANH', 'Phường Tân Phước Khánh', 'Tan Phuoc Khanh Ward', ARRAY['Tân Phước Khánh', 'Tan Phuoc Khanh'], (SELECT id FROM master_districts WHERE code = 'Q7'), 8),
('Q7_PHU_THUAN', 'Phường Phú Thuận', 'Phu Thuan Ward', ARRAY['Phú Thuận', 'Phu Thuan'], (SELECT id FROM master_districts WHERE code = 'Q7'), 9),
('Q7_PHU_MY', 'Phường Phú Mỹ', 'Phu My Ward', ARRAY['Phú Mỹ', 'Phu My', 'Phú Mỹ Hưng'], (SELECT id FROM master_districts WHERE code = 'Q7'), 10)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- BINH THANH (QUẬN BÌNH THẠNH)
-- ============================================================

INSERT INTO master_wards (code, name_vi, name_en, aliases, district_id, sort_order) VALUES
('QBT_P1', 'Phường 1', 'Ward 1', ARRAY['Phường 1', 'P.1', 'P1 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 1),
('QBT_P2', 'Phường 2', 'Ward 2', ARRAY['Phường 2', 'P.2', 'P2 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 2),
('QBT_P3', 'Phường 3', 'Ward 3', ARRAY['Phường 3', 'P.3', 'P3 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 3),
('QBT_P5', 'Phường 5', 'Ward 5', ARRAY['Phường 5', 'P.5', 'P5 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 5),
('QBT_P6', 'Phường 6', 'Ward 6', ARRAY['Phường 6', 'P.6', 'P6 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 6),
('QBT_P7', 'Phường 7', 'Ward 7', ARRAY['Phường 7', 'P.7', 'P7 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 7),
('QBT_P11', 'Phường 11', 'Ward 11', ARRAY['Phường 11', 'P.11', 'P11 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 11),
('QBT_P12', 'Phường 12', 'Ward 12', ARRAY['Phường 12', 'P.12', 'P12 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 12),
('QBT_P13', 'Phường 13', 'Ward 13', ARRAY['Phường 13', 'P.13', 'P13 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 13),
('QBT_P14', 'Phường 14', 'Ward 14', ARRAY['Phường 14', 'P.14', 'P14 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 14),
('QBT_P15', 'Phường 15', 'Ward 15', ARRAY['Phường 15', 'P.15', 'P15 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 15),
('QBT_P17', 'Phường 17', 'Ward 17', ARRAY['Phường 17', 'P.17', 'P17 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 17),
('QBT_P19', 'Phường 19', 'Ward 19', ARRAY['Phường 19', 'P.19', 'P19 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 19),
('QBT_P21', 'Phường 21', 'Ward 21', ARRAY['Phường 21', 'P.21', 'P21 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 21),
('QBT_P22', 'Phường 22', 'Ward 22', ARRAY['Phường 22', 'P.22', 'P22 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 22),
('QBT_P24', 'Phường 24', 'Ward 24', ARRAY['Phường 24', 'P.24', 'P24 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 24),
('QBT_P25', 'Phường 25', 'Ward 25', ARRAY['Phường 25', 'P.25', 'P25 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 25),
('QBT_P26', 'Phường 26', 'Ward 26', ARRAY['Phường 26', 'P.26', 'P26 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 26),
('QBT_P27', 'Phường 27', 'Ward 27', ARRAY['Phường 27', 'P.27', 'P27 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 27),
('QBT_P28', 'Phường 28', 'Ward 28', ARRAY['Phường 28', 'P.28', 'P28 Bình Thạnh'], (SELECT id FROM master_districts WHERE code = 'QBTh'), 28)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- THU DUC CITY (THÀNH PHỐ THỦ ĐỨC) - District 2 Area
-- ============================================================

INSERT INTO master_wards (code, name_vi, name_en, aliases, district_id, sort_order) VALUES
-- Former District 2 wards (now part of Thu Duc City)
('TD_THAO_DIEN', 'Phường Thảo Điền', 'Thao Dien Ward', ARRAY['Thảo Điền', 'Thao Dien', 'P. Thảo Điền'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 1),
('TD_AN_PHU', 'Phường An Phú', 'An Phu Ward', ARRAY['An Phú', 'An Phu', 'P. An Phú'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 2),
('TD_AN_KHANH', 'Phường An Khánh', 'An Khanh Ward', ARRAY['An Khánh', 'An Khanh'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 3),
('TD_BINH_AN', 'Phường Bình An', 'Binh An Ward', ARRAY['Bình An', 'Binh An', 'P. Bình An'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 4),
('TD_BINH_TRUNG_DONG', 'Phường Bình Trưng Đông', 'Binh Trung Dong Ward', ARRAY['Bình Trưng Đông', 'Binh Trung Dong'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 5),
('TD_BINH_TRUNG_TAY', 'Phường Bình Trưng Tây', 'Binh Trung Tay Ward', ARRAY['Bình Trưng Tây', 'Binh Trung Tay'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 6),
('TD_CAT_LAI', 'Phường Cát Lái', 'Cat Lai Ward', ARRAY['Cát Lái', 'Cat Lai'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 7),
('TD_THAO_DIEN_2', 'Phường Thạnh Mỹ Lợi', 'Thanh My Loi Ward', ARRAY['Thạnh Mỹ Lợi', 'Thanh My Loi'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 8),
('TD_THU_THIEM', 'Phường Thủ Thiêm', 'Thu Thiem Ward', ARRAY['Thủ Thiêm', 'Thu Thiem', 'Khu đô thị Thủ Thiêm'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 9),

-- Former District 9 wards
('TD_LONG_BINH', 'Phường Long Bình', 'Long Binh Ward', ARRAY['Long Bình', 'Long Binh'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 10),
('TD_LONG_THANH_MY', 'Phường Long Thạnh Mỹ', 'Long Thanh My Ward', ARRAY['Long Thạnh Mỹ', 'Long Thanh My'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 11),
('TD_LONG_PHU', 'Phường Long Phú', 'Long Phu Ward', ARRAY['Long Phú', 'Long Phu'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 12),
('TD_TANG_NHON_PHU_A', 'Phường Tăng Nhơn Phú A', 'Tang Nhon Phu A Ward', ARRAY['Tăng Nhơn Phú A', 'Tang Nhon Phu A'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 13),
('TD_TANG_NHON_PHU_B', 'Phường Tăng Nhơn Phú B', 'Tang Nhon Phu B Ward', ARRAY['Tăng Nhơn Phú B', 'Tang Nhon Phu B'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 14),
('TD_PHU_HUU', 'Phường Phú Hữu', 'Phu Huu Ward', ARRAY['Phú Hữu', 'Phu Huu'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 15),
('TD_HIEP_PHU', 'Phường Hiệp Phú', 'Hiep Phu Ward', ARRAY['Hiệp Phú', 'Hiep Phu'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 16),

-- Former Thu Duc District wards
('TD_LINH_CHIEU', 'Phường Linh Chiểu', 'Linh Chieu Ward', ARRAY['Linh Chiểu', 'Linh Chieu'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 17),
('TD_LINH_DONG', 'Phường Linh Đông', 'Linh Dong Ward', ARRAY['Linh Đông', 'Linh Dong'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 18),
('TD_LINH_TAY', 'Phường Linh Tây', 'Linh Tay Ward', ARRAY['Linh Tây', 'Linh Tay'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 19),
('TD_LINH_TRUNG', 'Phường Linh Trung', 'Linh Trung Ward', ARRAY['Linh Trung', 'Linh Trung'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 20),
('TD_TAM_BINH', 'Phường Tam Bình', 'Tam Binh Ward', ARRAY['Tam Bình', 'Tam Binh'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 21),
('TD_TAM_PHU', 'Phường Tam Phú', 'Tam Phu Ward', ARRAY['Tam Phú', 'Tam Phu'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 22),
('TD_TRUONG_THO', 'Phường Trường Thọ', 'Truong Tho Ward', ARRAY['Trường Thọ', 'Truong Tho'], (SELECT id FROM master_districts WHERE code = 'TPTD'), 23)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- TAN BINH (QUẬN TÂN BÌNH) - Near Airport
-- ============================================================

INSERT INTO master_wards (code, name_vi, name_en, aliases, district_id, sort_order) VALUES
('QTB_P1', 'Phường 1', 'Ward 1', ARRAY['Phường 1', 'P.1 Tân Bình', 'P1'], (SELECT id FROM master_districts WHERE code = 'QTD'), 1),
('QTB_P2', 'Phường 2', 'Ward 2', ARRAY['Phường 2', 'P.2 Tân Bình', 'P2'], (SELECT id FROM master_districts WHERE code = 'QTD'), 2),
('QTB_P3', 'Phường 3', 'Ward 3', ARRAY['Phường 3', 'P.3 Tân Bình', 'P3'], (SELECT id FROM master_districts WHERE code = 'QTD'), 3),
('QTB_P4', 'Phường 4', 'Ward 4', ARRAY['Phường 4', 'P.4 Tân Bình', 'P4'], (SELECT id FROM master_districts WHERE code = 'QTD'), 4),
('QTB_P5', 'Phường 5', 'Ward 5', ARRAY['Phường 5', 'P.5 Tân Bình', 'P5'], (SELECT id FROM master_districts WHERE code = 'QTD'), 5),
('QTB_P6', 'Phường 6', 'Ward 6', ARRAY['Phường 6', 'P.6 Tân Bình', 'P6'], (SELECT id FROM master_districts WHERE code = 'QTD'), 6),
('QTB_P7', 'Phường 7', 'Ward 7', ARRAY['Phường 7', 'P.7 Tân Bình', 'P7'], (SELECT id FROM master_districts WHERE code = 'QTD'), 7),
('QTB_P8', 'Phường 8', 'Ward 8', ARRAY['Phường 8', 'P.8 Tân Bình', 'P8'], (SELECT id FROM master_districts WHERE code = 'QTD'), 8),
('QTB_P10', 'Phường 10', 'Ward 10', ARRAY['Phường 10', 'P.10 Tân Bình', 'P10'], (SELECT id FROM master_districts WHERE code = 'QTD'), 10),
('QTB_P11', 'Phường 11', 'Ward 11', ARRAY['Phường 11', 'P.11 Tân Bình', 'P11'], (SELECT id FROM master_districts WHERE code = 'QTD'), 11),
('QTB_P12', 'Phường 12', 'Ward 12', ARRAY['Phường 12', 'P.12 Tân Bình', 'P12'], (SELECT id FROM master_districts WHERE code = 'QTD'), 12),
('QTB_P13', 'Phường 13', 'Ward 13', ARRAY['Phường 13', 'P.13 Tân Bình', 'P13'], (SELECT id FROM master_districts WHERE code = 'QTD'), 13),
('QTB_P14', 'Phường 14', 'Ward 14', ARRAY['Phường 14', 'P.14 Tân Bình', 'P14'], (SELECT id FROM master_districts WHERE code = 'QTD'), 14),
('QTB_P15', 'Phường 15', 'Ward 15', ARRAY['Phường 15', 'P.15 Tân Bình', 'P15'], (SELECT id FROM master_districts WHERE code = 'QTD'), 15)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- DISTRICT 3 (QUẬN 3)
-- ============================================================

INSERT INTO master_wards (code, name_vi, name_en, aliases, district_id, sort_order) VALUES
('Q3_P1', 'Phường 1', 'Ward 1', ARRAY['Phường 1', 'P.1 Q3'], (SELECT id FROM master_districts WHERE code = 'Q3'), 1),
('Q3_P2', 'Phường 2', 'Ward 2', ARRAY['Phường 2', 'P.2 Q3'], (SELECT id FROM master_districts WHERE code = 'Q3'), 2),
('Q3_P3', 'Phường 3', 'Ward 3', ARRAY['Phường 3', 'P.3 Q3'], (SELECT id FROM master_districts WHERE code = 'Q3'), 3),
('Q3_P4', 'Phường 4', 'Ward 4', ARRAY['Phường 4', 'P.4 Q3'], (SELECT id FROM master_districts WHERE code = 'Q3'), 4),
('Q3_P5', 'Phường 5', 'Ward 5', ARRAY['Phường 5', 'P.5 Q3'], (SELECT id FROM master_districts WHERE code = 'Q3'), 5),
('Q3_P9', 'Phường 9', 'Ward 9', ARRAY['Phường 9', 'P.9 Q3'], (SELECT id FROM master_districts WHERE code = 'Q3'), 9),
('Q3_P10', 'Phường 10', 'Ward 10', ARRAY['Phường 10', 'P.10 Q3'], (SELECT id FROM master_districts WHERE code = 'Q3'), 10),
('Q3_P11', 'Phường 11', 'Ward 11', ARRAY['Phường 11', 'P.11 Q3'], (SELECT id FROM master_districts WHERE code = 'Q3'), 11),
('Q3_P12', 'Phường 12', 'Ward 12', ARRAY['Phường 12', 'P.12 Q3'], (SELECT id FROM master_districts WHERE code = 'Q3'), 12),
('Q3_P13', 'Phường 13', 'Ward 13', ARRAY['Phường 13', 'P.13 Q3'], (SELECT id FROM master_districts WHERE code = 'Q3'), 13),
('Q3_VO_THI_SAU', 'Phường Võ Thị Sáu', 'Vo Thi Sau Ward', ARRAY['Võ Thị Sáu', 'Vo Thi Sau'], (SELECT id FROM master_districts WHERE code = 'Q3'), 14)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- PHU NHUAN (QUẬN PHÚ NHUẬN)
-- ============================================================

INSERT INTO master_wards (code, name_vi, name_en, aliases, district_id, sort_order) VALUES
('QPN_P1', 'Phường 1', 'Ward 1', ARRAY['Phường 1', 'P.1 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 1),
('QPN_P2', 'Phường 2', 'Ward 2', ARRAY['Phường 2', 'P.2 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 2),
('QPN_P3', 'Phường 3', 'Ward 3', ARRAY['Phường 3', 'P.3 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 3),
('QPN_P4', 'Phường 4', 'Ward 4', ARRAY['Phường 4', 'P.4 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 4),
('QPN_P5', 'Phường 5', 'Ward 5', ARRAY['Phường 5', 'P.5 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 5),
('QPN_P7', 'Phường 7', 'Ward 7', ARRAY['Phường 7', 'P.7 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 7),
('QPN_P8', 'Phường 8', 'Ward 8', ARRAY['Phường 8', 'P.8 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 8),
('QPN_P9', 'Phường 9', 'Ward 9', ARRAY['Phường 9', 'P.9 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 9),
('QPN_P10', 'Phường 10', 'Ward 10', ARRAY['Phường 10', 'P.10 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 10),
('QPN_P11', 'Phường 11', 'Ward 11', ARRAY['Phường 11', 'P.11 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 11),
('QPN_P13', 'Phường 13', 'Ward 13', ARRAY['Phường 13', 'P.13 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 13),
('QPN_P15', 'Phường 15', 'Ward 15', ARRAY['Phường 15', 'P.15 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 15),
('QPN_P17', 'Phường 17', 'Ward 17', ARRAY['Phường 17', 'P.17 Phú Nhuận'], (SELECT id FROM master_districts WHERE code = 'QPN'), 17)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- BINH CHANH (HUYỆN BÌNH CHÁNH)
-- ============================================================

INSERT INTO master_wards (code, name_vi, name_en, aliases, district_id, sort_order) VALUES
('HBC_BINH_CHANH', 'Xã Bình Chánh', 'Binh Chanh Commune', ARRAY['Bình Chánh', 'X. Bình Chánh'], (SELECT id FROM master_districts WHERE code = 'HBC'), 1),
('HBC_BINH_HUNG', 'Xã Bình Hưng', 'Binh Hung Commune', ARRAY['Bình Hưng', 'X. Bình Hưng'], (SELECT id FROM master_districts WHERE code = 'HBC'), 2),
('HBC_BINH_LAI', 'Xã Bình Lãi', 'Binh Lai Commune', ARRAY['Bình Lãi', 'X. Bình Lãi'], (SELECT id FROM master_districts WHERE code = 'HBC'), 3),
('HBC_LE_MINH_XUAN', 'Xã Lê Minh Xuân', 'Le Minh Xuan Commune', ARRAY['Lê Minh Xuân', 'X. Lê Minh Xuân'], (SELECT id FROM master_districts WHERE code = 'HBC'), 4),
('HBC_TAN_TUC', 'Xã Tân Túc', 'Tan Tuc Commune', ARRAY['Tân Túc', 'X. Tân Túc'], (SELECT id FROM master_districts WHERE code = 'HBC'), 5),
('HBC_VINH_LOC_A', 'Xã Vĩnh Lộc A', 'Vinh Loc A Commune', ARRAY['Vĩnh Lộc A', 'X. Vĩnh Lộc A'], (SELECT id FROM master_districts WHERE code = 'HBC'), 6),
('HBC_VINH_LOC_B', 'Xã Vĩnh Lộc B', 'Vinh Loc B Commune', ARRAY['Vĩnh Lộc B', 'X. Vĩnh Lộc B'], (SELECT id FROM master_districts WHERE code = 'HBC'), 7)
ON CONFLICT (code) DO NOTHING;
