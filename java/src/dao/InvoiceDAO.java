package dao;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import model.Customer;
import model.DeliveryStaff;
import model.Invoice;
import model.Order;

/** Hóa đơn được gộp vào tblOrder (quan hệ 1-1): id hóa đơn = id đơn, mã hóa đơn = invoiceCode. */
public class InvoiceDAO extends DAO {
    private static final String SELECT = "SELECT o.id, o.code, o.invoiceCode, o.issueDate, o.orderDate, o.shippingAddress,"
            + " o.status, o.exportedAt, m.id AS idCustomer, m.fullName, m.phone, m.address, c.code AS customerCode,"
            + " ds.id AS idDelivery, ds.code AS deliveryCode, ds.fullName AS deliveryName, ds.phone AS deliveryPhone,"
            + " (SELECT SUM(d.quantity * d.unitPrice) FROM tblOrderDetail d WHERE d.tblOrderid = o.id) AS total"
            + " FROM tblOrder o JOIN tblCustomer c ON c.tblMemberid = o.tblCustomerid"
            + " JOIN tblMember m ON m.id = c.tblMemberid"
            + " LEFT JOIN tblDeliveryStaff ds ON ds.id = o.tblDeliveryStaffid";

    public InvoiceDAO() {
        super();
    }

    /**
     * Danh sách hóa đơn của khách hàng, mới nhất trước.
     * @param idCustomer id của khách hàng đang đăng nhập
     */
    public ArrayList<Invoice> getInvoiceByCustomer(int idCustomer) {
        ArrayList<Invoice> kq = new ArrayList<>();
        try (PreparedStatement ps = con.prepareStatement(SELECT + " WHERE o.tblCustomerid = ? ORDER BY o.orderDate DESC")) {
            ps.setInt(1, idCustomer);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    kq.add(read(rs));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        OrderDetailDAO detailDAO = new OrderDetailDAO();
        for (Invoice inv : kq) {
            inv.getOrder().setDetails(detailDAO.getOrderDetailByOrder(inv.getId())); // để hiển thị số mặt hàng
        }
        return kq;
    }

    /**
     * Chi tiết một hóa đơn kèm dòng hàng. Điều kiện tblCustomerid trong câu truy vấn đảm bảo khách hàng không xem
     * được hóa đơn của người khác (BR01).
     * @return hóa đơn, hoặc null nếu không tồn tại / không thuộc khách hàng
     */
    public Invoice getInvoiceDetail(int idInvoice, int idCustomer) {
        Invoice kq = null;
        try (PreparedStatement ps = con.prepareStatement(SELECT + " WHERE o.id = ? AND o.tblCustomerid = ?")) {
            ps.setInt(1, idInvoice);
            ps.setInt(2, idCustomer);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    kq = read(rs);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        if (kq != null) {
            kq.getOrder().setDetails(new OrderDetailDAO().getOrderDetailByOrder(idInvoice));
        }
        return kq;
    }

    /**
     * Lập hóa đơn: ghi ngày lập = thời điểm xuất đơn. Chạy trong giao dịch của OrderDAO.exportOrder().
     * @return true nếu hóa đơn chưa lập trước đó và đã được lập
     */
    public boolean issueInvoice(Order order) {
        String sql = "UPDATE tblOrder SET issueDate = ? WHERE id = ? AND issueDate IS NULL";
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setTimestamp(1, toTimestamp(order.getExportedAt()));
            ps.setInt(2, order.getId());
            return ps.executeUpdate() == 1;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    private static Invoice read(ResultSet rs) throws Exception {
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
        o.setExportedAt(rs.getTimestamp("exportedAt"));
        o.setTotalAmount(rs.getDouble("total"));
        o.setCustomer(c);
        if (rs.getObject("idDelivery") != null) {
            DeliveryStaff ds = new DeliveryStaff();
            ds.setId(rs.getInt("idDelivery"));
            ds.setCode(rs.getString("deliveryCode"));
            ds.setFullName(rs.getString("deliveryName"));
            ds.setPhone(rs.getString("deliveryPhone"));
            o.setDeliveryStaff(ds);
        }
        Invoice inv = new Invoice();
        inv.setId(o.getId());
        inv.setCode(rs.getString("invoiceCode"));
        inv.setIssueDate(rs.getTimestamp("issueDate"));
        inv.setTotalAmount(o.getTotalAmount()); // thuộc tính dẫn xuất, tính từ các dòng hàng
        inv.setOrder(o);
        return inv;
    }
}
