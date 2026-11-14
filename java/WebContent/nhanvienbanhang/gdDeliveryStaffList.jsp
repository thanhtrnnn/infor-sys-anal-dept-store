<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="java.util.*,dao.*,model.*"%>
<%
    SaleStaff saleStaff = (SaleStaff) session.getAttribute("saleStaff");
    if (saleStaff == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
%>
<%
    Order order = (Order) session.getAttribute("order");
    if (order == null) { response.sendRedirect("gdOrderList.jsp"); return; }
    ArrayList<DeliveryStaff> listDeliveryStaff = new DeliveryStaffDAO().getAvailableDeliveryStaff();
    session.setAttribute("listDeliveryStaff", listDeliveryStaff);
%>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Chọn nhân viên giao hàng</title><link rel="stylesheet" href="/css/style.css"></head>
<body>
<h2>CHỌN NHÂN VIÊN GIAO HÀNG CHO ĐƠN <%= order.getCode() %></h2>
<form action="doSaveAssign.jsp" method="post">
<table border="1">
  <tr><th></th><th>Mã NV</th><th>Họ tên</th><th>Số điện thoại</th><th>Khu vực</th><th>Số đơn đang giao</th><th>Trạng thái</th></tr>
  <% for (DeliveryStaff s : listDeliveryStaff) { %>
  <tr>
    <td><input type="radio" name="idDeliveryStaff" value="<%= s.getId() %>"></td>
    <td><%= s.getCode() %></td><td><%= s.getFullName() %></td><td><%= s.getPhone() %></td><td><%= s.getArea() %></td>
    <td><%= s.getActiveOrderCount() %></td><td><%= "AVAILABLE".equals(s.getStatus()) ? "Sẵn sàng" : "Đang giao" %></td>
  </tr>
  <% } %>
</table>
<input type="submit" value="Lưu phân công">
</form>
<button onclick="location.href='gdOrderDetail.jsp'">Quay lại</button>
</body>
</html>
