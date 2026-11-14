package model;

import java.util.Date;

/** Khách hàng. */
public class Customer extends Member {
    private String code;
    private Date memberSince;

    public Customer() {
        super();
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public Date getMemberSince() {
        return memberSince;
    }

    public void setMemberSince(Date memberSince) {
        this.memberSince = memberSince;
    }
}
