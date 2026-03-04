"""
Module giao diện chính (GUI) cho ứng dụng mô phỏng External Merge Sort.
Chứa các class quản lý cửa sổ tương tác (App) và cửa sổ hoạt ảnh (AnimationPopup).
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import threading
import time
from core.sorter import split_and_sort_runs, merge_runs

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    """
    Lớp giao diện chính của ứng dụng.
    Xử lý các thao tác chọn file, nhập dữ liệu thủ công, hiển thị nhật ký (log) 
    và khởi chạy luồng thuật toán sắp xếp.
    """
    def __init__(self):
        super().__init__()
        self.title("Ứng dụng Minh họa Sắp xếp Ngoại")
        self.geometry("850x550") 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", rowspan=2)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="External Sort", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.select_btn = ctk.CTkButton(self.sidebar, text="Chọn file nguồn (.bin)", command=self.select_file)
        self.select_btn.grid(row=1, column=0, padx=20, pady=10)

        self.entry_numbers = ctk.CTkEntry(self.sidebar, placeholder_text="Ví dụ: 5.2, 10, -3", width=200)
        self.entry_numbers.grid(row=3, column=0, padx=20, pady=10)

        self.btn_convert = ctk.CTkButton(self.sidebar, text="Xác nhận & Tạo file", command=self.process_manual_input)
        self.btn_convert.grid(row=4, column=0, padx=20, pady=10)

        self.entry_ram = ctk.CTkEntry(self.sidebar, placeholder_text="Mặc định: 5")
        self.entry_ram.insert(0, "5") 
        self.entry_ram.grid(row=6, column=0, padx=20, pady=10)

        # Main Content
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.textbox = ctk.CTkTextbox(self.main_frame)
        self.textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, mode="indeterminate")
        self.progress_bar.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.start_btn = ctk.CTkButton(self, text="Bắt đầu sắp xếp", command=self.start_sorting, state="disabled", height=40)
        self.start_btn.grid(row=1, column=1, padx=20, pady=(0, 20))

        self.file_path = None

    def log(self, message, *args): 
        """
        Ghi một dòng thông báo vào khung textbox trên giao diện chính.
        
        Args:
            message (str): Nội dung cần hiển thị.
        """
        self.textbox.insert("end", f"> {message}\n")
        self.textbox.see("end")

    def select_file(self):
        """
        Mở hộp thoại để người dùng chọn file nhị phân (.bin) có sẵn từ máy tính.
        """
        self.file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if self.file_path:
            self.start_btn.configure(state="normal")

    def process_manual_input(self):
        """
        Đọc chuỗi số thực người dùng nhập vào, chuyển đổi và lưu thành file nhị phân tạm thời.
        """
        raw_data = self.entry_numbers.get()
        try:
            numbers = [float(x) for x in raw_data.replace(',', ' ').split()]
            from core.file_handler import write_double_to_binary
            save_path = "input_manual.bin"
            if write_double_to_binary(save_path, numbers):
                self.file_path = os.path.abspath(save_path)
                self.log(f"Đã tạo file nhị phân ({len(numbers)} số). SẴN SÀNG ĐỂ SẮP XẾP!") 
                self.start_btn.configure(state="normal")
        except Exception as e:
            self.log(f"Lỗi: {e}")

    def start_sorting(self):
        """
        Kiểm tra thông số RAM và khởi tạo một luồng (thread) phụ để chạy thuật toán, 
        tránh làm đơ giao diện chính.
        """
        if not self.file_path: return
        try: ram_size = int(self.entry_ram.get())
        except: ram_size = 5
        
        self.start_btn.configure(state="disabled")
        self.progress_bar.start()
        thread = threading.Thread(target=self.run_sort_logic, args=(ram_size,))
        thread.daemon = True
        thread.start()

    def run_sort_logic(self, ram_size):
        """
        Thực thi luồng chính của thuật toán External Sort (Phase 1 & Phase 2).
        
        Args:
            ram_size (int): Kích thước vùng nhớ RAM giả lập.
        """
        from core.file_handler import get_record_count, read_all_doubles
        total_elements = get_record_count(self.file_path)
        output_file = "sorted_final.bin"
        popup = AnimationPopup(self) if total_elements < 15 else None

        def unified_callback(stage, data=None, run_idx=None):
            """Hàm gọi lại (callback) để cập nhật giao diện và hoạt ảnh từ thuật toán lõi."""
            actual_data = data if data is not None else []
            self.log(stage if data is None else f"{stage}: {data}")
            if popup and popup.winfo_exists():
                popup.update_animation(stage, actual_data, run_idx)

        try:
            # Giai đoạn 1: Split & Sort
            run_files = split_and_sort_runs(self.file_path, "temp_storage", ram_size, unified_callback)
            
            if not run_files:
                self.log("Lỗi: Không tạo được các file Run.")
                return 

            # Giai đoạn 2: Merge
            merge_runs(run_files, output_file, unified_callback)
            
            final_data = read_all_doubles(output_file)
            unified_callback("KẾT QUẢ CUỐI CÙNG", final_data)
            if popup: time.sleep(5) 
        except Exception as e:
            self.log(f"Lỗi hệ thống: {e}")
        finally:
            self.progress_bar.stop()
            self.start_btn.configure(state="normal")

class AnimationPopup(ctk.CTkToplevel):
    """
    Cửa sổ hoạt ảnh đồ họa (Canvas) mô phỏng quá trình di chuyển dữ liệu 
    giữa Disk và RAM.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Mô phỏng Luồng Dữ liệu (Bản Wide 1800px)")
        self.geometry("1800x900")
        self.configure(fg_color="#1a1a1a")
        self.attributes("-topmost", True)
        
        self.canvas = ctk.CTkCanvas(self, width=1780, height=850, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(pady=10)
        
        self.cx = 890 
        
        self.ram_rect = self.canvas.create_rectangle(self.cx-220, 100, self.cx+220, 220, outline="cyan", width=3, tags="ram_ui")
        self.canvas.create_text(self.cx, 125, text="BỘ NHỚ RAM", fill="cyan", font=("Arial", 16, "bold"), tags="ram_ui")
        
        self.current_balls = []
        self.heap_balls = {}
        self.merged_results = [] 
        self.merged_text_id = None 

    def move_ball(self, start_pos, end_pos, value, color="#e74c3c"):
        """
        Tạo và di chuyển một đối tượng hình tròn (viên bi) từ điểm A đến điểm B.
        
        Args:
            start_pos (tuple): Tọa độ (x, y) xuất phát.
            end_pos (tuple): Tọa độ (x, y) đích đến.
            value (float/int): Giá trị hiển thị bên trong viên bi.
            color (str): Mã màu của viên bi.
            
        Returns:
            tuple: Trả về (ID hình tròn, ID văn bản) trên Canvas.
        """
        ball = self.canvas.create_oval(start_pos[0], start_pos[1], start_pos[0]+40, start_pos[1]+40, fill=color, tags="dynamic")
        text = self.canvas.create_text(start_pos[0]+20, start_pos[1]+20, text=str(value), fill="white", font=("Arial", 11, "bold"), tags="dynamic")
        steps = 20
        dx, dy = (end_pos[0] - start_pos[0]) / steps, (end_pos[1] - start_pos[1]) / steps
        for _ in range(steps):
            self.canvas.move(ball, dx, dy); self.canvas.move(text, dx, dy)
            self.update(); time.sleep(0.01)
        return ball, text

    def animate_existing_ball(self, ball_id, text_id, end_pos):
        """
        Di chuyển một viên bi đã tồn tại sẵn trên Canvas đến vị trí mới.
        
        Args:
            ball_id (int): ID của đối tượng hình tròn.
            text_id (int): ID của đối tượng văn bản.
            end_pos (tuple): Tọa độ đích đến (x, y).
        """
        curr = self.canvas.coords(ball_id)
        if not curr: return
        steps = 20
        dx, dy = (end_pos[0] - curr[0]) / steps, (end_pos[1] - curr[1]) / steps
        for _ in range(steps):
            self.canvas.move(ball_id, dx, dy); self.canvas.move(text_id, dx, dy)
            self.update(); time.sleep(0.01)

    def shake_ram(self):
        """Tạo hiệu ứng rung lắc nhẹ cho khung RAM để mô phỏng tiến trình so sánh/sắp xếp."""
        for _ in range(4):
            self.canvas.move(self.ram_rect, 10, 0); self.update(); time.sleep(0.04)
            self.canvas.move(self.ram_rect, -10, 0); self.update(); time.sleep(0.04)
        
    def update_animation(self, stage, data, run_idx=None):
        """
        Hàm trung tâm điều phối toàn bộ các hoạt ảnh trên màn hình dựa vào giai đoạn (stage) hiện tại.
        
        Args:
            stage (str): Tên giai đoạn ('loading', 'sorting', 'saving', 'init_heap', 'merging',...).
            data (list/float): Dữ liệu liên quan đến tiến trình hiện tại.
            run_idx (int, optional): Chỉ mục của file Run (nếu đang ở giai đoạn chia/trộn).
        """
        self.canvas.delete("status")
        safe_data = data if data is not None else []

        if stage == "loading":
            self.canvas.delete("dynamic")
            self.current_balls = []
            
            self.canvas.create_rectangle(self.cx-200, 700, self.cx+200, 780, outline="gray", tags="source_file")
            self.canvas.create_text(self.cx, 740, text="FILE NGUỒN (DISK)", fill="gray", font=("Arial", 14), tags="source_file")
            
            for i, val in enumerate(safe_data):
                start_x = (self.cx - 100) + (i * 55)
                self.current_balls.append(self.move_ball((start_x, 710), (start_x, 145), val))

        elif stage == "sorting":
            for _ in range(4):
                self.canvas.move(self.ram_rect, 10, 0); self.update(); time.sleep(0.05)
                self.canvas.move(self.ram_rect, -10, 0); self.update(); time.sleep(0.05)

        elif stage == "saving":
            x_run = (self.cx - 500) + (run_idx * 250)
            y_run = 400
            self.canvas.create_rectangle(x_run-80, y_run, x_run+80, y_run+110, outline="white", width=2, tags="permanent")
            self.canvas.create_text(x_run, y_run-20, text=f"Run {run_idx}.bin", fill="yellow", tags="permanent")
            
            content = "\n".join([str(x) for x in safe_data]) 
            self.canvas.create_text(x_run, y_run+55, text=content, fill="#3498db", font=("Arial", 10), tags="permanent")

            for b_id, t_id in self.current_balls:
                self.animate_existing_ball(b_id, t_id, (x_run-20, y_run+20))
            self.current_balls = []

        elif stage == "init_heap":
            if not getattr(self, "is_merging_phase", False):
                self.canvas.delete("dynamic") 
                self.canvas.delete("source_file")
                self.is_merging_phase = True
                self.merged_results = []
                
            x_origin = (self.cx - 500) + (run_idx * 300)
            x_ram_slot = (self.cx - 100) + (run_idx * 100) 
            y_ram_slot = 155 
            
            ball_ids = self.move_ball((x_origin, 450), (x_ram_slot, y_ram_slot), data, color="#e67e22") 
            self.heap_balls[run_idx] = ball_ids

        elif stage == "merging":
            if run_idx in self.heap_balls:
                b_id, t_id = self.heap_balls.pop(run_idx)
                
                self.shake_ram() 
                self.canvas.itemconfig(b_id, fill="#2ecc71")
                self.update()
                time.sleep(0.4) 
                
                self.animate_existing_ball(b_id, t_id, (self.cx, 715))
                self.canvas.create_rectangle(self.cx-300, 700, self.cx+300, 780, outline="#2ecc71", width=3, tags="status")
                self.canvas.create_text(self.cx, 800, text="FILE KẾT QUẢ ĐANG TRỘN", fill="#2ecc71", font=("Arial", 12, "bold"), tags="status")

                self.canvas.delete(b_id)
                self.canvas.delete(t_id)
                
                self.merged_results.append(str(data))
                if self.merged_text_id:
                    self.canvas.delete(self.merged_text_id)
                
                res_str = " | ".join(self.merged_results)
                self.merged_text_id = self.canvas.create_text(self.cx, 740, text=res_str, fill="white", font=("Arial", 16, "bold"), tags="status")

        elif stage == "KẾT QUẢ CUỐI CÙNG":
            self.canvas.delete("dynamic")
            self.canvas.delete("permanent")
            self.canvas.delete("ram_ui") 
            self.canvas.delete("source_file")
            if self.merged_text_id: 
                self.canvas.delete(self.merged_text_id)
            
            self.canvas.create_rectangle(200, 300, 1600, 500, outline="#2ecc71", width=5, tags="status")
            self.canvas.create_text(self.cx, 250, text="✨ KẾT QUẢ SẮP XẾP CUỐI CÙNG ✨", fill="#2ecc71", font=("Arial", 28, "bold"), tags="status")
            res_txt = "   |   ".join([str(x) for x in safe_data])
            self.canvas.create_text(self.cx, 400, text=res_txt, fill="white", font=("Arial", 22, "bold"), tags="status")

if __name__ == "__main__":
    App().mainloop()