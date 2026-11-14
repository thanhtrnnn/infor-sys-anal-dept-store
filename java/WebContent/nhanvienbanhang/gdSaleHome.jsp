<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="model.*"%>
<%
    SaleStaff saleStaff = (SaleStaff) session.getAttribute("saleStaff");
    if (saleStaff == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
%>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Trang chủ nhân viên bán hàng</title><link rel="stylesheet" href="/css/style.css"></head>
<body>
<h2>CỬA HÀNG BÁCH HÓA TRỰC TUYẾN</h2>
<p>Nhân viên: <b><%= saleStaff.getFullName() %></b> (<%= saleStaff.getCode() %>)</p>
<button onclick="location.href='gdOrderList.jsp'">Duyệt và xuất đơn hàng</button>
</body>
</html>
