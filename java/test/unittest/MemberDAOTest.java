package unittest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;

import dao.MemberDAO;
import model.Customer;
import model.Member;
import model.SaleStaff;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MemberDAOTest {
    @BeforeEach
    void db() throws Exception {
        TestDB.fresh();
    }

    @Test
    void customerLogsIn() {
        Member m = new MemberDAO().checkLogin("an", "123456");
        assertInstanceOf(Customer.class, m);
        assertEquals("KH01", ((Customer) m).getCode());
        assertEquals("Nguyễn Văn An", m.getFullName());
    }

    @Test
    void saleStaffLogsIn() {
        Member m = new MemberDAO().checkLogin("lan", "123456");
        assertInstanceOf(SaleStaff.class, m);
        assertEquals("NV01", ((SaleStaff) m).getCode());
    }

    @Test
    void wrongPasswordIsRejected() {
        assertNull(new MemberDAO().checkLogin("an", "sai"));
        assertNull(new MemberDAO().checkLogin("khongco", "123456"));
    }
}
