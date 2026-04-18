import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# --- 1. QUẢN LÝ DỮ LIỆU ---
class Database:
    def __init__(self):
        self.db_name = "healthcare_pro.db"
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS medicines (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, quantity INTEGER, price REAL)")
        c.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_name TEXT, service_name TEXT, amount REAL, date TEXT)")
        conn.commit()
        conn.close()

    def run(self, sql, params=(), is_fetch=False):
        try:
            conn = sqlite3.connect(self.db_name, timeout=10)
            c = conn.cursor()
            c.execute(sql, params)
            res = c.fetchall() if is_fetch else None
            conn.commit()
            conn.close()
            return res
        except Exception as e:
            print(f"Lỗi DB: {e}")
            return [] if is_fetch else None

# --- 2. MODULE BÁO CÁO TÁCH BIỆT (DASHBOARD) ---
class DashboardModule(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header
        header = QLabel("📊 HỆ THỐNG THỐNG KÊ CHI TIẾT")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)

        # Stats Cards Layout
        stats_lay = QHBoxLayout()
        self.card_rev = self.create_card("TỔNG DOANH THU", "0 VND", "#1abc9c")
        self.card_med = self.create_card("THUỐC TRONG KHO", "0", "#3498db")
        self.card_low = self.create_card("CẢNH BÁO HẾT", "0", "#e74c3c")
        
        stats_lay.addWidget(self.card_rev)
        stats_lay.addWidget(self.card_med)
        stats_lay.addWidget(self.card_low)
        layout.addLayout(stats_lay)

        # Bottom Area
        content_lay = QHBoxLayout()
        
        # Lịch sử giao dịch
        self.table_recent = QTableWidget(0, 3)
        self.table_recent.setHorizontalHeaderLabels(["Bệnh nhân", "Dịch vụ", "Tiền"])
        self.table_recent.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_recent.setStyleSheet("border-radius: 12px; background: white; border: 1px solid #ddd;")
        
        # Cảnh báo văn bản
        self.txt_alert = QTextEdit()
        self.txt_alert.setReadOnly(True)
        self.txt_alert.setStyleSheet("background: #fff5f5; border-radius: 12px; border: 1px solid #feb2b2; color: #c53030; padding: 10px;")
        
        content_lay.addWidget(self.table_recent, 2)
        content_lay.addWidget(self.txt_alert, 1)
        layout.addLayout(content_lay)

        self.refresh_stats()

    def create_card(self, title, value, color):
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet(f"background: {color}; border-radius: 15px;")
        v = QVBoxLayout(card)
        t_lbl = QLabel(title); t_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        v_lbl = QLabel(value); v_lbl.setStyleSheet("color: white; font-weight: 800; font-size: 22px;")
        v_lbl.setObjectName("value")
        v.addWidget(t_lbl); v.addWidget(v_lbl)
        v.setAlignment(Qt.AlignCenter)
        return card

    def refresh_stats(self):
        # 1. Doanh thu
        res = self.db.run("SELECT SUM(amount) FROM payments", is_fetch=True)
        rev = res[0][0] if res[0][0] else 0
        self.card_rev.findChild(QLabel, "value").setText(f"{rev:,.0f} Đ")

        # 2. Kho
        res_med = self.db.run("SELECT SUM(quantity) FROM medicines", is_fetch=True)
        med_count = res_med[0][0] or 0
        self.card_med.findChild(QLabel, "value").setText(f"{med_count} SP")

        # 3. Cảnh báo hết
        low_meds = self.db.run("SELECT name, quantity FROM medicines WHERE quantity < 5", is_fetch=True)
        self.card_low.findChild(QLabel, "value").setText(str(len(low_meds)))
        
        alert_msg = "⚠️ CẢNH BÁO KHO:\n\n"
        for m in low_meds: alert_msg += f"• {m[0]}: Còn {m[1]}\n"
        self.txt_alert.setText(alert_msg)

        # 4. Giao dịch gần đây
        recent = self.db.run("SELECT patient_name, service_name, amount FROM payments ORDER BY id DESC LIMIT 5", is_fetch=True)
        self.table_recent.setRowCount(0)
        for i, r in enumerate(recent):
            self.table_recent.insertRow(i)
            self.table_recent.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.table_recent.setItem(i, 1, QTableWidgetItem(str(r[1])))
            self.table_recent.setItem(i, 2, QTableWidgetItem(f"{r[2]:,.0f}"))

# --- 3. GIAO DIỆN CHÍNH ---
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.edit_dlg = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🏥 HỆ THỐNG QUẢN LÝ TỔNG THỂ")
        self.resize(1200, 800)
        
        # Style chung toàn bộ App
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f2f5; }
            QFrame#MainCard { background: white; border-radius: 15px; border: 1px solid #e0e0e0; }
            QPushButton#AddBtn { background: #2ecc71; color: white; border-radius: 8px; font-weight: bold; padding: 10px; }
            QPushButton#PayBtn { background: #3498db; color: white; border-radius: 8px; font-weight: bold; padding: 10px; }
            QLineEdit { border: 1px solid #ddd; border-radius: 6px; padding: 8px; }
            QTableWidget { background: white; border-radius: 10px; gridline-color: #f1f2f6; }
            QHeaderView::section { background: #2c3e50; color: white; font-weight: bold; border: none; padding: 5px; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0,0,0,0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.addItems(["📦 Quản Lý Kho", "💳 Thanh Toán", "📊 Báo Cáo"])
        self.sidebar.setStyleSheet("""
            QListWidget { background: #2c3e50; border: none; color: white; font-size: 15px; outline: none; }
            QListWidget::item { padding: 25px; border-bottom: 1px solid #34495e; }
            QListWidget::item:selected { background: #3498db; border-left: 6px solid #1abc9c; }
        """)
        self.sidebar.currentRowChanged.connect(self.switch_page)

        # Pages
        self.pages = QStackedWidget()
        self.pages.addWidget(self.ui_medicine())
        self.pages.addWidget(self.ui_payment())
        
        # PHẦN BÁO CÁO RIÊNG BIỆT
        self.dashboard = DashboardModule(self.db)
        self.pages.addWidget(self.dashboard)

        main_lay.addWidget(self.sidebar)
        main_lay.addWidget(self.pages)
        self.load_meds()

    def ui_medicine(self):
        w = QWidget(); l = QVBoxLayout(w)
        
        card = QFrame(); card.setObjectName("MainCard"); card.setFixedHeight(130)
        f_lay = QGridLayout(card)
        self.in_n, self.in_q, self.in_p = QLineEdit(), QLineEdit(), QLineEdit()
        self.in_q.setValidator(QIntValidator()); self.in_p.setValidator(QDoubleValidator())
        
        btn = QPushButton("➕ THÊM THUỐC MỚI"); btn.setObjectName("AddBtn")
        btn.clicked.connect(self.add_med)
        
        f_lay.addWidget(QLabel("<b>Tên thuốc:</b>"), 0, 0); f_lay.addWidget(self.in_n, 1, 0)
        f_lay.addWidget(QLabel("<b>Số lượng:</b>"), 0, 1); f_lay.addWidget(self.in_q, 1, 1)
        f_lay.addWidget(QLabel("<b>Giá nhập:</b>"), 0, 2); f_lay.addWidget(self.in_p, 1, 2)
        f_lay.addWidget(btn, 1, 3)
        
        self.table_med = QTableWidget(0, 5)
        self.table_med.setHorizontalHeaderLabels(["ID", "Tên thuốc", "SL", "Giá", "Hành động"])
        self.table_med.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        l.addWidget(QLabel("<h2>📦 QUẢN LÝ KHO THUỐC</h2>"))
        l.addWidget(card); l.addWidget(self.table_med)
        return w

    def ui_payment(self):
        w = QWidget(); l = QVBoxLayout(w)
        card = QFrame(); card.setObjectName("MainCard")
        f = QFormLayout(card)
        self.pn, self.ps, self.pa = QLineEdit(), QLineEdit(), QLineEdit()
        btn = QPushButton("✅ LƯU HÓA ĐƠN"); btn.setObjectName("PayBtn")
        btn.clicked.connect(self.add_pay)
        f.addRow("Bệnh nhân:", self.pn); f.addRow("Dịch vụ:", self.ps); f.addRow("Số tiền:", self.pa); f.addRow(btn)
        
        l.addWidget(QLabel("<h2>💳 THANH TOÁN DỊCH VỤ</h2>"))
        l.addWidget(card); l.addStretch()
        return w

    # --- LOGIC ---
    def switch_page(self, i):
        self.pages.setCurrentIndex(i)
        if i == 0: self.load_meds()
        if i == 2: self.dashboard.refresh_stats()

    def load_meds(self):
        data = self.db.run("SELECT * FROM medicines", is_fetch=True)
        self.table_med.setRowCount(0)
        for i, r in enumerate(data):
            self.table_med.insertRow(i)
            for j in range(4): self.table_med.setItem(i, j, QTableWidgetItem(str(r[j])))
            
            btns = QWidget(); bl = QHBoxLayout(btns); bl.setContentsMargins(0,0,0,0)
            be = QPushButton("Sửa"); bd = QPushButton("Xóa")
            be.setStyleSheet("background:#f1c40f;"); bd.setStyleSheet("background:#e74c3c; color:white;")
            be.clicked.connect(lambda checked, row=r: self.open_edit(row))
            bd.clicked.connect(lambda checked, rid=r[0]: self.delete_med(rid))
            bl.addWidget(be); bl.addWidget(bd)
            self.table_med.setCellWidget(i, 4, btns)

    def open_edit(self, data):
        self.edit_dlg = QDialog(self)
        self.edit_dlg.setWindowTitle("Sửa")
        lay = QFormLayout(self.edit_dlg)
        en = QLineEdit(str(data[1])); eq = QLineEdit(str(data[2])); ep = QLineEdit(str(data[3]))
        lay.addRow("Tên:", en); lay.addRow("SL:", eq); lay.addRow("Giá:", ep)
        btn = QPushButton("Cập nhật"); btn.clicked.connect(self.edit_dlg.accept)
        lay.addRow(btn)
        
        if self.edit_dlg.exec_():
            self.db.run("UPDATE medicines SET name=?, quantity=?, price=? WHERE id=?", (en.text(), eq.text(), ep.text(), data[0]))
            self.load_meds()

    def delete_med(self, rid):
        if QMessageBox.question(self, "Xóa", "Xác nhận xóa?") == QMessageBox.Yes:
            self.db.run("DELETE FROM medicines WHERE id=?", (rid,))
            self.load_meds()

    def add_med(self):
        n, q, p = self.in_n.text(), self.in_q.text(), self.in_p.text()
        if n:
            self.db.run("INSERT INTO medicines (name, quantity, price) VALUES (?,?,?)", (n, q, p))
            self.in_n.clear(); self.in_q.clear(); self.in_p.clear(); self.load_meds()

    def add_pay(self):
        n, s, a = self.pn.text(), self.ps.text(), self.pa.text()
        if n:
            t = datetime.now().strftime("%d/%m %H:%M")
            self.db.run("INSERT INTO payments (patient_name, service_name, amount, date) VALUES (?,?,?,?)", (n, s, a, t))
            self.pn.clear(); self.ps.clear(); self.pa.clear()
            QMessageBox.information(self, "Xong", "Đã lưu hóa đơn!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainApp()
    win.show()
    sys.exit(app.exec_())