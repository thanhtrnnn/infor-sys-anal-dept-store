package dao;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import model.Customer;
import model.Order;

public class OrderDAO extends DAO {
    public OrderDAO() {
        super();
    }

    /**
     * Danh sách đơn chưa xuất (Chờ duyệt, Đã duyệt), cũ nhất trước, kèm khách hàng, tổng tiền và các dòng hàng.
     */
    public ArrayList<Order> getUnexportedOrder() {
        ArrayList<Order> kq = new ArrayList<>();
        String sql = "SELECT o.id, o.code, o.orderDate, o.shippingAddress, o.status, o.approvedAt,"
                + " m.id AS idCustomer, m.fullName, m.phone, m.address, c.code AS customerCode,"
                + " (SELECT SUM(d.quantity * d.unitPrice) FROM tblOrderDetail d WHERE d.tblOrderid = o.id) AS total"
                + " FROM tblOrder o JOIN tblCustomer c ON c.tblMemberid = o.tblCustomerid"
                + " JOIN tblMember m ON m.id = c.tblMemberid"
                + " WHERE o.status IN ('PENDING', 'APPROVED') ORDER BY o.orderDate";
        try (PreparedStatement ps = con.prepareStatement(sql); ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Customer c = new Customer();
                c.setId(rs.getInt("idCustomer"));
                c.setCode(rs.getString("customerCode"));
                c.setFullName(rs.getString("fullName"));
                c.setPhone(rs.getString("phone"));
                c.setAddress(rs.getString("address"));
                Order o = new Order();
                o.setId(rs.getInt("id"));
                o.setCode(rs.getString("code"));
                o.setOrderDate(rs.getTimestamp("orderDate"));
                o.setShippingAddress(rs.getString("shippingAddress"));
                o.setStatus(rs.getString("status"));
                o.setApprovedAt(rs.getTimestamp("approvedAt"));
                o.setTotalAmount(rs.getDouble("total"));
                o.setCustomer(c);
                kq.add(o);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        OrderDetailDAO detailDAO = new OrderDetailDAO();
        for (Order o : kq) {
            o.setDetails(detailDAO.getOrderDetailByOrder(o.getId())); // cột "Số mặt hàng"
        }
        return kq;
    }

    /**
     * Lưu duyệt đơn: trạng thái, nhân viên duyệt, thời điểm duyệt (đã set vào order bởi doApproveOrder.jsp).
     * @return false nếu đơn không còn ở trạng thái Chờ duyệt (ví dụ đã bị hủy)
     */
    public boolean approveOrder(Order order) {
        String sql = "UPDATE tblOrder SET status = ?, tblStaffid = ?, approvedAt = ? WHERE id = ? AND status = 'PENDING'";
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setString(1, order.getStatus());
            ps.setInt(2, order.getSaleStaff().getId());
            ps.setTimestamp(3, toTimestamp(order.getApprovedAt()));
            ps.setInt(4, order.getId());
            return ps.executeUpdate() == 1;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    /**
     * Lưu nhân viên giao hàng cho đơn đã duyệt; nhân viên phải còn làm việc (không INACTIVE).
     */
    public boolean assignDeliveryStaff(Order order) {
        String sql = "UPDATE tblOrder SET tblDeliveryStaffid = ? WHERE id = ? AND status = 'APPROVED'"
                + " AND EXISTS (SELECT 1 FROM tblDeliveryStaff WHERE id = ? AND status <> 'INACTIVE')";
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, order.getDeliveryStaff().getId());
            ps.setInt(2, order.getId());
            ps.setInt(3, order.getDeliveryStaff().getId());
            return ps.executeUpdate() == 1;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    /**
     * Xuất đơn trong MỘT giao dịch (BR05) trên kết nối dùng chung:
     * kiểm tra tồn kho -> chuyển APPROVED sang EXPORTED (chỉ khi đã phân công) -> trừ tồn kho -> lập hóa đơn.
     * Câu UPDATE có điều kiện status = 'APPROVED' nên một đơn không thể bị xuất hai lần (BR03).
     * @return true nếu xuất thành công; false thì mọi thay đổi đã được rollback
     */
    public boolean exportOrder(Order order) {
        boolean kq = false;
        String sql = "UPDATE tblOrder SET status = ?, tblStaffid = ?, exportedAt = ?"
                + " WHERE id = ? AND status = 'APPROVED' AND tblDeliveryStaffid IS NOT NULL";
        try {
            con.setAutoCommit(false);
            ProductDAO productDAO = new ProductDAO();
            if (productDAO.checkStock(order.getDetails())) {
                try (PreparedStatement ps = con.prepareStatement(sql)) {
                    ps.setString(1, order.getStatus());
                    ps.setInt(2, order.getSaleStaff().getId());
                    ps.setTimestamp(3, toTimestamp(order.getExportedAt()));
                    ps.setInt(4, order.getId());
                    kq = ps.executeUpdate() == 1
                            && productDAO.decreaseStock(order.getDetails())
                            && new InvoiceDAO().issueInvoice(order);
                }
            }
            if (kq) {
                con.commit();
            } else {
                con.rollback();
            }
        } catch (Exception e) {
            e.printStackTrace();
            kq = false;
            try {
                con.rollback();
            } catch (Exception ee) {
                ee.printStackTrace();
            }
        } finally {
            try {
                con.setAutoCommit(true);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return kq;
    }
}
