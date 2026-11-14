<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="java.util.*,dao.*,model.*"%>
<%@ include file="/WEB-INF/common.jspf" %>
<%
    SaleStaff saleStaff = (SaleStaff) session.getAttribute("saleStaff");
    if (saleStaff == null) { response.sendRedirect("../gdLogin.jsp?err=timeout"); return; }
%>
<%
    Order order = (Order) session.getAttribute("order");
    String id = request.getParameter("id");
    if (id != null) {                       // chọn đơn từ danh sách đã lưu trong session
        order = null;
        ArrayList<Order> listOrder = (ArrayList<Order>) session.getAttribute("listOrder");
        if (listOrder != null) {
            for (Order o : listOrder) {
                if (String.valueOf(o.getId()).equals(id)) { order = o; }
            }
        }
        session.setAttribute("order", order);
    }
    if (order == null) { response.sendRedirect("gdOrderList.jsp"); return; }
    order.setDetails(new OrderDetailDAO().getOrderDetailByOrder(order.getId()));
    Customer c = order.getCustomer();
%>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Chi tiết đơn hàng</title><link rel="stylesheet" href="/css/style.css"></head>
<body>
<h2>CHI TIẾT ĐƠN HÀNG <%= order.getCode() %></h2>
<p>Trạng thái: <b><%= order.getStatusLabel() %></b></p>
<p>Khách hàng: <%= c.getFullName() %> - <%= c.getPhone() %> - <%= order.getShippingAddress() %></p>
<table border="1">
  <tr><th>Mã SP</th><th>Tên sản phẩm</th><th>Đơn vị</th><th>Số lượng</th><th>Đơn giá</th><th>Thành tiền</th><th>Tồn kho</th></tr>
  <% for (OrderDetail d : order.getDetails()) { Product p = d.getProduct(); %>
  <tr>
    <td><%= p.getCode() %></td><td><%= p.getName() %></td><td><%= p.getUnit() %></td><td><%= d.getQuantity() %></td>
    <td><%= vnd(d.getUnitPrice()) %></td><td><%= vnd(d.getLineAmount()) %></td><td><%= p.getStockQuantity() %></td>
  </tr>
  <% } %>
  <tr><td></td><td><b>Tổng tiền</b></td><td></td><td></td><td></td><td><b><%= vnd(order.getTotalAmount()) %></b></td><td></td></tr>
</table>
<p>Nhân viên giao hàng: <%= order.getDeliveryStaff() == null ? "(chưa phân công)"
        : order.getDeliveryStaff().getCode() + " - " + order.getDeliveryStaff().getFullName() %></p>
<form action="doApproveOrder.jsp" method="post" style="display:inline"><input type="submit" value="Duyệt đơn"></form>
<button onclick="location.href='gdDeliveryStaffList.jsp'">Chọn NV giao hàng</button>
<form action="doExportOrder.jsp" method="post" style="display:inline"><input type="submit" value="Xác nhận xuất hàng"></form>
<button onclick="location.href='gdInvoicePrint.jsp'">In hóa đơn</button>
<button onclick="location.href='gdOrderList.jsp?action=filter'">Quay lại</button>
</body>
</html>
