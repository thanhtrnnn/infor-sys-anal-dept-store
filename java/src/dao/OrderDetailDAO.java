package dao;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import model.OrderDetail;
import model.Product;

public class OrderDetailDAO extends DAO {
    public OrderDetailDAO() {
        super();
    }

    /**
     * Lấy các dòng hàng của một đơn, kèm sản phẩm và tồn kho hiện tại.
     * @param idOrder id của đơn hàng
     * @return danh sách dòng hàng (rỗng nếu đơn không có dòng nào)
     */
    public ArrayList<OrderDetail> getOrderDetailByOrder(int idOrder) {
        ArrayList<OrderDetail> kq = new ArrayList<>();
        String sql = "SELECT d.id, d.quantity, d.unitPrice, p.id AS idProduct, p.code, p.name, p.unit, p.salePrice,"
                + " p.stockQuantity, p.status FROM tblOrderDetail d JOIN tblProduct p ON p.id = d.tblProductid"
                + " WHERE d.tblOrderid = ? ORDER BY p.code";
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, idOrder);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    Product p = new Product();
                    p.setId(rs.getInt("idProduct"));
                    p.setCode(rs.getString("code"));
                    p.setName(rs.getString("name"));
                    p.setUnit(rs.getString("unit"));
                    p.setSalePrice(rs.getDouble("salePrice"));
                    p.setStockQuantity(rs.getInt("stockQuantity"));
                    p.setStatus(rs.getString("status"));
                    OrderDetail d = new OrderDetail();
                    d.setId(rs.getInt("id"));
                    d.setQuantity(rs.getInt("quantity"));
                    d.setUnitPrice(rs.getDouble("unitPrice"));
                    d.setLineAmount(d.getQuantity() * d.getUnitPrice()); // thuộc tính dẫn xuất, không lưu trong CSDL
                    d.setProduct(p);
                    kq.add(d);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return kq;
    }
}
