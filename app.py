import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFrame
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App với Background là ảnh logo")
        self.setFixedSize(600, 500)
        self.setStyleSheet("background-color: white;")

        self.setWindowIcon(QIcon("logo.png"))

        # Tạo QLabel hiển thị ảnh nền
        self.background_label = QLabel(self)
        self.background_label.setPixmap(QPixmap("logo.png"))  # ← Thay bằng đường dẫn logo của bạn
        self.background_label.setScaledContents(True)
        self.background_label.resize(self.size())

        # Đảm bảo ảnh nằm dưới cùng
        self.background_label.lower()

        # Widget khác thêm vào đây
        # self.label_text = QLabel("Chào mừng bạn!", self)
        # self.label_text.setStyleSheet("font-size: 24px; color: black; background-color: rgba(255,255,255,180);")
        # self.label_text.move(20, 20)
        # Frame nền trắng viền xám
        frame = QFrame(self)
        frame.setGeometry(10, 10, 580, 480)
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255,255,255,180);
                border: 2px solid gray;
                border-radius: 10px;
            }
        """)
        frame.label_text = QLabel("Chào mừng bạn!", self)
        frame.label_text.setStyleSheet("font-size: 24px; color: black; ")
        frame.label_text.move(20, 20)



    def resizeEvent(self, event):
        self.background_label.resize(self.size())  # Resize background khi cửa sổ thay đổi

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
