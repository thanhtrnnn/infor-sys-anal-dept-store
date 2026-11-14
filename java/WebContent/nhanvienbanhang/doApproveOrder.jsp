<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="java.util.*,dao.*,model.*"%>
<%@ include file="/WEB-INF/common.jspf" %>
<%
    SaleStaff saleStaff = (SaleStaff) session.getAttribute("saleStaff");
    if (saleStaff == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
%>
<%
    Order order = (Order) session.getAttribute("order");
    if (order == null) { response.sendRedirect("gdOrderList.jsp"); return; }
    String oldStatus = order.getStatus();
    order.setStatus("APPROVED");
    order.setSaleStaff(saleStaff);
    order.setApprovedAt(new Date());
    String message;
    if (new OrderDAO().approveOrder(order)) {
        message = "Duyệt đơn thành công";
    } else {
        order.setStatus(oldStatus);
        order.setApprovedAt(null);
        message = "Đơn hàng " + order.getCode() + " đã bị hủy hoặc không còn chờ duyệt, không thể duyệt";
    }
%>
<script type="text/javascript">
    alert('<%= js(message) %>');
    window.location = 'gdOrderDetail.jsp';
</script>
