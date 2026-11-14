package unittest;

import dao.DAO;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;

/**
 * Môi trường kiểm thử: dựng CSDL SQLite từ sql/system_schema.sql + sql/system_sample_data.sql cho mỗi ca kiểm thử
 * (tương đương "rollback sau mỗi ca kiểm thử" trong giáo trình mục 5.3) và gán vào kết nối dùng chung DAO.con.
 */
public final class TestDB {
    private static final Path SQL = Path.of(System.getProperty("deptstore.sql.dir", "../sql"));

    private TestDB() {
    }

    /** CSDL trong bộ nhớ (ca kiểm thử đơn vị) hoặc trong tệp (kiểm thử web). */
    public static Connection fresh(String url) throws Exception {
        Properties p = new Properties();
        p.setProperty("foreign_keys", "true");
        p.setProperty("date_class", "TEXT");
        p.setProperty("date_string_format", "yyyy-MM-dd HH:mm:ss");
        Connection con = DriverManager.getConnection(url, p);
        try (Statement st = con.createStatement()) {
            for (String file : new String[] {"system_schema.sql", "system_sample_data.sql"}) {
                StringBuilder sql = new StringBuilder();
                for (String line : Files.readAllLines(SQL.resolve(file))) {
                    int comment = line.indexOf("--");
                    sql.append(comment >= 0 ? line.substring(0, comment) : line).append('\n');
                }
                for (String stmt : sql.toString().split(";")) {
                    if (!stmt.isBlank()) {
                        st.execute(stmt);
                    }
                }
            }
        }
        if (DAO.con != null && DAO.con != con) {
            DAO.con.close();
        }
        DAO.con = con;
        return con;
    }

    public static Connection fresh() throws Exception {
        return fresh("jdbc:sqlite::memory:");
    }

    /** Giá trị đầu tiên của một câu truy vấn, để kiểm tra CSDL đã thay đổi đúng như mong đợi. */
    public static String value(String sql) throws Exception {
        try (Statement st = DAO.con.createStatement(); ResultSet rs = st.executeQuery(sql)) {
            return rs.next() ? rs.getString(1) : null;
        }
    }

    public static void exec(String sql) throws Exception {
        try (Statement st = DAO.con.createStatement()) {
            st.executeUpdate(sql);
        }
    }
}
