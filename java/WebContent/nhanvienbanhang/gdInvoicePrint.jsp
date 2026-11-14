<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="dao.*,model.*"%>
<%@ include file="/WEB-INF/common.jspf" %>
<%
    SaleStaff saleStaff = (SaleStaff) session.getAttribute("saleStaff");
    if (saleStaff == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
%>
<%
    Order order = (Order) session.getAttribute("order");
    if (order == null) { response.sendRedirect("gdOrderList.jsp"); return; }
    Invoice invoice = new InvoiceDAO().getInvoiceDetail(order.getId(), order.getCustomer().getId());
%>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>In hóa đơn</title><link rel="stylesheet" href="/css/style.css"></head>
<body>
<% if (invoice == null || invoice.getIssueDate() == null) { %>
<p>Đơn <%= order.getCode() %> chưa xuất nên chưa có hóa đơn để in</p>
<% } else { Order o = invoice.getOrder(); %>
<h2>HÓA ĐƠN BÁN HÀNG <%= invoice.getCode() %></h2>
<p>Khách hàng: <%= o.getCustomer().getFullName() %> &nbsp; Ngày lập: <%= day(invoice.getIssueDate()) %></p>
<p>Địa chỉ nhận: <%= o.getShippingAddress() %> &nbsp; Mã đơn: <%= o.getCode() %></p>
<table border="1">
  <tr><th>Mã SP</th><th>Tên sản phẩm</th><th>Số lượng</th><th>Đơn giá</th><th>Thành tiền</th></tr>
  <% for (OrderDetail d : o.getDetails()) { %>
  <tr><td><%= d.getProduct().getCode() %></td><td><%= d.getProduct().getName() %></td><td><%= d.getQuantity() %></td>
      <td><%= vnd(d.getUnitPrice()) %></td><td><%= vnd(d.getLineAmount()) %></td></tr>
  <% } %>
  <tr><td></td><td><b>Tổng tiền hóa đơn</b></td><td></td><td></td><td><b><%= vnd(invoice.getTotalAmount()) %></b></td></tr>
</table>
<button onclick="window.print()">In</button>
<% } %>
<button onclick="location.href='gdOrderDetail.jsp'">Quay lại</button>
</body>
</html>
