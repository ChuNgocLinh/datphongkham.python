import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# --- MODULE BÁO CÁO RIÊNG BIỆT ---
class ReportModule(QWidget):
    def __init__(self):
        super().__init__()
        self.db_name = "healthcare_pro.db"
        self.init_ui()

    def init_ui(self):
        # Thiết kế nền và font chữ
        self.setStyleSheet("""
            QWidget { background-color: #f4f7f6; font-family: 'Segoe UI', sans-serif; }
            QFrame#StatCard { 
                background-color: white; 
                border-radius: 20px; 
                border: 1px solid #e0e6ed;
            }
            QLabel#Value { font-size: 26px; font-weight: bold; color: #2d3436; }
            QLabel#Title { font-size: 14px; color: #636e72; font-weight: bold; }
            QTableWidget { 
                background-color: white; 
                border-radius: 15px; 
                border: none;
                gridline-color: #f1f2f6;
            }
            QHeaderView::section { 
                background-color: #f8f9fa; 
                padding: 10px; 
                border: none; 
                border-bottom: 2px solid #3498db;
                font-weight: bold;
            }
            QPushButton#RefreshBtn {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton#RefreshBtn:hover { background-color: #2980b9; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # 1. HEADER CHỨA LOGO VÀ TIÊU ĐỀ
        header_lay = QHBoxLayout()
        header_title = QLabel("📊 HỆ THỐNG THỐNG KÊ & BÁO CÁO")
        header_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        self.btn_refresh = QPushButton("🔄 Làm mới dữ liệu")
        self.btn_refresh.setObjectName("RefreshBtn")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.update_all_stats)
        
        header_lay.addWidget(header_title)
        header_lay.addStretch()
        header_lay.addWidget(self.btn_refresh)
        layout.addLayout(header_lay)

        # 2. HÀNG THẺ THỐNG KÊ (STAT CARDS)
        stats_lay = QHBoxLayout()
        stats_lay.setSpacing(20)

        self.card_rev = self.create_card("💰 TỔNG DOANH THU", "0 VND", "#55efc4")
        self.card_count = self.create_card("📑 SỐ HÓA ĐƠN", "0", "#74b9ff")
        self.card_med = self.create_card("💊 THUỐC TRONG KHO", "0", "#ff7675")

        stats_lay.addWidget(self.card_rev)
        stats_lay.addWidget(self.card_count)
        stats_lay.addWidget(self.card_med)
        layout.addLayout(stats_lay)

        # 3. PHẦN CHI TIẾT (TABLE & TEXT)
        content_lay = QHBoxLayout()
        content_lay.setSpacing(20)

        # Bên trái: Bảng lịch sử giao dịch gần đây
        left_vbox = QVBoxLayout()
        left_vbox.addWidget(QLabel("<b>🕒 Giao dịch gần đây</b>"))
        self.table_recent = QTableWidget(0, 3)
        self.table_recent.setHorizontalHeaderLabels(["Bệnh nhân", "Dịch vụ", "Tiền"])
        self.table_recent.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        left_vbox.addWidget(self.table_recent)
        
        # Bên phải: Cảnh báo thuốc hết hàng
        right_vbox = QVBoxLayout()
        right_vbox.addWidget(QLabel("<b>⚠️ Cảnh báo kho hàng</b>"))
        self.txt_alert = QTextEdit()
        self.txt_alert.setReadOnly(True)
        self.txt_alert.setStyleSheet("background: #fff; border-radius: 15px; border: 1px solid #fab1a0; color: #d63031; padding: 10px;")
        right_vbox.addWidget(self.txt_alert)

        content_lay.addLayout(left_vbox, 2)
        content_lay.addLayout(right_vbox, 1)
        layout.addLayout(content_lay)

        # Khởi tạo dữ liệu
        self.update_all_stats()

    def create_card(self, title, value, color_hex):
        card = QFrame()
        card.setObjectName("StatCard")
        card.setFixedHeight(130)
        
        # Tạo hiệu ứng màu vạch bên trái cho thẻ
        card.setStyleSheet(f"QFrame#StatCard {{ border-left: 8px solid {color_hex}; }}")
        
        v_lay = QVBoxLayout(card)
        lbl_title = QLabel(title)
        lbl_title.setObjectName("Title")
        
        lbl_value = QLabel(value)
        lbl_value.setObjectName("Value")
        
        v_lay.addWidget(lbl_title)
        v_lay.addWidget(lbl_value)
        v_lay.setAlignment(Qt.AlignCenter)
        return card

    def update_all_stats(self):
        """Hàm logic gộp tất cả báo cáo - CHỐNG SẬP 100%"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

            # 1. Thống kê tài chính
            c.execute("SELECT SUM(amount), COUNT(id) FROM payments")
            res = c.fetchone()
            rev = res[0] if res[0] else 0
            count = res[1] if res[1] else 0
            
            # Cập nhật Card (Dùng findChild để tìm đúng Label cần sửa)
            self.card_rev.findChild(QLabel, "Value").setText(f"{rev:,.0f} đ")
            self.card_count.findChild(QLabel, "Value").setText(f"{count} đơn")

            # 2. Thống kê kho
            c.execute("SELECT SUM(quantity) FROM medicines")
            total_med = c.fetchone()[0] or 0
            self.card_med.findChild(QLabel, "Value").setText(f"{total_med} đơn vị")

            # 3. Load bảng giao dịch gần đây (5 cái mới nhất)
            c.execute("SELECT patient_name, service_name, amount FROM payments ORDER BY id DESC LIMIT 5")
            rows = c.fetchall()
            self.table_recent.setRowCount(0)
            for i, r in enumerate(rows):
                self.table_recent.insertRow(i)
                self.table_recent.setItem(i, 0, QTableWidgetItem(str(r[0])))
                self.table_recent.setItem(i, 1, QTableWidgetItem(str(r[1])))
                self.table_recent.setItem(i, 2, QTableWidgetItem(f"{r[2]:,.0f}"))

            # 4. Kiểm tra thuốc sắp hết
            c.execute("SELECT name, quantity FROM medicines WHERE quantity < 10")
            low_meds = c.fetchall()
            alert_msg = ""
            if not low_meds:
                alert_msg = "✅ Kho hàng hiện tại rất đầy đủ."
            else:
                for m in low_meds:
                    alert_msg += f"• {m[0]}: Chỉ còn {m[1]}!\n"
            self.txt_alert.setText(alert_msg)

            conn.close()
        except Exception as e:
            print(f"Lỗi báo cáo: {e}")

# --- CHẠY THỬ NGHIỆM RIÊNG BIỆT ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Tạo một cửa sổ độc lập chỉ để chạy phần báo cáo
    window = QMainWindow()
    window.setWindowTitle("DASHBOARD BÁO CÁO")
    window.resize(1000, 650)
    
    report_widget = ReportModule()
    window.setCentralWidget(report_widget)
    
    window.show()
    sys.exit(app.exec_())