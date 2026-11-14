-- Thiết kế CSDL của HỆ THỐNG (giáo trình BG HP TTTN 2 CNPM 2020, mục 4.2, 5 bước).
-- Đầu vào: biểu đồ lớp thực thể pha thiết kế (diagrams/src/q2c-design-entity-classes-system.puml).
-- Chạy được trên MySQL 8 và SQLite 3. Quy ước: khóa chính `id`, khóa ngoại `tbl<Bảng>id`.
--
-- Bước 1-2: mỗi lớp thực thể -> một bảng; chỉ lấy thuộc tính kiểu cơ bản.
-- Bước 3: 1-n giữ nguyên; Order 1-1 Invoice -> GỘP Invoice vào tblOrder (invoiceCode, issueDate).
-- Bước 4: PK = id; lớp con (Customer, Staff) dùng khóa chính kiêm khóa ngoại tblMemberid.
-- Bước 5: loại thuộc tính dẫn xuất / trùng lặp và bảng rỗng:
--   * Order.totalAmount, OrderDetail.lineAmount, ImportReceipt.totalAmount, ImportReceiptDetail.lineAmount,
--     Invoice.totalAmount: tính được từ quantity x đơn giá -> bỏ.
--   * SaleStaff, ManagementStaff: không có thuộc tính riêng, chỉ còn 1 khóa ngoại -> bỏ bảng (phân biệt bằng tblMember.role).
--   * CustomerStat, SupplierStat, ImportStat, ExportStat: toàn thuộc tính dẫn xuất -> bỏ bảng (tính bằng truy vấn).
--   * OrderDetail.unitPrice GIỮ LẠI: là giá tại thời điểm đặt (BR08), không trùng với Product.salePrice.

DROP TABLE IF EXISTS tblOrderDetail;
DROP TABLE IF EXISTS tblOrder;
DROP TABLE IF EXISTS tblImportReceiptDetail;
DROP TABLE IF EXISTS tblImportReceipt;
DROP TABLE IF EXISTS tblProduct;
DROP TABLE IF EXISTS tblProductCategory;
DROP TABLE IF EXISTS tblSupplier;
DROP TABLE IF EXISTS tblDeliveryStaff;
DROP TABLE IF EXISTS tblStaff;
DROP TABLE IF EXISTS tblCustomer;
DROP TABLE IF EXISTS tblMember;

CREATE TABLE tblMember (
    id                  INTEGER      NOT NULL PRIMARY KEY,
    username            VARCHAR(255) NOT NULL UNIQUE,
    password            VARCHAR(255) NOT NULL,
    fullName            VARCHAR(255) NOT NULL,
    email               VARCHAR(255),
    phone               VARCHAR(20),
    address             VARCHAR(255),
    role                VARCHAR(20)  NOT NULL,      -- CUSTOMER | SALE_STAFF | MANAGEMENT_STAFF
    status              VARCHAR(20)  NOT NULL,
    createdAt           DATE         NOT NULL,
    CONSTRAINT ckMemberRole CHECK (role IN ('CUSTOMER', 'SALE_STAFF', 'MANAGEMENT_STAFF'))
);

CREATE TABLE tblCustomer (
    tblMemberid         INTEGER      NOT NULL PRIMARY KEY,
    code                VARCHAR(20)  NOT NULL UNIQUE,
    memberSince         DATE         NOT NULL,
    CONSTRAINT fkCustomerMember FOREIGN KEY (tblMemberid) REFERENCES tblMember (id)
);

CREATE TABLE tblStaff (
    tblMemberid         INTEGER      NOT NULL PRIMARY KEY,
    code                VARCHAR(20)  NOT NULL UNIQUE,
    position            VARCHAR(255) NOT NULL,
    CONSTRAINT fkStaffMember FOREIGN KEY (tblMemberid) REFERENCES tblMember (id)
);

CREATE TABLE tblDeliveryStaff (
    id                  INTEGER      NOT NULL PRIMARY KEY,
    code                VARCHAR(20)  NOT NULL UNIQUE,
    fullName            VARCHAR(255) NOT NULL,
    phone               VARCHAR(20)  NOT NULL,
    area                VARCHAR(255),
    status              VARCHAR(20)  NOT NULL
);

CREATE TABLE tblSupplier (
    id                  INTEGER      NOT NULL PRIMARY KEY,
    code                VARCHAR(20)  NOT NULL UNIQUE,
    name                VARCHAR(255) NOT NULL,
    address             VARCHAR(255),
    phone               VARCHAR(20),
    email               VARCHAR(255),
    status              VARCHAR(20)  NOT NULL
);

CREATE TABLE tblProductCategory (
    id                  INTEGER      NOT NULL PRIMARY KEY,
    name                VARCHAR(255) NOT NULL,
    description         VARCHAR(255)
);

CREATE TABLE tblProduct (
    id                  INTEGER      NOT NULL PRIMARY KEY,
    code                VARCHAR(20)  NOT NULL UNIQUE,
    name                VARCHAR(255) NOT NULL,
    description         VARCHAR(255),
    unit                VARCHAR(50)  NOT NULL,
    salePrice           FLOAT        NOT NULL,
    stockQuantity       INTEGER      NOT NULL DEFAULT 0,
    status              VARCHAR(20)  NOT NULL,
    tblProductCategoryid INTEGER     NOT NULL,
    CONSTRAINT ckProductStock CHECK (stockQuantity >= 0),
    CONSTRAINT fkProductCategory FOREIGN KEY (tblProductCategoryid) REFERENCES tblProductCategory (id)
);

CREATE TABLE tblImportReceipt (
    id                  INTEGER      NOT NULL PRIMARY KEY,
    code                VARCHAR(20)  NOT NULL UNIQUE,
    importDate          DATE         NOT NULL,
    status              VARCHAR(20)  NOT NULL,
    note                VARCHAR(255),
    tblSupplierid       INTEGER      NOT NULL,
    tblStaffid          INTEGER      NOT NULL,     -- nhân viên quản lí lập phiếu
    CONSTRAINT fkReceiptSupplier FOREIGN KEY (tblSupplierid) REFERENCES tblSupplier (id),
    CONSTRAINT fkReceiptStaff FOREIGN KEY (tblStaffid) REFERENCES tblStaff (tblMemberid)
);

CREATE TABLE tblImportReceiptDetail (
    id                  INTEGER      NOT NULL PRIMARY KEY,
    quantity            INTEGER      NOT NULL,
    unitCost            FLOAT        NOT NULL,
    tblImportReceiptid  INTEGER      NOT NULL,
    tblProductid        INTEGER      NOT NULL,
    CONSTRAINT ckReceiptQuantity CHECK (quantity > 0),
    CONSTRAINT fkReceiptDetailReceipt FOREIGN KEY (tblImportReceiptid) REFERENCES tblImportReceipt (id),
    CONSTRAINT fkReceiptDetailProduct FOREIGN KEY (tblProductid) REFERENCES tblProduct (id)
);

CREATE TABLE tblOrder (
    id                  INTEGER      NOT NULL PRIMARY KEY,
    code                VARCHAR(20)  NOT NULL UNIQUE,
    orderDate           DATETIME     NOT NULL,
    shippingAddress     VARCHAR(255) NOT NULL,
    status              VARCHAR(20)  NOT NULL,
    approvedAt          DATETIME,
    exportedAt          DATETIME,
    invoiceCode         VARCHAR(20)  NOT NULL UNIQUE,  -- Invoice gộp vào Order (quan hệ 1-1)
    issueDate           DATETIME,                      -- NULL khi hóa đơn chưa lập
    tblCustomerid       INTEGER      NOT NULL,
    tblStaffid          INTEGER,                       -- nhân viên bán hàng duyệt/xuất; NULL khi chưa duyệt
    tblDeliveryStaffid  INTEGER,                       -- NULL khi chưa phân công
    CONSTRAINT ckOrderStatus CHECK (status IN ('PENDING', 'APPROVED', 'EXPORTED', 'DELIVERING', 'DELIVERED', 'CANCELLED')),
    CONSTRAINT fkOrderCustomer FOREIGN KEY (tblCustomerid) REFERENCES tblCustomer (tblMemberid),
    CONSTRAINT fkOrderStaff FOREIGN KEY (tblStaffid) REFERENCES tblStaff (tblMemberid),
    CONSTRAINT fkOrderDelivery FOREIGN KEY (tblDeliveryStaffid) REFERENCES tblDeliveryStaff (id)
);

CREATE TABLE tblOrderDetail (
    id                  INTEGER      NOT NULL PRIMARY KEY,
    quantity            INTEGER      NOT NULL,
    unitPrice           FLOAT        NOT NULL,          -- giá tại thời điểm đặt (BR08)
    tblOrderid          INTEGER      NOT NULL,
    tblProductid        INTEGER      NOT NULL,
    CONSTRAINT ckOrderDetailQuantity CHECK (quantity > 0),
    CONSTRAINT fkOrderDetailOrder FOREIGN KEY (tblOrderid) REFERENCES tblOrder (id),
    CONSTRAINT fkOrderDetailProduct FOREIGN KEY (tblProductid) REFERENCES tblProduct (id)
);

-- Chỉ mục cho mọi khóa ngoại (checklist rà soát thiết kế CSDL, mục 16)
CREATE INDEX ixProductCategory ON tblProduct (tblProductCategoryid);
CREATE INDEX ixReceiptSupplier ON tblImportReceipt (tblSupplierid);
CREATE INDEX ixReceiptStaff ON tblImportReceipt (tblStaffid);
CREATE INDEX ixReceiptDetailReceipt ON tblImportReceiptDetail (tblImportReceiptid);
CREATE INDEX ixReceiptDetailProduct ON tblImportReceiptDetail (tblProductid);
CREATE INDEX ixOrderCustomer ON tblOrder (tblCustomerid);
CREATE INDEX ixOrderStaff ON tblOrder (tblStaffid);
CREATE INDEX ixOrderDelivery ON tblOrder (tblDeliveryStaffid);
CREATE INDEX ixOrderStatus ON tblOrder (status);
CREATE INDEX ixOrderDetailOrder ON tblOrderDetail (tblOrderid);
CREATE INDEX ixOrderDetailProduct ON tblOrderDetail (tblProductid);
