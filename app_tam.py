import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt


class BackgroundWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Kích thước cửa sổ
        self.setFixedSize(800, 600)
        self.setWindowTitle("Giao diện PyQt6 với hình nền và icon")

        # Đặt icon góc trái của cửa sổ (window icon)
        self.setWindowIcon(QIcon("resized_image.png"))

        # Đặt màu nền trắng
        self.setStyleSheet("background-color: white;")

        # Hiển thị hình ảnh lớn trên nền
        self.image_label = QLabel(self)
        pixmap = QPixmap("resized_image.png")  # ảnh chính
        scaled_pixmap = pixmap.scaled(4000, 3000, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.move(200, 150)  # căn giữa thủ công

        # Icon nhỏ ở góc trái trên cùng (bên trong giao diện)
        self.icon_label = QLabel(self)
        icon_pixmap = QPixmap("resized_image.png").scaled(1148, 1148, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.icon_label.setPixmap(icon_pixmap)
        self.icon_label.move(1110, 1110)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackgroundWindow()
    window.show()
    sys.exit(app.exec())

