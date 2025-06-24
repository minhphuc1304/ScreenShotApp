import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import ImageGrab
import os
import time

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Chụp Màn Hình")
        
        # Biến lưu thư mục lưu ảnh
        self.save_folder = "D:/screenshot/"
        
        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        # Tạo các nút trong giao diện
        self.btn_capture = tk.Button(root, text="Chọn Vùng Chụp", command=self.capture_area, width=20)
        self.btn_capture.pack(pady=10)

        self.btn_choose_folder = tk.Button(root, text="Chọn Thư Mục Lưu", command=self.choose_folder, width=20)
        self.btn_choose_folder.pack(pady=10)

        self.btn_exit = tk.Button(root, text="Thoát", command=root.quit, width=20)
        self.btn_exit.pack(pady=10)

    def choose_folder(self):
        """Cho phép người dùng chọn thư mục lưu ảnh."""
        folder = filedialog.askdirectory(title="Chọn thư mục lưu ảnh")
        if folder:
            self.save_folder = folder
            messagebox.showinfo("Thông báo", f"Thư mục lưu đã được cập nhật: {self.save_folder}")

    def capture_area(self):
        """Chọn vùng chụp màn hình và lưu vào thư mục."""
        # Tạo cửa sổ chọn vùng
        selection_window = tk.Toplevel(self.root)
        selection_window.attributes("-fullscreen", True)
        selection_window.attributes("-alpha", 0.3)
        selection_window.configure(bg="gray")
        selection_window.title("Chọn khu vực chụp")

        start_x = start_y = end_x = end_y = 0
        rect_id = None

        def start_selection(event):
            nonlocal start_x, start_y, rect_id
            start_x, start_y = event.x, event.y
            rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

        def update_selection(event):
            nonlocal rect_id
            canvas.coords(rect_id, start_x, start_y, event.x, event.y)

        def finish_selection(event):
            nonlocal start_x, start_y, end_x, end_y
            end_x, end_y = event.x, event.y
            selection_window.destroy()  # Đóng cửa sổ chọn vùng

            # Tính tọa độ thực
            x1, y1 = min(start_x, end_x), min(start_y, end_y)
            x2, y2 = max(start_x, end_x), max(start_y, end_y)

            # Kiểm tra vùng chọn hợp lệ
            if x1 == x2 or y1 == y2:
                messagebox.showerror("Lỗi", "Vùng chọn không hợp lệ.")
                return

            try:
                # Chụp màn hình vùng chọn
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(self.save_folder, f"screenshot_{timestamp}.png")
                screenshot.save(save_path)
                messagebox.showinfo("Thành công", f"Ảnh vùng chọn đã lưu tại: {save_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

        def cancel_selection(event):
            """Hủy chọn vùng và đóng cửa sổ chọn vùng."""
            selection_window.destroy()
            self.root.deiconify()  # Hiện lại cửa sổ chính

        canvas = tk.Canvas(selection_window, bg="gray")
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.bind("<Button-1>", start_selection)
        canvas.bind("<B1-Motion>", update_selection)
        canvas.bind("<ButtonRelease-1>", finish_selection)

        # Thêm sự kiện bàn phím cho phím Esc
        selection_window.bind("<Escape>", cancel_selection)

        selection_window.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.geometry("300x200")  # Kích thước cửa sổ chính
    root.mainloop()

