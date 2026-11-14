package unittest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dao.OrderDetailDAO;
import dao.ProductDAO;
import java.util.ArrayList;
import model.OrderDetail;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ProductDAOTest {
    @BeforeEach
    void db() throws Exception {
        TestDB.fresh();
    }

    @Test
    void enoughStock() {
        assertTrue(new ProductDAO().checkStock(new OrderDetailDAO().getOrderDetailByOrder(1024)));
    }

    @Test
    void notEnoughStockReportsCurrentStock() throws Exception {
        TestDB.exec("UPDATE tblProduct SET stockQuantity = 3 WHERE code = 'SP30'");
        ArrayList<OrderDetail> d = new OrderDetailDAO().getOrderDetailByOrder(1026);
        assertFalse(new ProductDAO().checkStock(d));
        assertEquals(3, d.get(1).getProduct().getStockQuantity());
    }

    @Test
    void decreaseStockOfEveryLine() throws Exception {
        assertTrue(new ProductDAO().decreaseStock(new OrderDetailDAO().getOrderDetailByOrder(1024)));
        assertEquals("38,115,50", TestDB.value("SELECT group_concat(stockQuantity) FROM (SELECT stockQuantity FROM"
                + " tblProduct WHERE id IN (7, 15, 22) ORDER BY id)"));
    }

    @Test
    void decreaseStockRefusesToGoNegative() throws Exception {
        TestDB.exec("UPDATE tblProduct SET stockQuantity = 1 WHERE code = 'SP07'");
        assertFalse(new ProductDAO().decreaseStock(new OrderDetailDAO().getOrderDetailByOrder(1024)));
        assertEquals("1", TestDB.value("SELECT stockQuantity FROM tblProduct WHERE code = 'SP07'"));
    }
}
