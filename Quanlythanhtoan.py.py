import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("healthcare_data.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Tạo bảng nếu chưa có
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT,
                service_name TEXT,
                amount TEXT,
                status TEXT DEFAULT 'Chưa thanh toán',
                date TEXT
            )
        """)
        self.conn.commit()
        
        # CƠ CHẾ TỰ SỬA LỖI: Kiểm tra và thêm cột nếu thiếu (Tránh lỗi OperationalError)
        self.cursor.execute("PRAGMA table_info(payments)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'service_name' not in columns:
            self.cursor.execute("ALTER TABLE payments ADD COLUMN service_name TEXT")
        if 'status' not in columns:
            self.cursor.execute("ALTER TABLE payments ADD COLUMN status TEXT DEFAULT 'Chưa thanh toán'")
        self.conn.commit()

class PaymentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("QUẢN LÝ THANH TOÁN - DỊCH VỤ")
        self.resize(1100, 750)
        
        # Giao diện đồng bộ với ảnh mẫu (Bo góc, thanh tìm kiếm ở góc)
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f7fa; }
            QFrame#InputCard { background-color: white; border-radius: 15px; border: 1px solid #dcdde1; }
            QLineEdit, QComboBox { border: 1px solid #dcdde1; border-radius: 8px; padding: 10px; }
            QPushButton#BtnAdd { background-color: #2ecc71; color: white; font-weight: bold; border-radius: 8px; padding: 10px; min-width: 140px; }
            QTableWidget { background-color: white; border-radius: 10px; border: none; }
            QHeaderView::section { background-color: #f8f9fa; font-weight: bold; border-bottom: 2px solid #3498db; padding: 10px; }
        """)

        main_widget = QWidget(); self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget); layout.setContentsMargins(30, 20, 30, 30)

        # Header Search
        h_header = QHBoxLayout()
        title = QLabel("HỆ THỐNG QUẢN LÝ DỊCH VỤ CHĂM SÓC SỨC KHỎE")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2980b9;")
        self.txt_search = QLineEdit(); self.txt_search.setPlaceholderText("🔍 Tìm tên bệnh nhân...")
        self.txt_search.textChanged.connect(self.load_payments)
        h_header.addWidget(title); h_header.addStretch(); h_header.addWidget(self.txt_search)
        layout.addLayout(h_header)

        # Input Card (Nhập liệu)
        self.card = QFrame(); self.card.setObjectName("InputCard"); grid = QGridLayout(self.card)
        self.p_name = QLineEdit(); self.p_service = QLineEdit(); self.p_amount = QLineEdit()
        btn_save = QPushButton("+ Thêm Hóa Đơn"); btn_save.setObjectName("BtnAdd")
        btn_save.clicked.connect(self.add_payment)

        grid.addWidget(QLabel("<b>Tên Bệnh Nhân</b>"), 0, 0)
        grid.addWidget(self.p_name, 1, 0, 1, 3)
        grid.addWidget(QLabel("<b>Dịch vụ / Thuốc</b>"), 2, 0)
        grid.addWidget(self.p_service, 3, 0)
        grid.addWidget(QLabel("<b>Tổng Tiền (VND)</b>"), 2, 1)
        grid.addWidget(self.p_amount, 3, 1)
        grid.addWidget(btn_save, 3, 2)
        layout.addWidget(self.card)

        # Bảng hiển thị
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Bệnh Nhân", "Dịch Vụ", "Trạng Thái", "Số Tiền", "Thao Tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.load_payments()

    def add_payment(self):
        name, svc, amt = self.p_name.text(), self.p_service.text(), self.p_amount.text()
        if name and amt:
            date = datetime.now().strftime("%d/%m/%Y %H:%M")
            self.db.cursor.execute("INSERT INTO payments (patient_name, service_name, amount, status, date) VALUES (?,?,?,?,?)",
                                   (name, svc, amt, "Chưa thanh toán", date))
            self.db.conn.commit()
            self.p_name.clear(); self.p_service.clear(); self.p_amount.clear()
            self.load_payments()

    def load_payments(self):
        search = self.txt_search.text()
        self.db.cursor.execute("SELECT id, patient_name, service_name, status, amount FROM payments WHERE patient_name LIKE ?", (f'%{search}%',))
        rows = self.db.cursor.fetchall()
        self.table.setRowCount(0)
        
        for i, row in enumerate(rows):
            self.table.insertRow(i)
            # Cột 0, 1, 2: ID, Tên, Dịch vụ
            for j in range(3):
                item = QTableWidgetItem(str(row[j]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
            
            # CỘT TRẠNG THÁI (MŨI TÊN XUỐNG - COMBOBOX)
            combo = QComboBox()
            combo.addItems(["Chưa thanh toán", "Đã thanh toán"])
            combo.setCurrentText(row[3])
            combo.currentTextChanged.connect(lambda txt, rid=row[0]: self.update_status(rid, txt))
            self.table.setCellWidget(i, 3, combo)
            
            # Cột Số tiền
            amt_item = QTableWidgetItem(str(row[4]))
            amt_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, amt_item)
            
            # NÚT XÓA (SỬA LỖI LOGIC XÓA)
            btn_del = QPushButton("Xóa"); btn_del.setStyleSheet("background: #e74c3c; color: white; border-radius: 5px;")
            btn_del.clicked.connect(lambda _, rid=row[0]: self.delete_payment(rid))
            self.table.setCellWidget(i, 5, btn_del)

    def update_status(self, rid, status):
        self.db.cursor.execute("UPDATE payments SET status = ? WHERE id = ?", (status, rid))
        self.db.conn.commit()

    def delete_payment(self, rid):
        if QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn xóa hóa đơn này?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.cursor.execute("DELETE FROM payments WHERE id = ?", (rid,))
            self.db.conn.commit()
            self.load_payments()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PaymentApp(); win.show(); sys.exit(app.exec_())