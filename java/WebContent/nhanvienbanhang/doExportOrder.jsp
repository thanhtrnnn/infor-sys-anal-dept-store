<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="java.util.*,dao.*,model.*"%>
<%@ include file="/WEB-INF/common.jspf" %>
<%
    SaleStaff saleStaff = (SaleStaff) session.getAttribute("saleStaff");
    if (saleStaff == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
%>
<%
    Order order = (Order) session.getAttribute("order");
    if (order == null) { response.sendRedirect("gdOrderList.jsp"); return; }
    String message;
    if (order.getDeliveryStaff() == null) {                                   // ngoại lệ 16c
        message = "Vui lòng chọn nhân viên giao hàng trước khi xuất đơn";
    } else {
        String oldStatus = order.getStatus();
        order.setStatus("EXPORTED");
        order.setSaleStaff(saleStaff);
        order.setExportedAt(new Date());
        if (new OrderDAO().exportOrder(order)) {
            message = "Xuất hàng thành công cho đơn " + order.getCode();
        } else {
            order.setStatus(oldStatus);
            order.setExportedAt(null);
            if (!new ProductDAO().checkStock(order.getDetails())) {              // ngoại lệ 16b
                StringBuilder missing = new StringBuilder();
                for (OrderDetail d : order.getDetails()) {
                    if (d.getProduct().getStockQuantity() < d.getQuantity()) {
                        missing.append(missing.length() == 0 ? "" : "; ").append(d.getProduct().getCode()).append(" - ")
                               .append(d.getProduct().getName()).append(": cần ").append(d.getQuantity())
                               .append(", còn ").append(d.getProduct().getStockQuantity());
                    }
                }
                message = "Không đủ hàng để xuất đơn " + order.getCode() + ": " + missing;
            } else {                                                            // ngoại lệ 16a / 8
                message = "Đơn hàng " + order.getCode() + " đã được xuất hoặc không ở trạng thái cho phép xuất";
            }
        }
    }
%>
<script type="text/javascript">
    alert('<%= js(message) %>');
    window.location = 'gdOrderDetail.jsp';
</script>
