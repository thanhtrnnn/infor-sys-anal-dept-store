package unittest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dao.OrderDetailDAO;
import java.util.ArrayList;
import java.util.stream.Collectors;
import model.OrderDetail;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class OrderDetailDAOTest {
    @BeforeEach
    void db() throws Exception {
        TestDB.fresh();
    }

    @Test
    void orderWithThreeLines() {
        ArrayList<OrderDetail> d = new OrderDetailDAO().getOrderDetailByOrder(1024);
        assertEquals("SP07x2@40=500000,SP15x5@120=300000,SP22x10@60=450000", d.stream()
                .map(x -> x.getProduct().getCode() + "x" + x.getQuantity() + "@" + x.getProduct().getStockQuantity()
                        + "=" + (long) x.getLineAmount())
                .collect(Collectors.joining(",")));
    }

    @Test
    void unknownOrderGivesEmptyList() {
        assertTrue(new OrderDetailDAO().getOrderDetailByOrder(9999).isEmpty());
    }
}
