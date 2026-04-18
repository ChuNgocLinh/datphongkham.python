# datphongkham.python
# 🏥 HỆ THỐNG QUẢN LÝ DỊCH VỤ CHĂM SÓC SỨC KHỎE

## 📌 Giới thiệu

Hệ thống quản lý dịch vụ chăm sóc sức khỏe được xây dựng nhằm hỗ trợ các cơ sở y tế (phòng khám, bệnh viện) trong việc quản lý thông tin bệnh nhân, bác sĩ, lịch hẹn, khám bệnh, thuốc, thanh toán và báo cáo thống kê.

Hệ thống giúp:

* Tăng hiệu quả quản lý
* Giảm sai sót thủ công
* Nâng cao trải nghiệm người dùng
* Hỗ trợ ra quyết định nhanh chóng

---

## 🎯 Mục tiêu hệ thống

* Quản lý toàn bộ quy trình khám chữa bệnh
* Tối ưu hóa việc đặt lịch và xử lý bệnh nhân
* Lưu trữ dữ liệu an toàn và dễ truy xuất
* Xây dựng giao diện thân thiện, hiện đại

---

## 🧠 Chức năng chính

HỆ THỐNG QUẢN LÝ DỊCH VỤ CHĂM SÓC SỨC KHỎE
│
├── Quản lý bệnh nhân
│   ├── Thêm bệnh nhân
│   ├── Sửa thông tin bệnh nhân
│   ├── Xóa bệnh nhân
│   ├── Tìm kiếm bệnh nhân
│   └── Xem lịch sử khám bệnh
│
├── Quản lý bác sĩ
│   ├── Thêm bác sĩ
│   ├── Sửa thông tin bác sĩ
│   ├── Xóa bác sĩ
│   ├── Tìm kiếm bác sĩ
│   └── Xem lịch làm việc
│
├── Quản lý lịch hẹn
│   ├── Đặt lịch khám
│   ├── Sửa lịch hẹn
│   ├── Hủy lịch hẹn
│   ├── Xem lịch hẹn
│   └── Nhắc lịch khám
│
├── Quản lý khám bệnh
│   ├── Tạo hồ sơ khám
│   ├── Nhập chẩn đoán
│   ├── Kê đơn thuốc
│   ├── Lưu kết quả khám
│   └── Xem lịch sử khám
│
├── Quản lý thuốc
│   ├── Thêm thuốc
│   ├── Sửa thông tin thuốc
│   ├── Xóa thuốc
│   ├── Tìm kiếm thuốc
│   └── Kiểm tra tồn kho thuốc
│
├── Quản lý thanh toán
│   ├── Tạo hóa đơn
│   ├── Xác nhận thanh toán
│   ├── Kiểm tra trạng thái thanh toán
│   ├── Hủy thanh toán
│   └── Xem lịch sử thanh toán
│
├── Quản lý dịch vụ
│   ├── Thêm dịch vụ khám
│   ├── Sửa dịch vụ
│   ├── Xóa dịch vụ
│   ├── Tìm kiếm dịch vụ
│   └── Cập nhật giá dịch vụ
│
├── Quản lý nhân viên
│   ├── Thêm nhân viên
│   ├── Sửa thông tin nhân viên
│   ├── Xóa nhân viên
│   ├── Phân quyền
│   └── Tìm kiếm nhân viên
│
├── Quản lý báo cáo & thống kê
│   ├── Thống kê số lượt khám
│   ├── Thống kê doanh thu
│   ├── Thống kê bệnh nhân
│   ├── Báo cáo thuốc sử dụng
│   └── Báo cáo dịch vụ phổ biến
│
└── Quản lý hệ thống
    ├── Đăng nhập
    ├── Đăng xuất
    ├── Đổi mật khẩu
    └── Phân quyền người dùng

---

## 🏗️ Kiến trúc hệ thống

Hệ thống được xây dựng theo mô hình:

👉 **MVC (Model - View - Controller)**

```
Model      → Xử lý dữ liệu (Database)
View       → Giao diện người dùng (Tkinter)
Controller → Điều khiển logic
```

---

## 🛠️ Công nghệ sử dụng

| Thành phần    | Công nghệ                    |
| ------------- | ---------------------------- |
| Ngôn ngữ      | Python                       |
| Giao diện     | QT Designer                  |
| Cơ sở dữ liệu | SQLite                       |
| IDE           | Visual Studio Code / PyCharm |

---

## 📂 Cấu trúc thư mục

```
healthcare_management/
│
├── main.py
├── database.py
│
├── models/
├── views/
├── controllers/
│
└── assets/
```

---

## 🚀 Cài đặt & chạy chương trình

### 1. Clone project

```bash
git clone <link-repo>
cd healthcare_management
```

### 2. Cài đặt (nếu cần)

```bash
pip install -r requirements.txt
```

### 3. Chạy chương trình

```bash
python main.py
```

---

## 🖥️ Giao diện hệ thống

* Dashboard tổng quan
* Sidebar điều hướng
* Bảng dữ liệu rõ ràng
* Giao diện thân thiện, dễ sử dụng

---

## 🔐 Phân quyền người dùng

| Vai trò   | Quyền                       |
| --------- | --------------------------- |
| Admin     | Toàn quyền                  |
| Nhân viên | Quản lý bệnh nhân, lịch hẹn |
| Bác sĩ    | Xem & cập nhật hồ sơ khám   |

---

## 📈 Hướng phát triển

* Phát triển web (Flask/Django)
* Tích hợp AI hỗ trợ chẩn đoán
* Kết nối hệ thống bệnh viện
* Ứng dụng mobile

---

## 📜 Giấy phép

Dự án phục vụ mục đích học tập và nghiên cứu.
