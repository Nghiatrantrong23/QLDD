-- ==========================================================================
-- SQL SEED SCRIPT FOR QLDD GIS PRO (POSTGRESQL + POSTGIS)
-- UPDATED: Added ON CONFLICT and removed missing columns
-- ==========================================================================

-- 1. ADD NEW OWNERS (Ignore if exists)
INSERT INTO myapp_chusudung (ho_ten, so_giay_to, loai_doi_tuong, dia_chi, so_dien_thoai, ngay_tao)
VALUES 
('Le Quang Vinh', '048092001122', 'ca_nhan', '22 Nguyen Hue, Da Nang', '0912345678', NOW()),
('Tran Thanh Hang', '052093003344', 'ca_nhan', '45 Le Duan, Da Nang', '0987654321', NOW()),
('Dia oc Viet Corp', '0101234567', 'to_chuc', '100 Duy Tan, Da Nang', '02363123456', NOW())
ON CONFLICT (so_giay_to) DO NOTHING;

-- 2. ADD LAND PARCELS (Ignore if exists)
INSERT INTO myapp_thuadat (
    ma_thua, so_to, so_thua, dia_chi_thua, dien_tich, loai_dat, 
    muc_dich_su_dung, chu_su_dung_id, mpoly, centroid, 
    so_gcn, ngay_cap_gcn, that_nghiep_lau, ghi_chu, ngay_tao, ngay_cap_nhat
)
VALUES 
(
    'PG-DT-991', 12, 105, 'Hoa Xuan, Da Nang', 150.5, 'ODT', 
    'Dat o do thi', 
    (SELECT id FROM myapp_chusudung WHERE ho_ten='Le Quang Vinh' LIMIT 1),
    ST_Multi(ST_GeomFromText('POLYGON((108.210 16.050, 108.211 16.050, 108.211 16.051, 108.210 16.051, 108.210 16.050))', 4326)),
    ST_GeomFromText('POINT(108.2105 16.0505)', 4326),
    'GCN-112233', '2023-01-15', false, '', NOW(), NOW()
),
(
    'PG-DT-992', 15, 202, 'Truong Sa Street, Da Nang', 320.0, 'CLN', 
    'Dat cay lau nam', 
    (SELECT id FROM myapp_chusudung WHERE ho_ten='Tran Thanh Hang' LIMIT 1),
    ST_Multi(ST_GeomFromText('POLYGON((108.240 16.000, 108.242 16.000, 108.242 16.002, 108.240 16.002, 108.240 16.000))', 4326)),
    ST_GeomFromText('POINT(108.241 16.001)', 4326),
    'GCN-445566', '2022-11-20', false, '', NOW(), NOW()
)
ON CONFLICT (ma_thua) DO NOTHING;

-- 3. ADD PLANNING ZONES
INSERT INTO myapp_vungquyhoach (ten_vung, loai_quy_hoach, nam_quy_hoach, mo_ta, geom, ngay_tao)
VALUES 
(
    'Lien Chieu Industrial Zone', 'dat_cong_nghiep', 2040, 'Urban planning 2040',
    ST_Multi(ST_GeomFromText('POLYGON((108.120 16.120, 108.150 16.120, 108.150 16.150, 108.120 16.150, 108.120 16.120))', 4326)),
    NOW()
)
ON CONFLICT DO NOTHING;

-- 4. ADD ALERTS (Removed MISSING column 'trang_thai')
-- Note: 'thua_dat_lien_quan_id' is added as NULL for generic alerts
INSERT INTO myapp_canhbaogis (tieu_de, loai_canh_bao, muc_do, noi_dung, location, da_xu_ly, ngay_phat_sinh)
VALUES 
('Canh bao ranh gioi', 'tranh_chap', 'trung_binh', 'Boundary dispute at Ngu Hanh Son', 
 ST_GeomFromText('POINT(108.250 16.010)', 4326), false, NOW());
