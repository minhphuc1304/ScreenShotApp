from multiprocessing import Pool, cpu_count
import numpy as np
import os

# ===== CHIA DANH SÁCH MÃ SỐ ====
def split_list(lst, n):
    return np.array_split(lst, n)

# ===== HÀM XỬ LÝ RIÊNG CHO MỖI TIẾN TRÌNH ====
def process_sublist(report_list):
    from gia_downloader import run_gia_downloader  # tách logic chính ra file riêng
    run_gia_downloader(report_list)

if __name__ == "__main__":
    import pandas as pd

    file_path = r"C:\Users\Admin\Downloads\IN gia 114V 2703.xlsx"
    df = pd.read_excel(file_path, sheet_name="Sheet1")
    report_numbers = df["Unnamed: 1"].dropna().astype(str).tolist()

    num_processes = min(cpu_count(), 4)  # chỉ nên dùng 2-4 process cho trình duyệt
    chunks = split_list(report_numbers, num_processes)

    with Pool(processes=num_processes) as pool:
        pool.map(process_sublist, chunks)

    print("✅ Đã xử lý xong toàn bộ danh sách.")
