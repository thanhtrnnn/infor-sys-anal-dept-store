package unittest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dao.DeliveryStaffDAO;
import dao.OrderDAO;
import dao.OrderDetailDAO;
import java.util.Date;
import java.util.stream.Collectors;
import model.DeliveryStaff;
import model.Order;
import model.SaleStaff;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class OrderDAOTest {
    private final SaleStaff lan = new SaleStaff();

    @BeforeEach
    void db() throws Exception {
        TestDB.fresh();
        lan.setId(11);
    }

    private Order order(int id) {
        Order o = new OrderDAO().getUnexportedOrder().stream().filter(x -> x.getId() == id).findFirst().orElseThrow();
        o.setDetails(new OrderDetailDAO().getOrderDetailByOrder(id));
        return o;
    }

    private DeliveryStaff staff(String code) {
        return new DeliveryStaffDAO().getAvailableDeliveryStaff().stream()
                .filter(s -> s.getCode().equals(code)).findFirst().orElseThrow();
    }

    private boolean approve(Order o) {
        o.setStatus("APPROVED");
        o.setSaleStaff(lan);
        o.setApprovedAt(new Date());
        return new OrderDAO().approveOrder(o);
    }

    private boolean export(Order o) {
        o.setStatus("EXPORTED");
        o.setSaleStaff(lan);
        o.setExportedAt(new Date());
        return new OrderDAO().exportOrder(o);
    }

    private static String stock() throws Exception {
        return TestDB.value("SELECT group_concat(stockQuantity) FROM (SELECT stockQuantity FROM tblProduct"
                + " WHERE id IN (7, 15, 22, 30) ORDER BY id)");
    }

    @Test
    void unexportedOrders() {
        assertEquals("DH1024/Nguyễn Văn An/3/1250000/Chờ duyệt,DH1025/Trần Thị Bích/1/320000/Chờ duyệt,"
                + "DH1026/Lê Minh Cường/2/780000/Đã duyệt", new OrderDAO().getUnexportedOrder().stream()
                .map(o -> o.getCode() + "/" + o.getCustomer().getFullName() + "/" + o.getDetails().size() + "/"
                        + (long) o.getTotalAmount() + "/" + o.getStatusLabel())
                .collect(Collectors.joining(",")));
    }

    @Test
    void approvePendingOrder() throws Exception {
        assertTrue(approve(order(1024)));
        assertEquals("APPROVED/11", TestDB.value("SELECT status || '/' || tblStaffid FROM tblOrder WHERE id = 1024"));
    }

    @Test
    void cancelledOrderCannotBeApproved() throws Exception {
        Order o = new Order();
        o.setId(1011);
        assertFalse(approve(o));                                                   // ngoại lệ 8
        assertEquals("CANCELLED", TestDB.value("SELECT status FROM tblOrder WHERE id = 1011"));
    }

    @Test
    void assignOnlyApprovedOrderAndWorkingStaff() throws Exception {
        Order pending = order(1024);
        pending.setDeliveryStaff(staff("GH03"));
        assertFalse(new OrderDAO().assignDeliveryStaff(pending));                 // chưa duyệt
        Order approved = order(1026);
        DeliveryStaff inactive = new DeliveryStaff();
        inactive.setId(9);
        approved.setDeliveryStaff(inactive);
        assertFalse(new OrderDAO().assignDeliveryStaff(approved));                // GH09 nghỉ việc
        approved.setDeliveryStaff(staff("GH05"));
        assertTrue(new OrderDAO().assignDeliveryStaff(approved));
        assertEquals("5", TestDB.value("SELECT tblDeliveryStaffid FROM tblOrder WHERE id = 1026"));
    }

    @Test
    void exportStandardScenario() throws Exception {
        Order o = order(1024);
        assertTrue(approve(o));
        o.setDeliveryStaff(staff("GH03"));
        assertTrue(new OrderDAO().assignDeliveryStaff(o));
        assertTrue(export(o));
        assertEquals("38,115,50,80", stock());                                     // bước 17
        assertEquals("EXPORTED/11/3/1", TestDB.value("SELECT status || '/' || tblStaffid || '/' || tblDeliveryStaffid"
                + " || '/' || (issueDate IS NOT NULL) FROM tblOrder WHERE id = 1024"));     // bước 18
        assertFalse(export(o));                                                    // ngoại lệ 16a: không xuất lần hai
        assertEquals("38,115,50,80", stock());
    }

    @Test
    void exportWithoutAssignedDeliveryStaffIsRejected() throws Exception {
        Order o = order(1026);                       // đã duyệt nhưng chưa phân công trong CSDL
        o.setDeliveryStaff(staff("GH05"));
        assertFalse(export(o));                                                    // ngoại lệ 16c
        assertEquals("APPROVED", TestDB.value("SELECT status FROM tblOrder WHERE id = 1026"));
    }

    @Test
    void exportOutOfStockChangesNothing() throws Exception {
        TestDB.exec("UPDATE tblProduct SET stockQuantity = 3 WHERE code = 'SP30'");
        Order o = order(1026);
        o.setDeliveryStaff(staff("GH05"));
        assertTrue(new OrderDAO().assignDeliveryStaff(o));
        assertFalse(export(o));                                                    // ngoại lệ 16b
        assertEquals("40,120,60,3", stock());                                      // BR05: không trừ dòng nào
        assertEquals("APPROVED/0", TestDB.value("SELECT status || '/' || (issueDate IS NOT NULL) FROM tblOrder"
                + " WHERE id = 1026"));
    }
}
