<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="java.util.*,dao.*,model.*"%>
<%@ include file="/WEB-INF/common.jspf" %>
<%
    Customer customer = (Customer) session.getAttribute("customer");
    if (customer == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
    ArrayList<Invoice> listInvoice = new InvoiceDAO().getInvoiceByCustomer(customer.getId());
    session.setAttribute("listInvoice", listInvoice);
%>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Theo dõi hóa đơn</title><link rel="stylesheet" href="/css/style.css"></head>
<body>
<h2>THEO DÕI HÓA ĐƠN</h2>
<p>Khách hàng: <%= customer.getFullName() %> (<%= customer.getCode() %>)</p>
<% if (listInvoice.isEmpty()) { %>
<p>Bạn chưa có hóa đơn nào</p>
<% } else { %>
<table border="1">
  <tr><th>Mã HĐ</th><th>Mã đơn</th><th>Ngày đặt</th><th>Số mặt hàng</th><th>Tổng tiền</th><th>Trạng thái</th></tr>
  <% for (Invoice inv : listInvoice) { Order o = inv.getOrder(); %>
  <tr>
    <td><a href="gdInvoiceDetail.jsp?id=<%= inv.getId() %>"><%= inv.getCode() %></a></td>
    <td><%= o.getCode() %></td>
    <td><%= day(o.getOrderDate()) %></td>
    <td><%= o.getDetails().size() %></td>
    <td><%= vnd(inv.getTotalAmount()) %></td>
    <td><%= o.getStatusLabel() %></td>
  </tr>
  <% } %>
</table>
<% } %>
<button onclick="location.href='gdCustomerHome.jsp'">Quay lại</button>
</body>
</html>
