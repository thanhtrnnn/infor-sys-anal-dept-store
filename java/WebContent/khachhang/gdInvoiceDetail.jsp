<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="dao.*,model.*"%>
<%@ include file="/WEB-INF/common.jspf" %>
<%
    Customer customer = (Customer) session.getAttribute("customer");
    if (customer == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
    Invoice invoice = null;
    try {
        invoice = new InvoiceDAO().getInvoiceDetail(Integer.parseInt(request.getParameter("id")), customer.getId());
    } catch (NumberFormatException e) {
        invoice = null;
    }
%>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Chi tiết hóa đơn</title><link rel="stylesheet" href="/css/style.css"></head>
<body>
<% if (invoice == null) { %>
<p>Không tìm thấy hóa đơn</p>
<% } else { Order o = invoice.getOrder(); %>
<h2>CHI TIẾT HÓA ĐƠN <%= invoice.getCode() %></h2>
<p>Mã đơn: <%= o.getCode() %> &nbsp; Ngày đặt: <%= day(o.getOrderDate()) %></p>
<p>Ngày lập: <%= day(invoice.getIssueDate()) %> &nbsp; Địa chỉ nhận: <%= o.getShippingAddress() %></p>
<table border="1">
  <tr><th>Mã SP</th><th>Tên sản phẩm</th><th>Số lượng</th><th>Đơn giá</th><th>Thành tiền</th></tr>
  <% for (OrderDetail d : o.getDetails()) { %>
  <tr>
    <td><%= d.getProduct().getCode() %></td><td><%= d.getProduct().getName() %></td>
    <td><%= d.getQuantity() %></td><td><%= vnd(d.getUnitPrice()) %></td><td><%= vnd(d.getLineAmount()) %></td>
  </tr>
  <% } %>
  <tr><td></td><td><b>Tổng tiền</b></td><td></td><td></td><td><b><%= vnd(invoice.getTotalAmount()) %></b></td></tr>
</table>
<p>Trạng thái hiện tại: <b><%= o.getStatusLabel() %></b> <%= o.getExportedAt() == null ? "" : "(" + time(o.getExportedAt()) + ")" %></p>
<% if (o.getDeliveryStaff() != null) { %>
<p>Nhân viên giao hàng: <%= o.getDeliveryStaff().getFullName() %> - <%= o.getDeliveryStaff().getPhone() %></p>
<% } %>
<% } %>
<button onclick="location.href='gdInvoiceList.jsp'">Quay lại</button>
</body>
</html>
