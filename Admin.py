import sys
import sqlite3
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ===== DATABASE =====
def init_db():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stats(
        day TEXT,
        visits INTEGER
    )
    """)

    cur.execute("DELETE FROM stats")

    data = [
        ("Thứ 2", 12),
        ("Thứ 3", 18),
        ("Thứ 4", 23),
        ("Thứ 5", 32),
        ("Thứ 6", 30),
        ("Thứ 7", 45),
        ("Chủ nhật", 38)
    ]

    cur.executemany("INSERT INTO stats VALUES (?,?)", data)
    conn.commit()
    conn.close()


# ===== CHART =====
class ChartCanvas(FigureCanvas):
    def __init__(self):
        fig = Figure(figsize=(6,3))
        super().__init__(fig)
        self.ax = fig.add_subplot(111)
        self.draw_chart()

    def draw_chart(self):
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM stats")
        rows = cur.fetchall()

        days = [r[0] for r in rows]
        values = [r[1] for r in rows]

        self.ax.clear()

        self.ax.plot(days, values, marker='o', color='#2dd4bf', linewidth=3, label="Lượt khám bệnh")
        self.ax.fill_between(days, values, color='#99f6e4', alpha=0.6)

# 👉 THÊM 2 DÒNG NÀY
        self.ax.set_title("Biểu đồ lượt khám bệnh", fontsize=12)
        self.ax.legend()

        self.ax.set_ylim(0, 50)
        self.ax.grid(True)

        self.draw()


# ===== MAIN WINDOW =====
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.setGeometry(100, 100, 1200, 700)

        self.setStyleSheet("""
QWidget {
    background:#e9f3f6;
    font-family: Arial;
    color:#0f172a;
}

QLabel {
    color:#0f172a;
}

QPushButton {
    color:#0f172a;
}
""")

        self.initUI()

    def initUI(self):
        main = QWidget()
        self.setCentralWidget(main)

        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(15,15,15,15)

        # ===== HEADER (FIX CHUẨN) =====
        header = QFrame()
        header.setStyleSheet("""
        background:white;
        border-radius:12px;
        """)
        header.setFixedHeight(70)

        h_layout = QHBoxLayout(header)

        # LEFT (logo + title)
        logo = QLabel()
        logo.setPixmap(QPixmap("BTL/icons/logo.jpg").scaled(45,45, Qt.AspectRatioMode.KeepAspectRatio))
        print(QPixmap("icons/logo.jpg").isNull())

        title = QLabel("HỆ THỐNG QUẢN LÝ DỊCH VỤ CHĂM SÓC SỨC KHỎE")
        title.setStyleSheet("""
        font-size:20px;
        font-weight:bold;
        color:#0f172a;
        """)

        left_layout = QHBoxLayout()
        left_layout.addWidget(logo)
        left_layout.addWidget(title)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        avatar = QLabel()
        avatar.setPixmap(QPixmap("BTL/icons/avatar.jpg").scaled(35,35, Qt.AspectRatioMode.KeepAspectRatio))
        avatar.setStyleSheet("border-radius:17px;")
        # RIGHT
        user = QLabel("admin")
        user.setStyleSheet("font-weight:bold;")

        logout = QPushButton("Đăng xuất")
        logout.setStyleSheet("""
        background:#ff6b6b;
        color:white;
        border-radius:6px;
        padding:6px 12px;
        """)

        h_layout.addWidget(left_widget)
        h_layout.addStretch()
        h_layout.addWidget(user)
        h_layout.addWidget(avatar)
        h_layout.addWidget(logout)

        main_layout.addWidget(header)

        # ===== BODY =====
        body = QHBoxLayout()

        # ===== SIDEBAR (FULL MENU) =====
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
        background:#e6f0f2;
        border-radius:12px;
        """)

        side_layout = QVBoxLayout(sidebar)

        self.stack = QStackedWidget()

        menus = [
            ("Dashboard","icons/home.png"),
            ("Quản lý bệnh nhân","BTL/icons/bg.jbg"),
            ("Quản lý bác sĩ","icons/doctor.png"),
            ("Quản lý lịch hẹn","icons/calendar.png"),
            ("Quản lý khám bệnh","icons/medical.png"),
            ("Quản lý thuốc","icons/medicine.png"),
            ("Quản lý thanh toán","icons/payment.png"),
            ("Báo cáo & thống kê","icons/report.png"),  
            ("Quản lý hệ thống","icons/setting.png")
        ]
        
        def add_btn(name, icon, index):
            
            btn = QPushButton(name)
            btn.setIcon(QIcon(icon))
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setStyleSheet("""
                QPushButton {
            text-align:left;
        padding:10px;
        border:none;
        font-size:14px;
    }
            QPushButton:hover {
        background:#d1f5f9;
    }
    QPushButton:checked {
        background:#4fd1c5;
        color:white;
        border-radius:8px;
    }
    """)
            btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
            side_layout.addWidget(btn)
            
        
        for i, (text, icon) in enumerate(menus):
             add_btn(text, icon, i)
        side_layout.addStretch()

        # ===== PAGE 1 =====
        page1 = QWidget()
        layout1 = QVBoxLayout(page1)

        title2 = QLabel("Dashboard")
        title2.setStyleSheet("font-size:22px; font-weight:bold;")
        layout1.addWidget(title2)

        # CARDS
        cards = QHBoxLayout()

        def card(title, value, color, icon):
            w = QFrame()
            w.setFixedHeight(110)
            w.setStyleSheet(f"""
                background:{color};
                border-radius:12px;
            """)
            layout = QHBoxLayout(w)

            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(icon).scaled(40,40))

            text_layout = QVBoxLayout()
            t = QLabel(title)
            t.setStyleSheet("color:#334155; font-size:13px;")

            v = QLabel(str(value))
            v.setStyleSheet("font-size:28px; font-weight:bold; color:#0f172a;")
            text_layout.addWidget(t)
            text_layout.addWidget(v)
            layout.addWidget(icon_label)
            layout.addLayout(text_layout)
            return w

        cards.addWidget(card("Tổng bệnh nhân", 120, "#dbeafe", "icons/patient.png"))
        cards.addWidget(card("Tổng bác sĩ", 25, "#dcfce7", "icons/doctor.png"))
        cards.addWidget(card("Lịch hẹn hôm nay", 15, "#fef3c7", "icons/calendar.png"))

        layout1.addLayout(cards)

       

        # CHART BOX
        chart_box = QFrame()
        chart_box.setStyleSheet("background:white; border-radius:10px;")
        chart_layout = QVBoxLayout(chart_box)

        chart_layout.addWidget(ChartCanvas())

        layout1.addWidget(chart_box)

        # ===== PAGE 2 =====
        page2 = QLabel("Trang quản lý bệnh nhân")
        page2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== PAGE 3 =====
        page3 = QLabel("Trang quản lý bác sĩ")
        page3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page4 = QLabel("Trang lịch hẹn")
        page4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page5 = QLabel("Trang khám bệnh")
        page5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page6 = QLabel("Trang thuốc")
        page6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page7 = QLabel("Trang thanh toán")
        page7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page8 = QLabel("Trang báo cáo")
        page8.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page9 = QLabel("Trang hệ thống")
        page9.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ADD PAGES
        self.stack.addWidget(page1)
        self.stack.addWidget(page2)
        self.stack.addWidget(page3)
        self.stack.addWidget(page4)
        self.stack.addWidget(page5)
        self.stack.addWidget(page6)
        self.stack.addWidget(page7)
        self.stack.addWidget(page8)
        self.stack.addWidget(page9)

        # ADD LAYOUT
        body.addWidget(sidebar)
        body.addWidget(self.stack)

        main_layout.addLayout(body)


# ===== RUN =====
if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())