import struct
import os
import random

def create_sample_binary(file_path, count=100):
    """
    Tạo một file nhị phân chứa các số thực (8 bytes) ngẫu nhiên.
    """
    try:
        with open(file_path, 'wb') as f:
            for _ in range(count):
                random_num = random.uniform(-1000, 1000)
                f.write(struct.pack('d', random_num))
        print(f"Đã tạo file mẫu thành công: {file_path}")
    except Exception as e:
        print(f"Lỗi khi tạo file: {e}")

def read_all_doubles(file_path):
    """
    Đọc toàn bộ số thực từ file nhị phân (Chỉ nên dùng cho file nhỏ).
    """
    numbers = []
    if not os.path.exists(file_path):
        return numbers
    with open(file_path, 'rb') as f:
        while chunk := f.read(8):
            num = struct.unpack('d', chunk)[0]
            numbers.append(num)
    return numbers

def get_record_count(file_path):
    """
    Tính số lượng bản ghi (số thực 8-byte) có trong file.
    """
    file_size = os.path.getsize(file_path)
    return file_size // 8

def write_double_to_binary(file_path, numbers):
    """
    Ghi danh sách số thực vào file nhị phân 8-byte.
    """
    try:
        with open(file_path, 'wb') as f:
            for num in numbers:
                f.write(struct.pack('d', num))
        return True
    except Exception as e:
        print(f"Lỗi khi ghi file nhị phân: {e}")
        return False