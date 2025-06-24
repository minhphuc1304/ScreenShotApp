def run_gia_downloader(report_numbers):
    import os
    import time
    import random
    import requests
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium_stealth import stealth

    download_dir = r"C:\Users\Admin\Downloads\gia_reports"
    os.makedirs(download_dir, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    # log theo tiến trình
    pid = str(os.getpid())
    log_path = os.path.join(download_dir, f"log_{pid}.txt")

    def log(msg):
        print(msg)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    # Khởi tạo trình duyệt
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

    url = "https://www.gia.edu/report-check-landing"
    driver.get(url)

    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "reportno")))

    for report_no in report_numbers:
        try:
            log(f"PID {pid} | Đang xử lý: {report_no}")
            input_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "reportno"))
            )
            input_box.clear()
            input_box.send_keys(report_no)
            time.sleep(random.uniform(0.5, 1.5))

            lookup_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Look Up')]"))
            )
            time.sleep(random.uniform(0.5, 1.5))
            lookup_button.click()

            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            if "No results found" in driver.page_source:
                log(f"[KHÔNG TÌM THẤY] {report_no}")
            else:
                try:
                    download_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Download Report PDF')]"))
                    )
                    download_button.click()
                    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                    driver.switch_to.window(driver.window_handles[-1])
                    pdf_url = driver.current_url
                    pdf_path = os.path.join(download_dir, f"{report_no}.pdf")
                    response = session.get(pdf_url, stream=True, timeout=15)
                    with open(pdf_path, "wb") as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    log(f"[ĐÃ TẢI] {report_no}")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except Exception as e:
                    log(f"[LỖI TẢI PDF] {report_no}: {e}")

            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "reportno")))
            time.sleep(random.uniform(2, 5))
        except Exception as e:
            log(f"[LỖI CHUNG] {report_no}: {e}")
            time.sleep(random.uniform(10, 20))
            continue

    driver.quit()

## (venv_build_print_app) (base) PS D:\qt_env\print> power shell
