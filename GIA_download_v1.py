import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import pandas as pd
from multiprocessing import Pool
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QLineEdit, QMessageBox, QComboBox
)
from PyQt6.QtCore import QThread, pyqtSignal
import sys
from multiprocessing import Value
import ctypes

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.202 Mobile Safari/537.36"
]

stop_flag = False

def get_random_user_agent():
    return {"User-Agent": random.choice(USER_AGENTS)}

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    return driver

def clean_number(val):
    return int(float(val))

def log(log_path, msg):
    print(msg)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def run_gia_downloader(report_numbers, download_dir, stopflag):
    global stop_flag
    os.makedirs(download_dir, exist_ok=True)
    session = requests.Session()
    session.headers.update(get_random_user_agent())

    pid = str(os.getpid())
    log_path = os.path.join(download_dir, f"log_{pid}.txt")
    log(log_path, f"Bắt đầu session PID {pid}")

    driver = init_driver()
    url = "https://www.gia.edu/report-check-landing"
    driver.get(url)

    for report_no in report_numbers:
        if stop_flag.value:
            log(log_path, "Đã dừng theo yêu cầu người dùng.")
            break
        try:
            report_no = clean_number(report_no)
            log(log_path, f"PID {pid} | Đang xử lý: {report_no}")
            input_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "reportno"))
            )
            input_box.clear()
            input_box.send_keys(report_no)
            time.sleep(random.uniform(0.5, 1.5))

            lookup_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Look Up')]"))
            )
            lookup_button.click()

            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            if "No results found" in driver.page_source:
                log(log_path, f"[KHÔNG TÌM THẤY] {report_no}")
            else:
                download_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Download Report PDF')]"))
                )
                download_button.click()

                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[-1])

                pdf_url = driver.current_url
                pdf_path = os.path.join(download_dir, f"{report_no}.pdf")
                response = session.get(pdf_url, stream=True, timeout=15)

                if response.status_code == 200:
                    with open(pdf_path, "wb") as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    log(log_path, f"[ĐÃ TẢI] {report_no}")
                else:
                    log(log_path, f"[LỖI HTTP {response.status_code}] {report_no}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "reportno")))
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            log(log_path, f"[LỖI CHUNG] {report_no}: {e}")
            time.sleep(random.uniform(10, 20))
            continue
    driver.quit()

class GiaDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GIA PDF Downloader")
        self.resize(500, 300)
        layout = QVBoxLayout()

        self.input_path_edit = QLineEdit()
        self.output_path_edit = QLineEdit()
        self.sheet_combo = QComboBox()
        self.column_combo = QComboBox()

        self.input_btn = QPushButton("Chọn file Excel đầu vào")
        self.input_btn.clicked.connect(self.select_input)

        self.output_btn = QPushButton("Chọn thư mục lưu PDF")
        self.output_btn.clicked.connect(self.select_output)

        self.download_btn = QPushButton("Bắt đầu tải báo cáo")
        self.download_btn.clicked.connect(self.start_download)

        self.stop_btn = QPushButton("Dừng lại")
        self.stop_btn.clicked.connect(self.stop_download)
        self.stop_btn.setEnabled(False)

        self.threads_label = QLabel(f"Đang dùng 4 luồng cố định")

        layout.addWidget(QLabel("File Excel đầu vào:"))
        layout.addWidget(self.input_path_edit)
        layout.addWidget(self.input_btn)

        layout.addWidget(QLabel("Chọn Sheet:"))
        layout.addWidget(self.sheet_combo)

        layout.addWidget(QLabel("Chọn cột chứa mã báo cáo:"))
        layout.addWidget(self.column_combo)

        layout.addWidget(QLabel("Thư mục lưu file PDF:"))
        layout.addWidget(self.output_path_edit)
        layout.addWidget(self.output_btn)

        layout.addWidget(self.threads_label)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.stop_btn)

        self.setLayout(layout)

    def select_input(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file Excel", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            self.input_path_edit.setText(file_path)
            try:
                xls = pd.ExcelFile(file_path)
                self.sheet_combo.clear()
                self.sheet_combo.addItems(xls.sheet_names)
                self.sheet_combo.currentIndexChanged.connect(self.update_columns)
                self.update_columns()
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không đọc được file Excel: {e}")

    def update_columns(self):
        sheet_name = self.sheet_combo.currentText()
        file_path = self.input_path_edit.text()
        if not file_path or not sheet_name:
            return
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            self.column_combo.clear()
            self.column_combo.addItems(df.columns.astype(str))
        except Exception as e:
            self.column_combo.clear()
            QMessageBox.warning(self, "Lỗi", f"Không đọc được sheet để lấy danh sách cột: {e}")

    def select_output(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu PDF")
        if folder_path:
            self.output_path_edit.setText(folder_path)

    def stop_download(self):
        global stop_flag
        stop_flag.value = True
        QMessageBox.information(self, "Dừng", "Quá trình tải sẽ được dừng sau khi tiến trình hiện tại hoàn thành.")

    def start_download(self):
        global stop_flag
        stop_flag = False
        input_path = self.input_path_edit.text()
        output_dir = self.output_path_edit.text()
        selected_sheet = self.sheet_combo.currentText()
        selected_column = self.column_combo.currentText()

        if not input_path or not output_dir or not selected_sheet or not selected_column:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn đầy đủ file, sheet, cột và thư mục đầu ra.")
            return

        try:
            df = pd.read_excel(input_path, sheet_name=selected_sheet)
            report_numbers = df[selected_column].dropna().astype(str).tolist()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lấy danh sách mã báo cáo: {e}")
            return

        if not report_numbers:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy mã báo cáo trong cột đã chọn.")
            return

        self.input_btn.setEnabled(False)
        self.output_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        num_processes = 4
        chunks = [report_numbers[i::num_processes] for i in range(num_processes)]

        os.makedirs(output_dir, exist_ok=True)

        with Pool(processes=num_processes) as pool:
            # pool.starmap(run_gia_downloader, [(chunk, output_dir) for chunk in chunks])
            pool.starmap(run_gia_downloader, [(chunk, output_dir, stop_flag) for chunk in chunks])


        self.input_btn.setEnabled(True)
        self.output_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        QMessageBox.information(self, "Hoàn thành", "Đã tải xong tất cả báo cáo!")

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    stop_flag = Value(ctypes.c_bool, False)
    app = QApplication(sys.argv)
    window = GiaDownloaderApp()
    window.show()
    sys.exit(app.exec())


# pyinstaller --noconfirm --onefile --windowed --add-data "/Users/lephuc/anaconda3/envs/gia_pdf_app/lib/python3.11/site-packages/selenium_stealth/js:selenium_stealth/js" GIA_download_v1.py
# pyinstaller --noconfirm --onefile --windowed --icon=/Users/lephuc/Downloads/resized_image.icns --add-data "/Users/lephuc/anaconda3/envs/gia_pdf_app/lib/python3.11/site-packages/selenium_stealth/js:selenium_stealth/js" GIA_download_v1.py
# /Users/lephuc/Downloads/resized_image.icns