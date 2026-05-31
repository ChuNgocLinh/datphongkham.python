# Database scripts

## SQL Server

Thư mục `sqlserver/` chứa các script dùng cho cấu hình chính của bài tập lớn:

1. Chuẩn bị database `khambenh` và các bảng nghiệp vụ cơ bản.
2. Chạy `sqlserver/sqlserver_notifications.sql` để bổ sung bảng cấu hình người dùng và thông báo.
3. Chạy `sqlserver/seed_sqlserver.sql` khi cần nạp lại dữ liệu mẫu.

Lưu ý: `seed_sqlserver.sql` xóa dữ liệu nghiệp vụ hiện có trước khi thêm dữ liệu mẫu. Chỉ chạy khi chủ động đặt lại dữ liệu demo.

## MySQL

Thư mục `mysql/` chỉ được giữ để hỗ trợ môi trường MySQL cũ và `docker-compose.yml`.
