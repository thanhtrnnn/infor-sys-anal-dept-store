package dao;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import model.DeliveryStaff;

public class DeliveryStaffDAO extends DAO {
    public DeliveryStaffDAO() {
        super();
    }

    /**
     * Lấy nhân viên giao hàng đang làm việc (không INACTIVE), người sẵn sàng xếp trước, kèm số đơn đang giao.
     */
    public ArrayList<DeliveryStaff> getAvailableDeliveryStaff() {
        ArrayList<DeliveryStaff> kq = new ArrayList<>();
        String sql = "SELECT s.*, (SELECT COUNT(*) FROM tblOrder o WHERE o.tblDeliveryStaffid = s.id"
                + " AND o.status IN ('EXPORTED', 'DELIVERING')) AS activeOrderCount"
                + " FROM tblDeliveryStaff s WHERE s.status <> 'INACTIVE'"
                + " ORDER BY CASE s.status WHEN 'AVAILABLE' THEN 0 ELSE 1 END, s.code";
        try (PreparedStatement ps = con.prepareStatement(sql); ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                DeliveryStaff s = new DeliveryStaff();
                s.setId(rs.getInt("id"));
                s.setCode(rs.getString("code"));
                s.setFullName(rs.getString("fullName"));
                s.setPhone(rs.getString("phone"));
                s.setArea(rs.getString("area"));
                s.setStatus(rs.getString("status"));
                s.setActiveOrderCount(rs.getInt("activeOrderCount"));
                kq.add(s);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return kq;
    }
}
