import os
import pandas as pd

# Đường dẫn
folder_path = r"D:\gia_1"  # Thư mục chứa file
excel_path = r"C:\Users\Admin\Downloads\gia-20250424T114732Z-001\gia\GIA 179.xlsx"  # File Excel
output_txt = r"C:\Users\Admin\Downloads\kq.txt" # File kết quả

# Lấy danh sách file trong thư mục (bỏ đuôi)
files_in_folder = [
    os.path.splitext(f)[0]
    for f in os.listdir(folder_path)
    if os.path.isfile(os.path.join(folder_path, f))
]

# Đọc file Excel không có tiêu đề
df = pd.read_excel(excel_path, header=None)
file_names_in_excel = df[1].astype(str).tolist()  # Cột thứ 2 (mã/tên file)
file_names_in_excel_clean = [os.path.splitext(name)[0] for name in file_names_in_excel]

# So sánh
missing_in_folder = [f for f in file_names_in_excel_clean if f not in files_in_folder]
extra_in_folder = [f for f in files_in_folder if f not in file_names_in_excel_clean]

# Xuất kết quả ra file txt
with open(output_txt, 'w', encoding='utf-8') as f:
    f.write("📁 Có trong Excel nhưng KHÔNG có trong thư mục:\n")
    for item in missing_in_folder:
        f.write(f"{item}\n")

    f.write("\n📄 Có trong thư mục nhưng KHÔNG có trong Excel:\n")
    for item in extra_in_folder:
        f.write(f"{item}\n")

print(f"✅ Kết quả đã được lưu tại: {output_txt}")
