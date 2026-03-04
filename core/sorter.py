"""
Module chứa logic cốt lõi của thuật toán Sắp xếp ngoại (External Merge Sort).
Bao gồm hai giai đoạn chính: 
1. Chia nhỏ và sắp xếp nội bộ (Split & Sort).
2. Trộn đa đường sử dụng cấu trúc Min-Heap (K-way Merge).
"""

import struct
import heapq
import os
import time

def split_and_sort_runs(input_path, temp_dir, run_size, callback=None):
    """
    Giai đoạn 1: Chia file gốc thành các file tạm (runs) đã được sắp xếp nội bộ.
    
    Đọc dữ liệu từ file nhị phân gốc theo từng khối (chunk) có kích thước bằng `run_size`,
    sắp xếp các phần tử ngay trong RAM, sau đó ghi kết quả ra các file tạm trên ổ đĩa.

    Args:
        input_path (str): Đường dẫn đến file nhị phân nguồn.
        temp_dir (str): Thư mục dùng để lưu trữ các file tạm (Run files).
        run_size (int): Số lượng phần tử (số thực) tối đa được phép đưa vào RAM mỗi lần.
        callback (function, optional): Hàm gọi lại để gửi dữ liệu về giao diện/hoạt ảnh.

    Returns:
        list[str]: Danh sách chứa đường dẫn tới các file tạm (Run files) vừa được tạo.
    """
    run_files = []
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    with open(input_path, 'rb') as f:
        run_idx = 0
        while True:
            data = f.read(run_size * 8)
            if not data: break
            
            count = len(data) // 8
            numbers = list(struct.unpack(f'{count}d', data))
            
            if callback:
                callback("loading", numbers)
                time.sleep(1.2)
                callback("sorting", numbers)
                time.sleep(1.0)
            
            numbers.sort()
            
            temp_file = os.path.join(temp_dir, f"run_{run_idx}.bin")
            with open(temp_file, 'wb') as tf:
                for num in numbers: tf.write(struct.pack('d', num))
            
            if callback:
                callback("saving", numbers, run_idx)
                time.sleep(1.2)
            
            run_files.append(temp_file)
            run_idx += 1
            
    return run_files

def merge_runs(run_files, output_path, callback=None):
    """
    Giai đoạn 2: Trộn các file tạm đã sắp xếp thành file kết quả duy nhất bằng Min-Heap.
    
    Đóng vai trò "Trọng tài RAM", sử dụng cấu trúc dữ liệu Min-Heap để liên tục 
    so sánh các phần tử đầu tiên của mỗi Run file. Phần tử nhỏ nhất sẽ được 
    rút ra (heappop) và ghi xuống file đích, sau đó nạp ngay phần tử tiếp theo 
    từ Run file tương ứng vào Heap.

    Args:
        run_files (list[str]): Danh sách đường dẫn của các file tạm.
        output_path (str): Đường dẫn file nhị phân kết quả cuối cùng.
        callback (function, optional): Hàm gọi lại để gửi dữ liệu về giao diện/hoạt ảnh.
    """
    import heapq
    import struct
    import time
    
    min_heap = []
    file_handles = [open(rf, 'rb') for rf in run_files]

    # BƯỚC 1: RAM NẠP CÁC PHẦN TỬ ĐẦU TIÊN (VAI TRÒ TRỌNG TÀI)
    for i, fh in enumerate(file_handles):
        data = fh.read(8)
        if data:
            val = struct.unpack('d', data)[0]
            # Gọi callback để Animation hiện viên bi nạp vào RAM
            if callback: 
                callback("init_heap", val, i) 
            heapq.heappush(min_heap, (val, i))
            time.sleep(0.5) # Đợi 0.5s để nhìn rõ từng số bay vào RAM

    with open(output_path, 'wb') as out_f:
        while min_heap:
            # BƯỚC 2: RAM SO SÁNH VÀ CHỌN SỐ NHỎ NHẤT (NGƯỜI THẮNG)
            smallest_val, file_idx = heapq.heappop(min_heap)
            out_f.write(struct.pack('d', smallest_val))
            
            # Gọi callback để Animation cho viên bi bay từ RAM xuống file kết quả
            if callback: 
                callback("merging", smallest_val, file_idx)
            time.sleep(0.5)

            # BƯỚC 3: NẠP TIẾP SỐ KẾ TIẾP TỪ RUN VỪA LẤY SỐ
            data = file_handles[file_idx].read(8)
            if data:
                next_val = struct.unpack('d', data)[0]
                # Gọi callback để nạp ứng cử viên mới vào RAM
                if callback: 
                    callback("init_heap", next_val, file_idx)
                heapq.heappush(min_heap, (next_val, file_idx))
                
    for fh in file_handles: 
        fh.close()