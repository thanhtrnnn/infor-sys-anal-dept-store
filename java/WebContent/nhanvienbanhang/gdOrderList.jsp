<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="java.util.*,dao.*,model.*"%>
<%@ include file="/WEB-INF/common.jspf" %>
<%
    SaleStaff saleStaff = (SaleStaff) session.getAttribute("saleStaff");
    if (saleStaff == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
%>
<%
    ArrayList<Order> listOrder = null;
    if ("filter".equals(request.getParameter("action"))) {   // trang submit gọi chính nó xử lí
        listOrder = new OrderDAO().getUnexportedOrder();
        session.setAttribute("listOrder", listOrder);
    }
%>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Danh sách đơn hàng</title><link rel="stylesheet" href="/css/style.css"></head>
<body>
<h2>DANH SÁCH ĐƠN HÀNG</h2>
<form action="gdOrderList.jsp" method="get">
  Trạng thái: <select name="status"><option value="UNEXPORTED">Chưa xuất</option></select>
  <input type="hidden" name="action" value="filter">
  <input type="submit" value="Lọc">
</form>
<% if (listOrder != null) { %>
<table border="1">
  <tr><th>Mã đơn</th><th>Khách hàng</th><th>Ngày đặt</th><th>Số mặt hàng</th><th>Tổng tiền</th><th>Trạng thái</th></tr>
  <% for (Order o : listOrder) { %>
  <tr>
    <td><a href="gdOrderDetail.jsp?id=<%= o.getId() %>"><%= o.getCode() %></a></td>
    <td><%= o.getCustomer().getFullName() %></td><td><%= day(o.getOrderDate()) %></td>
    <td><%= o.getDetails().size() %></td><td><%= vnd(o.getTotalAmount()) %></td><td><%= o.getStatusLabel() %></td>
  </tr>
  <% } %>
</table>
<% } %>
<button onclick="location.href='gdSaleHome.jsp'">Quay lại</button>
</body>
</html>
