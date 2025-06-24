import os
import time
import random
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

# ==== Cấu hình đường dẫn ====
file_path = r"C:\Users\Admin\Downloads\gia-20250424T114732Z-001\gia\GIA 179.xlsx"
sheet_name = "Sheet3"
download_dir = r"C:\Users\Admin\Downloads\gia_reports"
os.makedirs(download_dir, exist_ok=True)

log_path = os.path.join(download_dir, "log.txt")
success_path = os.path.join(download_dir, "success.txt")
fail_path = os.path.join(download_dir, "fail.txt")

# ==== Hàm ghi log ====
def log(msg):
    print(msg)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# ==== Đọc danh sách mã số ====
df = pd.read_excel(file_path, sheet_name=sheet_name)
report_numbers = df["Unnamed: 1"].dropna().astype(str)

# ==== Session requests ====
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# ==== Selenium setup ====
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True)

# ==== Vào trang tra cứu ====
url = "https://www.gia.edu/report-check-landing"
driver.get(url)

WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "reportno")))

# ==== Vòng lặp xử lý ====
for report_no in report_numbers:
    try:
        log(f"\nĐang xử lý: {report_no}")

        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "reportno"))
        )
        input_box.clear()
        input_box.send_keys(report_no)
        time.sleep(random.uniform(0.5, 1.2))

        lookup_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Look Up')]"))
        )
        time.sleep(random.uniform(0.5, 1.5))
        lookup_button.click()

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        if "No results found" in driver.page_source:
            log(f"[KHÔNG TÌM THẤY] {report_no}")
            with open(fail_path, "a", encoding="utf-8") as f:
                f.write(report_no + "\n")
        else:
            log(f"[TÌM THẤY] {report_no}")
            try:
                download_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Download Report PDF')]"))
                )
                time.sleep(random.uniform(0.5, 1.5))
                download_button.click()

                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[-1])

                pdf_url = driver.current_url
                pdf_path = os.path.join(download_dir, f"{report_no}.pdf")

                response = session.get(pdf_url, stream=True, timeout=15)
                with open(pdf_path, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                log(f"[ĐÃ TẢI PDF] {pdf_path}")
                with open(success_path, "a", encoding="utf-8") as f:
                    f.write(report_no + "\n")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                log(f"[LỖI TẢI PDF] {report_no}: {e}")
                with open(fail_path, "a", encoding="utf-8") as f:
                    f.write(report_no + "\n")

        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "reportno")))
        time.sleep(random.uniform(2.5, 6.5))  # Sleep sau mỗi lượt

    except Exception as e:
        log(f"[LỖI TOÀN PHẦN] {report_no}: {e}")
        time.sleep(random.uniform(10, 20))
        with open(fail_path, "a", encoding="utf-8") as f:
            f.write(report_no + "\n")
        continue

driver.quit()
log("\n✅ Hoàn tất tất cả mã số.")
