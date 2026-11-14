package dao;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import model.OrderDetail;

public class ProductDAO extends DAO {
    public ProductDAO() {
        super();
    }

    /**
     * Kiểm tra tồn kho cho mọi dòng hàng; cập nhật stockQuantity hiện tại vào từng Product để giao diện báo thiếu.
     * @return true nếu mọi sản phẩm còn đủ số lượng đặt
     */
    public boolean checkStock(ArrayList<OrderDetail> listDetail) {
        boolean kq = true;
        String sql = "SELECT stockQuantity FROM tblProduct WHERE id = ?";
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            for (OrderDetail d : listDetail) {
                ps.setInt(1, d.getProduct().getId());
                try (ResultSet rs = ps.executeQuery()) {
                    int stock = rs.next() ? rs.getInt(1) : 0;
                    d.getProduct().setStockQuantity(stock);
                    if (stock < d.getQuantity()) {
                        kq = false;
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            kq = false;
        }
        return kq;
    }

    /**
     * Trừ tồn kho từng dòng hàng. Điều kiện stockQuantity >= ? đảm bảo không trừ âm khi hai giao dịch chạy đồng thời.
     * Chạy trong giao dịch của OrderDAO.exportOrder() (kết nối dùng chung) nên không tự commit.
     * @return true nếu trừ được mọi dòng
     */
    public boolean decreaseStock(ArrayList<OrderDetail> listDetail) {
        String sql = "UPDATE tblProduct SET stockQuantity = stockQuantity - ? WHERE id = ? AND stockQuantity >= ?";
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            for (OrderDetail d : listDetail) {
                ps.setInt(1, d.getQuantity());
                ps.setInt(2, d.getProduct().getId());
                ps.setInt(3, d.getQuantity());
                if (ps.executeUpdate() != 1) {
                    return false;
                }
                d.getProduct().setStockQuantity(d.getProduct().getStockQuantity() - d.getQuantity());
            }
            return true;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }
}
