#  Trực quan hóa Thuật toán Sắp xếp Ngoại (External Merge Sort)

Một ứng dụng đồ họa (GUI) được xây dựng bằng Python nhằm trực quan hóa cách hoạt động của thuật toán **External Merge Sort**. Dự án này giúp người xem dễ dàng hình dung luồng dữ liệu di chuyển giữa Ổ cứng (Disk) và Bộ nhớ trong (RAM) khi xử lý các tệp dữ liệu lớn hơn dung lượng bộ nhớ.

##  Tính năng nổi bật

* **Cửa sổ mô phỏng siêu rộng (1800px):** Cung cấp không gian hiển thị toàn cảnh luồng dữ liệu mà không bị chồng chéo.
* **Mô phỏng Giai đoạn 1 (Split & Sort):**
  * Đọc dữ liệu từ file nhị phân (Disk) theo từng khối (chunk) vừa với sức chứa của RAM giả lập.
  * Sắp xếp cục bộ và lưu trữ xuống các tệp tạm (`Run 0.bin`, `Run 1.bin`,...).
* **Mô phỏng Giai đoạn 2 (K-way Merge):**
  * **Trọng tài RAM:** Nạp các phần tử đầu tiên của mỗi tệp Run vào cấu trúc Min-Heap trong RAM.
  * **Hoạt ảnh trực quan:** Khung RAM rung lắc khi thực hiện so sánh; phần tử nhỏ nhất (người chiến thắng) được đổi sang màu xanh lá và di chuyển mượt mà xuống file kết quả.
* **Nhập liệu linh hoạt:** Hỗ trợ nạp dữ liệu từ file `.bin` có sẵn hoặc nhập trực tiếp mảng số từ giao diện.

##  Công nghệ sử dụng

* **Ngôn ngữ:** Python 3.x
* **Thư viện UI:** `customtkinter`, `tkinter` (Canvas Animation)
* **Cấu trúc dữ liệu lõi:** Min-Heap (`heapq`), Xử lý file nhị phân (`struct`, `os`)

##  Hướng dẫn Cài đặt & Sử dụng

### 1. Chạy từ mã nguồn (Dành cho Developer)
Clone kho lưu trữ này về máy cục bộ của bạn:
```bash
git clone https://github.com/Tobieeeeeee/CS523-24521699-ExternalMergeSort.git
cd CS523-24521699-ExternalMergeSort
```

Cài đặt thư viện giao diện yêu cầu:
```bash
pip install customtkinter
```

Khởi chạy ứng dụng:
```bash
python main.py
```

### 2. Chạy tệp thực thi trực tiếp (Dành cho Người dùng Windows)
Chỉ cần tải tệp `MoPhongSapXepNgoai.exe` trong phần **Releases** của kho lưu trữ này và nhấp đúp để khởi chạy mà không cần cài đặt Python.

## 📂 Cấu trúc thư mục
```text
├── core/
│   ├── file_handler.py   # Các hàm xử lý đọc/ghi tệp nhị phân (Double 8-byte)
│   └── sorter.py         # Logic thuật toán cốt lõi: Split & Sort và K-way Merge
├── main.py               # Giao diện điều khiển chính và logic vẽ Hoạt ảnh (Animation)
└── README.md             # Tài liệu dự án
```
---
*Bài tập Môn học CS523 - 24521699 - Nguyễn Văn Quốc Thịnh*