-- Dữ liệu mẫu cho CSDL hệ thống, khớp hai kịch bản chuẩn (trạng thái ngay trước bước 1 của module 2, 06/09/2026 ~09:00).
-- Mật khẩu để dạng rõ cho mục đích minh họa, giống ví dụ trong giáo trình.

INSERT INTO tblMember (id, username, password, fullName, email, phone, address, role, status, createdAt) VALUES
 (1,  'an',    '123456', 'Nguyễn Văn An', 'an@example.com',    '0905112233', '25 Trần Duy Hưng, Cầu Giấy, Hà Nội', 'CUSTOMER',         'ACTIVE', '2026-01-10'),
 (2,  'bich',  '123456', 'Trần Thị Bích', 'bich@example.com',  '0913456789', '12 Láng Hạ, Đống Đa, Hà Nội',        'CUSTOMER',         'ACTIVE', '2026-02-01'),
 (3,  'cuong', '123456', 'Lê Minh Cường', 'cuong@example.com', '0978123456', '8 Quang Trung, Hà Đông, Hà Nội',     'CUSTOMER',         'ACTIVE', '2026-03-15'),
 (11, 'lan',   '123456', 'Hoàng Thị Lan', 'lan@example.com',   '0901000001', NULL,                                 'SALE_STAFF',       'ACTIVE', '2025-05-01'),
 (12, 'minh',  '123456', 'Vũ Đức Minh',   'minh@example.com',  '0901000002', NULL,                                 'SALE_STAFF',       'ACTIVE', '2025-05-01'),
 (21, 'quanly','123456', 'Đặng Văn Quản', 'ql@example.com',    '0901000009', NULL,                                 'MANAGEMENT_STAFF', 'ACTIVE', '2025-01-01');

INSERT INTO tblCustomer (tblMemberid, code, memberSince) VALUES
 (1, 'KH01', '2026-01-10'), (2, 'KH02', '2026-02-01'), (3, 'KH03', '2026-03-15');

INSERT INTO tblStaff (tblMemberid, code, position) VALUES
 (11, 'NV01', 'Nhân viên bán hàng'), (12, 'NV02', 'Nhân viên bán hàng'), (21, 'QL01', 'Nhân viên quản lí');

INSERT INTO tblDeliveryStaff (id, code, fullName, phone, area, status) VALUES
 (3, 'GH03', 'Phạm Văn Dũng', '0912345678', 'Cầu Giấy',  'AVAILABLE'),
 (5, 'GH05', 'Ngô Thị Hà',    '0987654321', 'Đống Đa',   'AVAILABLE'),
 (8, 'GH08', 'Đỗ Quang Huy',  '0933221100', 'Hà Đông',   'DELIVERING'),
 (9, 'GH09', 'Bùi Văn Tùng',  '0944556677', 'Long Biên', 'INACTIVE');

INSERT INTO tblSupplier (id, code, name, address, phone, email, status) VALUES
 (1, 'NCC01', 'Công ty Lương thực Miền Nam', 'TP Hồ Chí Minh', '0281234567', 'ncc01@example.com', 'ACTIVE');

INSERT INTO tblProductCategory (id, name, description) VALUES
 (1, 'Thực phẩm', NULL), (2, 'Gia dụng', NULL);

INSERT INTO tblProduct (id, code, name, description, unit, salePrice, stockQuantity, status, tblProductCategoryid) VALUES
 (7,  'SP07', 'Gạo ST25 5kg',               NULL, 'Túi',  250000,  40, 'ACTIVE', 1),
 (15, 'SP15', 'Dầu ăn Neptune 1L',          NULL, 'Chai',  60000, 120, 'ACTIVE', 1),
 (22, 'SP22', 'Sữa tươi Vinamilk 1L',       NULL, 'Hộp',   45000,  60, 'ACTIVE', 1),
 (30, 'SP30', 'Nước mắm Nam Ngư 500ml',     NULL, 'Chai',  35000,  80, 'ACTIVE', 1),
 (40, 'SP40', 'Nồi cơm điện Sunhouse 1.8L', NULL, 'Cái',  320000,  15, 'ACTIVE', 2);

INSERT INTO tblOrder (id, code, orderDate, shippingAddress, status, approvedAt, exportedAt, invoiceCode, issueDate,
                      tblCustomerid, tblStaffid, tblDeliveryStaffid) VALUES
 (987,  'DH0987', '2026-08-20 19:05:00', '25 Trần Duy Hưng, Cầu Giấy, Hà Nội', 'DELIVERED',  '2026-08-21 08:10:00', '2026-08-21 09:00:00', 'HD0987', '2026-08-21 09:00:00', 1, 12, 5),
 (1011, 'DH1011', '2026-09-01 21:30:00', '25 Trần Duy Hưng, Cầu Giấy, Hà Nội', 'CANCELLED',  NULL, NULL, 'HD1011', NULL, 1, NULL, NULL),
 (1024, 'DH1024', '2026-09-05 10:12:00', '25 Trần Duy Hưng, Cầu Giấy, Hà Nội', 'PENDING',    NULL, NULL, 'HD1024', NULL, 1, NULL, NULL),
 (1025, 'DH1025', '2026-09-05 15:40:00', '12 Láng Hạ, Đống Đa, Hà Nội',        'PENDING',    NULL, NULL, 'HD1025', NULL, 2, NULL, NULL),
 (1026, 'DH1026', '2026-09-06 07:55:00', '8 Quang Trung, Hà Đông, Hà Nội',     'APPROVED',   '2026-09-06 08:20:00', NULL, 'HD1026', NULL, 3, 12, NULL),
 (990,  'DH0990', '2026-09-04 09:00:00', '12 Láng Hạ, Đống Đa, Hà Nội',        'DELIVERING', '2026-09-04 10:00:00', '2026-09-04 11:00:00', 'HD0990', '2026-09-04 11:00:00', 2, 11, 3),
 (991,  'DH0991', '2026-09-04 09:30:00', '8 Quang Trung, Hà Đông, Hà Nội',     'DELIVERING', '2026-09-04 10:05:00', '2026-09-04 11:05:00', 'HD0991', '2026-09-04 11:05:00', 3, 11, 8),
 (992,  'DH0992', '2026-09-04 13:00:00', '12 Láng Hạ, Đống Đa, Hà Nội',        'EXPORTED',   '2026-09-04 14:00:00', '2026-09-05 08:30:00', 'HD0992', '2026-09-05 08:30:00', 2, 12, 8),
 (993,  'DH0993', '2026-09-04 16:20:00', '8 Quang Trung, Hà Đông, Hà Nội',     'EXPORTED',   '2026-09-05 08:00:00', '2026-09-05 08:40:00', 'HD0993', '2026-09-05 08:40:00', 3, 12, 8);

INSERT INTO tblOrderDetail (id, quantity, unitPrice, tblOrderid, tblProductid) VALUES
 (1,  9,  60000, 987,  15),
 (2,  5,  35000, 1011, 30),
 (3,  2, 250000, 1024, 7),
 (4,  5,  60000, 1024, 15),
 (5, 10,  45000, 1024, 22),
 (6,  1, 320000, 1025, 40),
 (7,  2, 250000, 1026, 7),
 (8,  8,  35000, 1026, 30),
 (9,  2,  45000, 990,  22),
 (10, 2,  35000, 991,  30),
 (11, 2,  35000, 992,  30),
 (12, 2,  35000, 993,  30);
