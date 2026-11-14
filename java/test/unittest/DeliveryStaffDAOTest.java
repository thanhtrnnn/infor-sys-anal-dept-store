package unittest;

import static org.junit.jupiter.api.Assertions.assertEquals;

import dao.DeliveryStaffDAO;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DeliveryStaffDAOTest {
    @BeforeEach
    void db() throws Exception {
        TestDB.fresh();
    }

    @Test
    void workingStaffWithActiveOrders() {
        assertEquals("GH03(1),GH05(0),GH08(3)", new DeliveryStaffDAO().getAvailableDeliveryStaff().stream()
                .map(s -> s.getCode() + "(" + s.getActiveOrderCount() + ")").collect(Collectors.joining(",")));
    }
}
