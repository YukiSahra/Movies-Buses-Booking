# Utils.py
# Các hàm tiện ích: log, validate dữ liệu, format kết quả

import datetime

# --- Logging ---
def log_event(message, logfile="events.log"):
    """Ghi lại sự kiện vào file log"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


# --- Validation ---
def validate_seats(available_seats, requested=1):
    """Kiểm tra số ghế còn trống"""
    return available_seats >= requested


def validate_booking_type(btype):
    """Chỉ cho phép loại booking hợp lệ"""
    return btype.lower() in ["movie", "bus"]


# --- Formatting ---
def format_booking(booking):
    """
    booking: dict hoặc tuple chứa thông tin booking
    Ví dụ: {"user": "Alice", "type": "movie", "ref": "Avengers"}
    """
    if isinstance(booking, dict):
        return f"👤 {booking['user']} đặt {booking['type']} → {booking['ref']}"
    elif isinstance(booking, tuple) and len(booking) >= 4:
        # tuple từ SQLite: (id, user, type, ref_id)
        return f"👤 {booking[1]} đặt {booking[2]} (ref_id={booking[3]})"
    else:
        return str(booking)


def format_booking_list(bookings):
    """In đẹp danh sách booking"""
    if not bookings:
        return "📭 Chưa có vé nào."
    return "\n".join([f"{i+1}. {format_booking(b)}" for i, b in enumerate(bookings)])
