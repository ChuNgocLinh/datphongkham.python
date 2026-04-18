import sys
import sqlite3
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# --- CHỐNG SẬP APP ---
def exception_hook(exctype, value, traceback):
    QMessageBox.critical(None, "Lỗi Hệ Thống", f"Phát hiện lỗi: {value}")
sys.excepthook = exception_hook

# --- QUẢN LÝ DỮ LIỆU ---
class Database:
    def __init__(self):
        self.db_name = "healthcare_final_v4.db" 
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, quantity INTEGER, price REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, patient_name TEXT, service_name TEXT, 
            amount REAL, method TEXT, status TEXT, date TEXT)""")
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
            raise e

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PHẦN MỀM QUẢN LÝ Y TẾ")
        self.resize(1300, 850)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #f8f9fa; }
            QListWidget { background-color: #2c3e50; border: none; color: white; }
            QListWidget::item { padding: 25px; border-bottom: 1px solid #34495e; font-size: 15px; }
            QListWidget::item:selected { background-color: #3498db; border-left: 8px solid #1abc9c; }
            QFrame#Card { background: white; border-radius: 15px; border: 1px solid #dcdde1; }
            QPushButton#ActionBtn { background: #3498db; color: white; border-radius: 8px; font-weight: bold; padding: 12px; }
            QTableWidget { background: white; border-radius: 10px; border: none; }
            QHeaderView::section { background: #34495e; color: white; padding: 10px; border: none; }
            QLineEdit, QComboBox { border: 1px solid #bdc3c7; border-radius: 6px; padding: 8px; background: white; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)

        # SIDEBAR
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.addItem("💊 Quản Lý Thuốc")
        self.sidebar.addItem("💳 Quản Lý Thanh Toán")
        self.sidebar.addItem("📊 Báo Cáo & Thống Kê")
        self.sidebar.addItem("⚙️ Quản Lý Hệ Thống")
        self.sidebar.currentRowChanged.connect(self.switch_page)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.ui_medicine())
        self.pages.addWidget(self.ui_payment())
        self.pages.addWidget(self.ui_report())
        self.pages.addWidget(self.ui_system())

        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages)
        self.sidebar.setCurrentRow(0)

    def create_header(self, title):
        head = QWidget(); head.setFixedHeight(100)
        l = QHBoxLayout(head)
        lbl_logo = QLabel()
        if os.path.exists("logo.png"):
            lbl_logo.setPixmap(QPixmap("logo.png").scaled(80, 80, Qt.KeepAspectRatio))
        else:
            lbl_logo.setText("🏥")
            lbl_logo.setStyleSheet("font-size: 40px; background: #dfe6e9; border-radius: 40px; padding: 10px;")
        
        lbl_title = QLabel(f"<h2 style='color: #2c3e50;'>{title}</h2>")
        l.addWidget(lbl_logo); l.addWidget(lbl_title); l.addStretch()
        return head

    def switch_page(self, i):
        self.pages.setCurrentIndex(i)
        if i == 0: self.load_meds()
        if i == 1: self.load_pays()
        if i == 2: self.refresh_report()
        if i == 3: self.refresh_system()

    # ========================== 1. TRANG THUỐC ==========================
    def ui_medicine(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(30,10,30,30)
        l.addWidget(self.create_header("QUẢN LÝ KHO THUỐC"))
        
        card = QFrame(); card.setObjectName("Card"); card.setFixedHeight(180); cl = QHBoxLayout(card)
        sub_logo = QLabel("LOGO"); sub_logo.setFixedSize(100, 100); sub_logo.setStyleSheet("background:#f1f2f6; border-radius:15px; border:2px dashed #ccc;"); sub_logo.setAlignment(Qt.AlignCenter)
        cl.addWidget(sub_logo)
        
        form = QVBoxLayout()
        self.m_n = QLineEdit(); self.m_n.setPlaceholderText("Tên thuốc...")
        row2 = QHBoxLayout()
        self.m_q = QLineEdit(); self.m_q.setPlaceholderText("Số lượng")
        self.m_p = QLineEdit(); self.m_p.setPlaceholderText("Giá nhập")
        btn = QPushButton("NHẬP KHO"); btn.setObjectName("ActionBtn"); btn.clicked.connect(self.add_med)
        row2.addWidget(self.m_q); row2.addWidget(self.m_p); row2.addWidget(btn)
        form.addWidget(self.m_n); form.addLayout(row2); cl.addLayout(form, 1)

        self.table_med = QTableWidget(0, 4); self.table_med.setHorizontalHeaderLabels(["ID", "Tên Thuốc", "SL", "Giá"])
        self.table_med.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(card); l.addWidget(self.table_med)
        return w

    # ========================== 2. TRANG THANH TOÁN (MỚI) ==========================
    def ui_payment(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(30,10,30,30)
        l.addWidget(self.create_header("QUẢN LÝ THANH TOÁN"))
        
        card = QFrame(); card.setObjectName("Card"); f = QFormLayout(card); f.setContentsMargins(25,25,25,25)
        
        self.p_n = QLineEdit(); self.p_n.setPlaceholderText("Tên bệnh nhân...")
        self.p_s = QLineEdit(); self.p_s.setPlaceholderText("Khám bệnh / Mua thuốc...")
        self.p_a = QLineEdit(); self.p_a.setPlaceholderText("0.00")
        
        # Thêm Phương thức & Trạng thái khi tạo
        self.p_method = QComboBox(); self.p_method.addItems(["Tiền mặt", "Mã QR (Chuyển khoản)"])
        self.p_status = QComboBox(); self.p_status.addItems(["Chưa thanh toán", "Đã thanh toán"])
        
        btn = QPushButton("TẠO HÓA ĐƠN"); btn.setObjectName("ActionBtn"); btn.clicked.connect(self.add_pay)
        
        f.addRow("Bệnh nhân:", self.p_n)
        f.addRow("Dịch vụ:", self.p_s)
        f.addRow("Số tiền (VND):", self.p_a)
        f.addRow("Thanh toán bằng:", self.p_method)
        f.addRow("Trạng thái:", self.p_status)
        f.addRow(btn)

        self.table_pay = QTableWidget(0, 6); self.table_pay.setHorizontalHeaderLabels(["ID", "Bệnh Nhân", "Dịch Vụ", "Số Tiền", "Hình Thức", "Trạng Thái"])
        self.table_pay.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(card); l.addWidget(self.table_pay)
        return w

    # ========================== LOGIC XỬ LÝ ==========================
    def add_med(self):
        n, q, p = self.m_n.text(), self.m_q.text(), self.m_p.text()
        if n and q and p:
            self.db.run("INSERT INTO medicines (name, quantity, price) VALUES (?,?,?)", (n, int(q), float(p)))
            self.load_meds(); self.m_n.clear(); self.m_q.clear(); self.m_p.clear()

    def load_meds(self):
        data = self.db.run("SELECT * FROM medicines", is_fetch=True)
        self.table_med.setRowCount(0)
        for i, r in enumerate(data):
            self.table_med.insertRow(i)
            self.table_med.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.table_med.setItem(i, 1, QTableWidgetItem(str(r[1])))
            self.table_med.setItem(i, 2, QTableWidgetItem(str(r[2])))
            self.table_med.setItem(i, 3, QTableWidgetItem(f"{r[3]:,.0f} Đ"))

    def add_pay(self):
        n, s, a = self.p_n.text(), self.p_s.text(), self.p_a.text()
        m, st = self.p_method.currentText(), self.p_status.currentText()
        if n and a:
            dt = datetime.now().strftime("%d/%m/%Y %H:%M")
            self.db.run("INSERT INTO payments (patient_name, service_name, amount, method, status, date) VALUES (?,?,?,?,?,?)", 
                        (n, s, float(a), m, st, dt))
            self.load_pays()
            self.p_n.clear(); self.p_s.clear(); self.p_a.clear()
            QMessageBox.information(self, "Thành công", f"Đã lưu hóa đơn {st} qua {m}")

    def load_pays(self):
        data = self.db.run("SELECT id, patient_name, service_name, amount, method, status FROM payments", is_fetch=True)
        self.table_pay.setRowCount(0)
        for i, r in enumerate(data):
            self.table_pay.insertRow(i)
            for j in range(3): self.table_pay.setItem(i, j, QTableWidgetItem(str(r[j])))
            self.table_pay.setItem(i, 3, QTableWidgetItem(f"{r[3]:,.0f} Đ"))
            self.table_pay.setItem(i, 4, QTableWidgetItem(str(r[4]))) # Hình thức
            
            cb = QComboBox()
            cb.addItems(["Chưa thanh toán", "Đã thanh toán"])
            cb.setCurrentText(r[5])
            cb.currentTextChanged.connect(lambda txt, rid=r[0]: self.db.run("UPDATE payments SET status=? WHERE id=?", (txt, rid)))
            self.table_pay.setCellWidget(i, 5, cb)

    # ========================== 3. BÁO CÁO & 4. HỆ THỐNG ==========================
    def ui_report(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(30,10,30,30)
        l.addWidget(self.create_header("BÁO CÁO & THỐNG KÊ"))
        self.rep_txt = QTextEdit(); self.rep_txt.setReadOnly(True); self.rep_txt.setStyleSheet("border-radius:15px; padding:20px; font-size:16px;")
        l.addWidget(self.rep_txt)
        return w

    def refresh_report(self):
        rev = self.db.run("SELECT SUM(amount) FROM payments WHERE status='Đã thanh toán'", is_fetch=True)[0][0] or 0
        qr_rev = self.db.run("SELECT SUM(amount) FROM payments WHERE status='Đã thanh toán' AND method LIKE '%QR%'", is_fetch=True)[0][0] or 0
        cash_rev = self.db.run("SELECT SUM(amount) FROM payments WHERE status='Đã thanh toán' AND method='Tiền mặt'", is_fetch=True)[0][0] or 0
        cnt = self.db.run("SELECT COUNT(*) FROM payments", is_fetch=True)[0][0] or 0
        
        self.rep_txt.setText(f"""
📋 BÁO CÁO HOẠT ĐỘNG HỆ THỐNG
--------------------------------------
💰 TỔNG DOANH THU: {rev:,.0f} VND

Trong đó:
💵 Tiền mặt: {cash_rev:,.0f} VND
📲 Chuyển khoản QR: {qr_rev:,.0f} VND

📑 Tổng số hóa đơn đã tạo: {cnt}
⏰ Thời gian cập nhật: {datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}
        """)

    def ui_system(self):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(30,10,30,30)
        l.addWidget(self.create_header("QUẢN LÝ HỆ THỐNG"))
        card = QFrame(); card.setObjectName("Card"); vl = QVBoxLayout(card)
        self.sys_info = QLabel("Đang kiểm tra dữ liệu..."); self.sys_info.setStyleSheet("font-size: 16px;")
        vl.addWidget(self.sys_info); vl.addStretch()
        l.addWidget(card); l.addStretch()
        return w

    def refresh_system(self):
        m_count = self.db.run("SELECT COUNT(*) FROM medicines", is_fetch=True)[0][0]
        p_count = self.db.run("SELECT COUNT(*) FROM payments", is_fetch=True)[0][0]
        self.sys_info.setText(f"✅ Trạng thái: Đã kết nối Cơ sở dữ liệu\n\n📦 Tổng loại thuốc: {m_count}\n💳 Tổng số giao dịch: {p_count}\n📂 File DB: {self.db.db_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec_())