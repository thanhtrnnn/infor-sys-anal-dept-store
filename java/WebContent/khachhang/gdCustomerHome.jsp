<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="model.*"%>
<%
    Customer customer = (Customer) session.getAttribute("customer");
    if (customer == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
%>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Trang chủ khách hàng</title><link rel="stylesheet" href="/css/style.css"></head>
<body>
<h2>CỬA HÀNG BÁCH HÓA TRỰC TUYẾN</h2>
<p>Xin chào, <b><%= customer.getFullName() %></b> (<%= customer.getCode() %>)</p>
<button onclick="location.href='gdInvoiceList.jsp'">Theo dõi hóa đơn</button>
</body>
</html>
