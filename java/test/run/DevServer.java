package run;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import org.apache.catalina.Context;
import org.apache.catalina.startup.Tomcat;
import unittest.TestDB;

/**
 * Chạy thử ứng dụng trên máy cá nhân: dựng CSDL SQLite từ sql/*.sql (dữ liệu mẫu của hai kịch bản chuẩn)
 * rồi mở Tomcat nhúng trên java/WebContent. Không cần cài MySQL hay Tomcat riêng.
 * Chạy bằng: python3 run_app.py  (cổng mặc định 8080, đổi bằng -Ddeptstore.port=...)
 */
public final class DevServer {
    private DevServer() {
    }

    public static void main(String[] args) throws Exception {
        Path tmp = Files.createTempDirectory("deptstore-dev");
        TestDB.fresh("jdbc:sqlite:" + tmp.resolve("deptstore.db"));
        Tomcat tomcat = new Tomcat();
        tomcat.setBaseDir(tmp.toString());
        tomcat.setPort(Integer.getInteger("deptstore.port", 8080));
        tomcat.getConnector();
        Context ctx = tomcat.addWebapp("",
                new File(System.getProperty("deptstore.webcontent", "WebContent")).getAbsolutePath());
        ctx.setParentClassLoader(DevServer.class.getClassLoader());
        tomcat.start();
        System.out.println("Online Department Store: http://localhost:" + tomcat.getConnector().getLocalPort()
                + "/gdLogin.jsp  (khách hàng: an/123456, NV bán hàng: lan/123456)");
        tomcat.getServer().await();
    }
}
