<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Đăng nhập</title><link rel="stylesheet" href="/css/style.css"></head>
<body>
<h2>Đăng nhập</h2>
<% if ("fail".equals(request.getParameter("err"))) { %><p>Sai tên đăng nhập hoặc mật khẩu</p><% } %>
<% if ("timeout".equals(request.getParameter("err"))) { %><p>Hết phiên làm việc, vui lòng đăng nhập lại</p><% } %>
<form action="doLogin.jsp" method="post">
  Tên đăng nhập: <input type="text" name="username"><br>
  Mật khẩu: <input type="password" name="password"><br>
  <input type="submit" value="Đăng nhập">
</form>
</body>
</html>
