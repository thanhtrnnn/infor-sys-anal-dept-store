package webtest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.File;
import java.net.CookieManager;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import org.apache.catalina.Context;
import org.apache.catalina.startup.Tomcat;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import unittest.TestDB;

/**
 * Chạy các trang JSP thật trong Tomcat nhúng và đi lại hai kịch bản chuẩn qua HTTP (kiểm thử chấp nhận cho 2 module).
 */
class WebFlowTest {
    private static Tomcat tomcat;
    private static String base;

    @BeforeAll
    static void start() throws Exception {
        Path tmp = Files.createTempDirectory("deptstore-web");
        TestDB.fresh("jdbc:sqlite:" + tmp.resolve("deptstore.db"));
        tomcat = new Tomcat();
        tomcat.setBaseDir(tmp.toString());
        tomcat.setPort(0);
        tomcat.getConnector();
        Context ctx = tomcat.addWebapp("",
                new File(System.getProperty("deptstore.webcontent", "WebContent")).getAbsolutePath());
        // classes (model, dao, Jasper) come from the test class path, not from WEB-INF/lib
        ctx.setParentClassLoader(WebFlowTest.class.getClassLoader());
        tomcat.start();
        base = "http://localhost:" + tomcat.getConnector().getLocalPort() + "/";
    }

    @AfterAll
    static void stop() throws Exception {
        tomcat.stop();
        tomcat.destroy();
    }

    private static HttpClient client() {
        return HttpClient.newBuilder().cookieHandler(new CookieManager())
                .followRedirects(HttpClient.Redirect.NORMAL).build();
    }

    private static String get(HttpClient c, String path) throws Exception {
        HttpResponse<String> r = c.send(HttpRequest.newBuilder(URI.create(base + path)).build(),
                HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        assertEquals(200, r.statusCode(), path + "\n" + r.body());
        return r.body();
    }

    private static String post(HttpClient c, String path, String... kv) throws Exception {
        StringBuilder form = new StringBuilder();
        for (int i = 0; i < kv.length; i += 2) {
            form.append(i == 0 ? "" : "&").append(kv[i]).append('=')
                    .append(URLEncoder.encode(kv[i + 1], StandardCharsets.UTF_8));
        }
        HttpResponse<String> r = c.send(HttpRequest.newBuilder(URI.create(base + path))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(form.toString())).build(),
                HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        assertEquals(200, r.statusCode(), path + "\n" + r.body());
        return r.body();
    }

    private static void has(String body, String... parts) {
        for (String p : parts) {
            assertTrue(body.contains(p), "missing \"" + p + "\" in:\n" + body);
        }
    }

    @Test
    void notLoggedInGoesToLoginPage() throws Exception {
        has(get(client(), "khachhang/gdInvoiceList.jsp"), "Hết phiên làm việc");
        has(get(client(), "nhanvienbanhang/gdOrderList.jsp"), "Hết phiên làm việc");
    }

    @Test
    void wrongPassword() throws Exception {
        has(post(client(), "doLogin.jsp", "username", "an", "password", "sai"), "Sai tên đăng nhập hoặc mật khẩu");
    }

    @Test
    void module2ThenModule1StandardScenarios() throws Exception {
        // ---- Module 2: NV01 duyệt, phân công GH03, xuất và in DH1024 ----
        HttpClient sale = client();
        has(post(sale, "doLogin.jsp", "username", "lan", "password", "123456"), "Hoàng Thị Lan", "Duyệt và xuất đơn hàng");
        has(get(sale, "nhanvienbanhang/gdOrderList.jsp?action=filter"),
                "DH1024", "Nguyễn Văn An", "1.250.000", "DH1025", "320.000", "DH1026", "780.000");
        has(get(sale, "nhanvienbanhang/gdOrderDetail.jsp?id=1024"),
                "CHI TIẾT ĐƠN HÀNG DH1024", "Chờ duyệt", "Gạo ST25 5kg", "<td>40</td>", "<td>120</td>", "1.250.000",
                "(chưa phân công)");
        has(post(sale, "nhanvienbanhang/doApproveOrder.jsp"), "Duyệt đơn thành công");
        has(get(sale, "nhanvienbanhang/gdOrderDetail.jsp"), "Đã duyệt");
        has(post(sale, "nhanvienbanhang/doExportOrder.jsp"),
                "Vui lòng chọn nhân viên giao hàng trước khi xuất đơn");                  // ngoại lệ 16c
        String staff = get(sale, "nhanvienbanhang/gdDeliveryStaffList.jsp");
        has(staff, "GH03", "Phạm Văn Dũng", "GH05", "GH08", "Đang giao");
        assertTrue(!staff.contains("GH09"), "inactive staff must not be listed");
        has(post(sale, "nhanvienbanhang/doSaveAssign.jsp", "idDeliveryStaff", "3"), "Phân công thành công: GH03");
        has(post(sale, "nhanvienbanhang/doExportOrder.jsp"), "Xuất hàng thành công cho đơn DH1024");
        has(get(sale, "nhanvienbanhang/gdOrderDetail.jsp"), "Đã xuất", "<td>38</td>", "<td>115</td>", "<td>50</td>",
                "GH03 - Phạm Văn Dũng");
        has(get(sale, "nhanvienbanhang/gdInvoicePrint.jsp"), "HÓA ĐƠN BÁN HÀNG HD1024", "Tổng tiền hóa đơn",
                "1.250.000", "window.print()");
        has(post(sale, "nhanvienbanhang/doExportOrder.jsp"), "đã được xuất");            // ngoại lệ 16a
        assertEquals("38,115,50", TestDB.value("SELECT group_concat(stockQuantity) FROM (SELECT stockQuantity"
                + " FROM tblProduct WHERE id IN (7, 15, 22) ORDER BY id)"));
        String list = get(sale, "nhanvienbanhang/gdOrderList.jsp?action=filter");
        assertTrue(!list.contains("DH1024"), "DH1024 must leave the unexported list (step 24)");

        // ---- Module 2, ngoại lệ 16b: DH1026 thiếu SP30 ----
        TestDB.exec("UPDATE tblProduct SET stockQuantity = 3 WHERE code = 'SP30'");
        has(get(sale, "nhanvienbanhang/gdOrderDetail.jsp?id=1026"), "DH1026", "Đã duyệt");
        get(sale, "nhanvienbanhang/gdDeliveryStaffList.jsp");
        has(post(sale, "nhanvienbanhang/doSaveAssign.jsp", "idDeliveryStaff", "5"), "Phân công thành công: GH05");
        has(post(sale, "nhanvienbanhang/doExportOrder.jsp"),
                "Không đủ hàng để xuất đơn DH1026: SP30 - Nước mắm Nam Ngư 500ml: cần 8, còn 3");
        assertEquals("38/APPROVED", TestDB.value("SELECT (SELECT stockQuantity FROM tblProduct WHERE id = 7)"
                + " || '/' || status FROM tblOrder WHERE id = 1026"));
        has(get(sale, "nhanvienbanhang/gdInvoicePrint.jsp"), "chưa có hóa đơn để in");

        TestDB.exec("DELETE FROM tblOrderDetail WHERE tblOrderid = 1026");
        get(sale, "nhanvienbanhang/gdOrderDetail.jsp");                 // nạp lại chi tiết rỗng từ CSDL
        has(post(sale, "nhanvienbanhang/doExportOrder.jsp"), "Đơn hàng DH1026 không có mặt hàng để xuất");
        assertEquals("APPROVED/0", TestDB.value("SELECT status || '/' || (issueDate IS NOT NULL)"
                + " FROM tblOrder WHERE id = 1026"));

        // ---- Module 1: khách hàng KH01 theo dõi hóa đơn ----
        HttpClient an = client();
        has(post(an, "doLogin.jsp", "username", "an", "password", "123456"), "Nguyễn Văn An", "Theo dõi hóa đơn");
        String invoices = get(an, "khachhang/gdInvoiceList.jsp");
        has(invoices, "HD1024", "Đã xuất", "HD1011", "Đã hủy", "HD0987", "Đã giao");
        assertTrue(invoices.indexOf("HD1024") < invoices.indexOf("HD1011")
                && invoices.indexOf("HD1011") < invoices.indexOf("HD0987"), "newest first");
        has(get(an, "khachhang/gdInvoiceDetail.jsp?id=1024"), "CHI TIẾT HÓA ĐƠN HD1024", "Đã xuất",
                "Phạm Văn Dũng - 0912345678", "Sữa tươi Vinamilk 1L", "1.250.000");
        has(get(an, "khachhang/gdInvoiceDetail.jsp?id=1025"), "Không tìm thấy hóa đơn");   // ngoại lệ 4a / BR01
        has(get(an, "khachhang/gdInvoiceDetail.jsp?id=1011"), "Đã hủy", "Chưa lập");     // ngoại lệ 4b
    }
}
