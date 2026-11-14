package unittest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dao.InvoiceDAO;
import java.util.Date;
import java.util.stream.Collectors;
import model.Invoice;
import model.Order;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class InvoiceDAOTest {
    @BeforeEach
    void db() throws Exception {
        TestDB.fresh();
    }

    @Test
    void invoicesOfCustomerNewestFirst() {
        assertEquals("HD1024/Chờ duyệt/3/1250000,HD1011/Đã hủy/1/175000,HD0987/Đã giao/1/540000",
                new InvoiceDAO().getInvoiceByCustomer(1).stream()
                        .map(i -> i.getCode() + "/" + i.getOrder().getStatusLabel() + "/"
                                + i.getOrder().getDetails().size() + "/" + (long) i.getTotalAmount())
                        .collect(Collectors.joining(",")));
    }

    @Test
    void customerWithoutInvoices() throws Exception {
        TestDB.exec("DELETE FROM tblOrderDetail WHERE tblOrderid IN (SELECT id FROM tblOrder WHERE tblCustomerid = 3)");
        TestDB.exec("DELETE FROM tblOrder WHERE tblCustomerid = 3");
        assertTrue(new InvoiceDAO().getInvoiceByCustomer(3).isEmpty());
    }

    @Test
    void detailOfOwnInvoice() {
        Invoice inv = new InvoiceDAO().getInvoiceDetail(987, 1);
        assertEquals("HD0987", inv.getCode());
        assertEquals(1, inv.getOrder().getDetails().size());
        assertEquals("Ngô Thị Hà", inv.getOrder().getDeliveryStaff().getFullName());
    }

    @Test
    void invoiceOfAnotherCustomerIsHidden() {
        assertNull(new InvoiceDAO().getInvoiceDetail(1025, 1));   // BR01
        assertNull(new InvoiceDAO().getInvoiceDetail(9999, 1));
    }

    @Test
    void issueInvoiceOnlyOnce() throws Exception {
        Order o = new Order();
        o.setId(1026);
        o.setExportedAt(new Date());
        assertTrue(new InvoiceDAO().issueInvoice(o));
        assertFalse(new InvoiceDAO().issueInvoice(o));
        assertEquals("1", TestDB.value("SELECT COUNT(*) FROM tblOrder WHERE id = 1026 AND issueDate IS NOT NULL"));
    }
}
