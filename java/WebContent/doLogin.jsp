<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" import="dao.*,model.*"%>
<%
    request.setCharacterEncoding("UTF-8");
    Member m = new MemberDAO().checkLogin(request.getParameter("username"), request.getParameter("password"));
    if (m instanceof Customer) {
        session.setAttribute("customer", m);
        response.sendRedirect("khachhang/gdCustomerHome.jsp");
    } else if (m instanceof SaleStaff) {
        session.setAttribute("saleStaff", m);
        response.sendRedirect("nhanvienbanhang/gdSaleHome.jsp");
    } else {
        response.sendRedirect("gdLogin.jsp?err=fail");
    }
%>
