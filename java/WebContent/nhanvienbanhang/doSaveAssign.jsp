<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="java.util.*,dao.*,model.*"%>
<%@ include file="/WEB-INF/common.jspf" %>
<%
    SaleStaff saleStaff = (SaleStaff) session.getAttribute("saleStaff");
    if (saleStaff == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
%>
<%
    Order order = (Order) session.getAttribute("order");
    ArrayList<DeliveryStaff> list = (ArrayList<DeliveryStaff>) session.getAttribute("listDeliveryStaff");
    if (order == null || list == null) { response.sendRedirect("gdOrderList.jsp"); return; }
    DeliveryStaff chosen = null;
    for (DeliveryStaff s : list) {
        if (String.valueOf(s.getId()).equals(request.getParameter("idDeliveryStaff"))) { chosen = s; }
    }
    String message;
    if (chosen == null) {
        message = "Vui lòng chọn một nhân viên giao hàng";
    } else {
        DeliveryStaff old = order.getDeliveryStaff();
        order.setDeliveryStaff(chosen);
        if (new OrderDAO().assignDeliveryStaff(order)) {
            message = "Phân công thành công: " + chosen.getCode() + " - " + chosen.getFullName();
        } else {
            order.setDeliveryStaff(old);
            message = "Không thể phân công nhân viên giao hàng cho đơn " + order.getCode();
        }
    }
%>
<script type="text/javascript">
    alert('<%= js(message) %>');
    window.location = 'gdOrderDetail.jsp';
</script>
