package dao;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import model.Customer;
import model.Member;
import model.SaleStaff;
import model.Staff;

/** Đăng nhập dùng chung cho mọi thành viên (view.thanhvien). */
public class MemberDAO extends DAO {
    public MemberDAO() {
        super();
    }

    /**
     * Kiểm tra đăng nhập.
     * @return Customer, SaleStaff hoặc Staff (nhân viên quản lí) tùy vai trò; null nếu sai tài khoản/mật khẩu
     */
    public Member checkLogin(String username, String password) {
        String sql = "SELECT m.id, m.fullName, m.phone, m.address, m.role, c.code AS customerCode, s.code AS staffCode,"
                + " s.position FROM tblMember m"
                + " LEFT JOIN tblCustomer c ON c.tblMemberid = m.id"
                + " LEFT JOIN tblStaff s ON s.tblMemberid = m.id"
                + " WHERE m.username = ? AND m.password = ? AND m.status = 'ACTIVE'";
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setString(1, username);
            ps.setString(2, password);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) {
                    return null;
                }
                Member m;
                String role = rs.getString("role");
                if ("CUSTOMER".equals(role)) {
                    Customer c = new Customer();
                    c.setCode(rs.getString("customerCode"));
                    m = c;
                } else {
                    Staff s = "SALE_STAFF".equals(role) ? new SaleStaff() : new Staff();
                    s.setCode(rs.getString("staffCode"));
                    s.setPosition(rs.getString("position"));
                    m = s;
                }
                m.setId(rs.getInt("id"));
                m.setUsername(username);
                m.setFullName(rs.getString("fullName"));
                m.setPhone(rs.getString("phone"));
                m.setAddress(rs.getString("address"));
                m.setRole(role);
                return m;
            }
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}
