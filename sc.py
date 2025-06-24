import sys
import os
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, QRect, QUrl
from PyQt6.QtGui import QGuiApplication, QPixmap, QPainter, QDesktopServices, QIcon


class ScreenshotOverlay(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

        # Icon (không hiện vì là Frameless + Fullscreen, nhưng vẫn giữ nếu bạn muốn dùng lại)
        self.setWindowIcon(QIcon(r"C:\Users\Admin\Desktop\gia_code\logo.png"))

        self.setWindowTitle("Chọn vùng chụp")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setWindowOpacity(0.3)
        self.setStyleSheet("background-color: gray;")
        self.start = None
        self.end = None
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = self.start
        self.update()

    def mouseMoveEvent(self, event):
        if self.start:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.start and self.end:
            self.close()
            rect = QRect(self.start, self.end).normalized()
            self.callback(rect)

    def paintEvent(self, event):
        if self.start and self.end:
            painter = QPainter(self)
            painter.setPen(Qt.GlobalColor.red)
            painter.drawRect(QRect(self.start, self.end))


class ScreenshotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ứng dụng Chụp Màn Hình - PyQt6")
        self.setWindowIcon(QIcon(r"C:\Users\Admin\Desktop\gia_code\logo2.png"))
        self.setFixedSize(400, 250)

        from pathlib import Path

        default_dir = Path.home() / "Documents" / "ScreenshotApp"
        self.save_folder = str(default_dir)
        os.makedirs(self.save_folder, exist_ok=True)


        layout = QVBoxLayout()

        # Hiển thị thư mục hiện tại
        self.folder_label = QLabel(f"📁 Thư mục lưu: {self.save_folder}")
        self.folder_label.setWordWrap(True)
        layout.addWidget(self.folder_label)

        # Nút chọn thư mục
        self.choose_btn = QPushButton("📂 Chọn Thư Mục Lưu")
        self.choose_btn.clicked.connect(self.choose_folder)
        layout.addWidget(self.choose_btn)

        # Nút chọn vùng chụp
        self.capture_btn = QPushButton("📸 Chọn Vùng Chụp")
        self.capture_btn.clicked.connect(self.start_capture)
        layout.addWidget(self.capture_btn)

        # Nút mở thư mục
        self.open_folder_btn = QPushButton("📂 Mở Thư Mục Lưu")
        self.open_folder_btn.clicked.connect(self.open_folder)
        layout.addWidget(self.open_folder_btn)

        # Nút thoát
        self.exit_btn = QPushButton("❌ Thoát")
        self.exit_btn.clicked.connect(self.close)
        layout.addWidget(self.exit_btn)

        self.setLayout(layout)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu")
        if folder:
            self.save_folder = folder
            self.folder_label.setText(f"📁 Thư mục lưu: {self.save_folder}")
            QMessageBox.information(self, "Thông báo", f"Đã chọn: {self.save_folder}")

    def start_capture(self):
        self.hide()
        self.overlay = ScreenshotOverlay(self.capture_area)
        self.overlay.show()

    def capture_area(self, rect):
        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())

        if screenshot.isNull():
            QMessageBox.critical(self, "Lỗi", "Không thể chụp vùng đã chọn.")
            self.show()
            return

        # Lưu ảnh
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.save_folder, f"screenshot_{timestamp}.png")
        screenshot.save(file_path, "png")

        QMessageBox.information(self, "Thành công", f"Đã lưu ảnh:\n{file_path}")
        self.show()

    def open_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.save_folder))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotApp()
    window.show()
    sys.exit(app.exec())
# pyinstaller --noconfirm --onefile --windowed --icon=logo2.ico sc.py