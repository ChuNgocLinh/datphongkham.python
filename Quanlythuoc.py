import sys
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# --- 1. LỚP QUẢN LÝ CƠ SỞ DỮ LIỆU (Giúp lưu dữ liệu vĩnh viễn) ---
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("medicine_data.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                quantity TEXT,
                price TEXT
            )
        """)
        self.conn.commit()

    def fetch_all(self):
        self.cursor.execute("SELECT * FROM medicines")
        return self.cursor.fetchall()

    def add_medicine(self, name, qty, price):
        self.cursor.execute("INSERT INTO medicines (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
        self.conn.commit()

    def update_medicine(self, m_id, name, qty, price):
        self.cursor.execute("UPDATE medicines SET name=?, quantity=?, price=? WHERE id=?", (name, qty, price, m_id))
        self.conn.commit()

    def delete_medicine(self, m_id):
        self.cursor.execute("DELETE FROM medicines WHERE id=?", (m_id,))
        self.conn.commit()

    def search_medicine(self, query):
        self.cursor.execute("SELECT * FROM medicines WHERE name LIKE ?", ('%' + query + '%',))
        return self.cursor.fetchall()

# --- 2. HỘP THOẠI CHỈNH SỬA (Pop-up khi nhấn nút Sửa) ---
class EditDialog(QDialog):
    def __init__(self, name, qty, price, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chỉnh sửa thông tin thuốc")
        self.setFixedWidth(400)
        layout = QVBoxLayout(self)
        
        self.txt_name = QLineEdit(name)
        self.txt_qty = QLineEdit(qty)
        self.txt_price = QLineEdit(price)

        layout.addWidget(QLabel("Tên Thuốc:"))
        layout.addWidget(self.txt_name)
        layout.addWidget(QLabel("Số Lượng:"))
        layout.addWidget(self.txt_qty)
        layout.addWidget(QLabel("Giá (VND):"))
        layout.addWidget(self.txt_price)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return self.txt_name.text(), self.txt_qty.text(), self.txt_price.text()

# --- 3. ỨNG DỤNG CHÍNH (Giao diện giống ảnh mẫu) ---
class MedicineApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Hệ Thống Quản Lý Dịch Vụ Chăm Sóc Sức Khỏe")
        self.setGeometry(100, 100, 1200, 850)
        
        # Style tổng thể (Fix lỗi mất khung và màu sắc)
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f7fa; }
            QLineEdit {
                border: 1px solid #dcdde1;
                border-radius: 8px;
                padding: 10px;
                background-color: #ffffff;
                color: #2f3640;
            }
            QLineEdit:focus { border: 2px solid #3498db; }
            QLabel { font-family: 'Segoe UI'; color: #2c3e50; }
            QTableWidget { background-color: #ffffff; border-radius: 12px; border: none; }
            QHeaderView::section { background-color: #ffffff; padding: 12px; border: none; border-bottom: 2px solid #3498db; font-weight: bold; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 20, 30, 30)

        # Header
        header = QHBoxLayout()
        lbl_logo = QLabel()
        lbl_logo.setPixmap(self.create_medical_logo(45))
        lbl_title = QLabel("HỆ THỐNG QUẢN LÝ DỊCH VỤ CHĂM SÓC SỨC KHỎE")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2980b9; margin-left: 10px;")
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Tìm kiếm tên thuốc...")
        self.txt_search.setFixedWidth(300)
        self.txt_search.textChanged.connect(self.handle_search)

        header.addWidget(lbl_logo); header.addWidget(lbl_title); header.addStretch(); header.addWidget(self.txt_search)
        main_layout.addLayout(header)

        # Khung nhập liệu (Input Card)
        input_card = QFrame()
        input_card.setStyleSheet("background-color: white; border-radius: 15px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setColor(QColor(0,0,0,30)); shadow.setOffset(0, 4)
        input_card.setGraphicsEffect(shadow)

        grid = QGridLayout(input_card)
        grid.setContentsMargins(25, 25, 25, 25)
        
        grid.addWidget(QLabel("<b>Tên Thuốc</b>"), 0, 0)
        self.txt_name = QLineEdit(); grid.addWidget(self.txt_name, 1, 0, 1, 3)

        grid.addWidget(QLabel("<b>Số Lượng</b>"), 2, 0)
        self.txt_qty = QLineEdit(); grid.addWidget(self.txt_qty, 3, 0)

        grid.addWidget(QLabel("<b>Giá (VND)</b>"), 2, 1)
        self.txt_price = QLineEdit(); grid.addWidget(self.txt_price, 3, 1)

        btn_add = QPushButton("+ Thêm Thuốc")
        btn_add.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; border-radius: 8px; padding: 12px;")
        btn_add.clicked.connect(self.handle_add)
        grid.addWidget(btn_add, 3, 2)

        lbl_side_logo = QLabel(); lbl_side_logo.setPixmap(self.create_medical_logo(100))
        grid.addWidget(lbl_side_logo, 0, 4, 4, 1)
        main_layout.addWidget(input_card)

        # Bảng dữ liệu
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Tên Thuốc", "Số Lượng", "Giá (VND)", "Thao Tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table)

        self.refresh_table_data()

    def create_medical_logo(self, size):
        pix = QPixmap(size, size); pix.fill(Qt.transparent)
        p = QPainter(pix); p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#ffffff")); p.setPen(QPen(QColor("#3498db"), 2)); p.drawEllipse(2, 2, size-4, size-4)
        p.setBrush(QColor("#3498db")); p.setPen(Qt.NoPen)
        w = size // 5; center = size // 2
        p.drawRect(center - w//2, size//4, w, size//2); p.drawRect(size//4, center - w//2, size//2, w)
        p.end(); return pix

    def refresh_table_data(self, data=None):
        if data is None: data = self.db.fetch_all()
        self.table.setRowCount(0)
        for i, row in enumerate(data):
            self.table.insertRow(i)
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
            actions = QWidget(); lay = QHBoxLayout(actions); lay.setContentsMargins(10,2,10,2)
            btn_edit = QPushButton("Sửa"); btn_edit.setStyleSheet("background: #3498db; color: white; border-radius: 4px; padding: 5px;")
            btn_edit.clicked.connect(lambda _, r=row: self.handle_edit(r))
            btn_del = QPushButton("Xóa"); btn_del.setStyleSheet("background: #e74c3c; color: white; border-radius: 4px; padding: 5px;")
            btn_del.clicked.connect(lambda _, r=row[0]: self.handle_delete(r))
            lay.addWidget(btn_edit); lay.addWidget(btn_del)
            self.table.setCellWidget(i, 4, actions)

    def handle_add(self):
        n, q, p = self.txt_name.text(), self.txt_qty.text(), self.txt_price.text()
        if n and q and p:
            self.db.add_medicine(n, q, p)
            self.refresh_table_data(); self.txt_name.clear(); self.txt_qty.clear(); self.txt_price.clear()

    def handle_edit(self, row_data):
        dialog = EditDialog(row_data[1], row_data[2], row_data[3], self)
        if dialog.exec_() == QDialog.Accepted:
            new_n, new_q, new_p = dialog.get_data()
            self.db.update_medicine(row_data[0], new_n, new_q, new_p)
            self.refresh_table_data()

    def handle_delete(self, m_id):
        self.db.delete_medicine(m_id); self.refresh_table_data()

    def handle_search(self):
        results = self.db.search_medicine(self.txt_search.text())
        self.refresh_table_data(results)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MedicineApp()
    win.show()
    sys.exit(app.exec_())