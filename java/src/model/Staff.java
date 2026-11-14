package model;

/** Nhân viên. */
public class Staff extends Member {
    private String code;
    private String position;

    public Staff() {
        super();
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getPosition() {
        return position;
    }

    public void setPosition(String position) {
        this.position = position;
    }
}
