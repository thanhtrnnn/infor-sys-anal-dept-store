package dao;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Timestamp;
import java.util.Date;

/**
 * Lớp DAO cơ sở: giữ một kết nối tĩnh dùng chung cho mọi lớp XxxDAO (giáo trình mục 4.3.1, bước 3).
 * Thông tin kết nối mặc định là MySQL; đổi được bằng system property deptstore.db.url / .user / .password.
 */
public class DAO {
    public static Connection con;

    public DAO() {
        if (con == null) {
            String dbUrl = System.getProperty("deptstore.db.url",
                    "jdbc:mysql://localhost:3306/deptstore?useUnicode=true&characterEncoding=UTF-8&useSSL=false");
            try {
                con = DriverManager.getConnection(dbUrl, System.getProperty("deptstore.db.user", "root"),
                        System.getProperty("deptstore.db.password", ""));
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    protected static Timestamp toTimestamp(Date date) {
        return date == null ? null : new Timestamp(date.getTime());
    }
}
