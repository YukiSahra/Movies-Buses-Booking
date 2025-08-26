import socket
import json
import os

class BookingClient:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✅ Đã kết nối thành công đến server {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Không thể kết nối đến server: {e}")
            return False
    
    def send_request(self, request):
        try:
            message = json.dumps(request, ensure_ascii=False)
            self.socket.send(message.encode('utf-8'))
            
            response = self.socket.recv(4096).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            print(f"❌ Lỗi gửi yêu cầu: {e}")
            return {"status": "error", "message": "Lỗi kết nối"}
    
    def format_price(self, price):
        return f"{price:,}đ".replace(',', '.')
    
    def view_buses(self):
        request = {'action': 'get_buses'}
        response = self.send_request(request)
        
        if response['status'] == 'success':
            buses = response['data']
            
            print("\n🚌 DANH SÁCH XE KHÁCH")
            print("=" * 80)
            
            if not buses:
                print("Hiện tại không có xe nào.")
                return buses
            
            print(f"{'Mã xe':<8} {'Tuyến đường':<25} {'Khởi hành':<10} {'Giá vé':<12} {'Ghế trống':<10}")
            print("-" * 80)
            
            for bus in buses:
                print(f"{bus['id']:<8} {bus['route']:<25} {bus['departure']:<10} {self.format_price(bus['price']):<12} {bus['available_seats']}/{bus['total_seats']:<10}")
            
            return buses
        else:
            print(f"❌ {response['message']}")
            return []
    
    def view_movies(self):
        request = {'action': 'get_movies'}
        response = self.send_request(request)
        
        if response['status'] == 'success':
            movies = response['data']
            
            print("\n🎬 DANH SÁCH PHIM")
            print("=" * 90)
            
            if not movies:
                print("Hiện tại không có phim nào.")
                return movies
            
            print(f"{'Mã':<8} {'Tên phim':<30} {'Giờ chiếu':<10} {'Rạp':<15} {'Giá vé':<10} {'Ghế trống':<10}")
            print("-" * 90)
            
            for movie in movies:
                print(f"{movie['id']:<8} {movie['title']:<30} {movie['showtime']:<10} {movie['cinema']:<15} {self.format_price(movie['price']):<10} {movie['available_seats']}/{movie['total_seats']:<10}")
            
            return movies
        else:
            print(f"❌ {response['message']}")
            return []
    
    def get_customer_info(self):
        print("\n👤 THÔNG TIN KHÁCH HÀNG")
        print("-" * 30)
        
        while True:
            name = input("Họ tên (hoặc 'back' để quay lại): ").strip()
            if name.lower() == 'back':
                return None
            if name:
                break
            print("❌ Tên là bắt buộc!")
        
        while True:
            phone = input("Số điện thoại: ").strip()
            if phone.lower() == 'back':
                return None
            if phone:
                break
            print("❌ Số điện thoại là bắt buộc!")
        
        email = input("Email (không bắt buộc, Enter để bỏ qua): ").strip()
        
        return {
            'name': name,
            'phone': phone,
            'email': email if email else ""
        }
    
    def book_bus_ticket(self):
        print("\n🎫 ĐẶT VÉ XE KHÁCH")
        print("=" * 40)
        
        buses = self.view_buses()
        if not buses:
            return
        
        while True:
            bus_id = input("\nNhập mã xe (hoặc 'back' để quay lại): ").strip().upper()
            if bus_id.lower() == 'back':
                return
                
            # Kiểm tra xe có tồn tại
            selected_bus = None
            for bus in buses:
                if bus['id'] == bus_id:
                    selected_bus = bus
                    break
            
            if selected_bus:
                break
            else:
                print("❌ Mã xe không hợp lệ! Vui lòng thử lại.")
        
        if selected_bus['available_seats'] == 0:
            print("❌ Xe này đã hết chỗ!")
            return
        
        while True:
            try:
                num_seats_input = input(f"Số lượng vé (tối đa {selected_bus['available_seats']}, 'back' để quay lại): ").strip()
                if num_seats_input.lower() == 'back':
                    return
                    
                num_seats = int(num_seats_input)
                if num_seats <= 0 or num_seats > selected_bus['available_seats']:
                    print("❌ Số lượng vé không hợp lệ!")
                    continue
                break
            except ValueError:
                print("❌ Vui lòng nhập số!")
        
        customer_info = self.get_customer_info()
        if not customer_info:
            return
        
        # Xác nhận đặt vé
        total_price = selected_bus['price'] * num_seats
        print(f"\n📋 XÁC NHẬN THÔNG TIN")
        print("-" * 30)
        print(f"Tuyến: {selected_bus['route']}")
        print(f"Khởi hành: {selected_bus['departure']}")
        print(f"Số vé: {num_seats}")
        print(f"Tổng tiền: {self.format_price(total_price)}")
        
        confirm = input("\nXác nhận đặt vé? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Đã hủy đặt vé.")
            return
        
        # Gửi yêu cầu đặt vé
        request = {
            'action': 'book_bus',
            'bus_id': bus_id,
            'seats': num_seats,
            'customer': customer_info
        }
        
        response = self.send_request(request)
        if response['status'] == 'success':
            booking = response['booking_info']
            print(f"\n🎉 {response['message']}")
            print(f"Mã đặt vé: {booking['booking_id']}")
            print(f"Số ghế: {', '.join(map(str, booking['seats']))}")
            print(f"Tổng tiền: {self.format_price(booking['total_price'])}")
        else:
            print(f"❌ {response['message']}")
    
    def book_movie_ticket(self):
        print("\n🎫 ĐẶT VÉ XEM PHIM")
        print("=" * 40)
        
        movies = self.view_movies()
        if not movies:
            return
        
        while True:
            movie_id = input("\nNhập mã phim (hoặc 'back' để quay lại): ").strip().upper()
            if movie_id.lower() == 'back':
                return
                
            selected_movie = None
            for movie in movies:
                if movie['id'] == movie_id:
                    selected_movie = movie
                    break
            
            if selected_movie:
                break
            else:
                print("❌ Mã phim không hợp lệ! Vui lòng thử lại.")
        
        if selected_movie['available_seats'] == 0:
            print("❌ Phim này đã hết vé!")
            return
        
        while True:
            try:
                num_seats_input = input(f"Số lượng vé (tối đa {selected_movie['available_seats']}, 'back' để quay lại): ").strip()
                if num_seats_input.lower() == 'back':
                    return
                    
                num_seats = int(num_seats_input)
                if num_seats <= 0 or num_seats > selected_movie['available_seats']:
                    print("❌ Số lượng vé không hợp lệ!")
                    continue
                break
            except ValueError:
                print("❌ Vui lòng nhập số!")
        
        customer_info = self.get_customer_info()
        if not customer_info:
            return
        
        # Xác nhận đặt vé
        total_price = selected_movie['price'] * num_seats
        print(f"\n📋 XÁC NHẬN THÔNG TIN")
        print("-" * 30)
        print(f"Phim: {selected_movie['title']}")
        print(f"Rạp: {selected_movie['cinema']}")
        print(f"Giờ chiếu: {selected_movie['showtime']}")
        print(f"Số vé: {num_seats}")
        print(f"Tổng tiền: {self.format_price(total_price)}")
        
        confirm = input("\nXác nhận đặt vé? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Đã hủy đặt vé.")
            return
        
        # Gửi yêu cầu đặt vé
        request = {
            'action': 'book_movie',
            'movie_id': movie_id,
            'seats': num_seats,
            'customer': customer_info
        }
        
        response = self.send_request(request)
        if response['status'] == 'success':
            booking = response['booking_info']
            print(f"\n🎉 {response['message']}")
            print(f"Mã đặt vé: {booking['booking_id']}")
            print(f"Số ghế: {', '.join(booking['seats'])}")
            print(f"Tổng tiền: {self.format_price(booking['total_price'])}")
        else:
            print(f"❌ {response['message']}")
    
    def view_my_bookings(self):
        """Xem lịch sử đặt vé"""
        print("\n📖 LỊCH SỬ ĐẶT VÉ")
        print("-" * 25)
        
        phone = input("Nhập số điện thoại: ").strip()
        if not phone:
            print("❌ Vui lòng nhập số điện thoại!")
            return
        
        request = {
            'action': 'get_bookings',
            'customer_phone': phone
        }
        
        response = self.send_request(request)
        if response['status'] == 'success':
            bookings = response['data']
            
            if not bookings:
                print("Bạn chưa có lịch sử đặt vé nào.")
                return
            
            print(f"\n📋 CÓ {response['count']} ĐẶT VÉ")
            print("=" * 80)
            
            for booking in bookings:
                print(f"\n🎫 Mã đặt vé: {booking['booking_id']}")
                print(f"Loại: {'Xe khách' if booking['type'] == 'bus' else 'Phim'}")
                print(f"Dịch vụ: {booking['service_name']}")
                print(f"Ghế: {', '.join(map(str, booking['seats']))}")
                print(f"Tổng tiền: {self.format_price(booking['total_price'])}")
                print(f"Thời gian đặt: {booking['booking_time']}")
                print("-" * 50)
        else:
            print(f"❌ {response['message']}")
    
    def cancel_booking(self):
        print("\n🗑️ HỦY VÉ")
        print("-" * 15)
        
        booking_id = input("Nhập mã đặt vé: ").strip().upper()
        if not booking_id:
            print("❌ Vui lòng nhập mã đặt vé!")
            return
        
        confirm = input(f"Bạn có chắc muốn hủy vé {booking_id}? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Đã hủy thao tác.")
            return
        
        request = {
            'action': 'cancel_booking',
            'booking_id': booking_id
        }
        
        response = self.send_request(request)
        if response['status'] == 'success':
            print(f"✅ {response['message']}")
            print(f"Số tiền hoàn: {self.format_price(response['refund_amount'])}")
        else:
            print(f"❌ {response['message']}")
    
    def show_menu(self):
        print("\n" + "="*60)
        print("🎫 HỆ THỐNG ĐẶT VÉ ONLINE")
        print("="*60)
        print("1. 🚌 Xem danh sách xe khách")
        print("2. 🎬 Xem danh sách phim")
        print("3. 🎫 Đặt vé xe khách")
        print("4. 🎭 Đặt vé xem phim")
        print("5. 📖 Xem lịch sử đặt vé")
        print("6. 🗑️  Hủy vé")
        print("7. 🚪 Thoát")
        print("\n💡 Lệnh hỗ trợ: 'menu', 'clear', 'exit'")
        print("-"*60)
    
    def run(self):
        if not self.connect_to_server():
            return
        
        self.show_menu()
        
        try:
            while True:
                choice = input("\nChọn chức năng (1-7) hoặc 'menu' để xem lại: ").strip().lower()
                
                if choice == '1':
                    self.view_buses()
                elif choice == '2':
                    self.view_movies()
                elif choice == '3':
                    self.book_bus_ticket()
                elif choice == '4':
                    self.book_movie_ticket()
                elif choice == '5':
                    self.view_my_bookings()
                elif choice == '6':
                    self.cancel_booking()
                elif choice == '7' or choice == 'exit' or choice == 'quit':
                    print("🙏 Cảm ơn bạn đã sử dụng dịch vụ!")
                    break
                elif choice == 'menu' or choice == 'help':
                    self.show_menu()
                elif choice == 'clear' or choice == 'cls':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.show_menu()
                else:
                    print("❌ Lựa chọn không hợp lệ! Nhập 'menu' để xem danh sách chức năng.")
                
        except KeyboardInterrupt:
            print("\n👋 Đã thoát ứng dụng!")
        finally:
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    client = BookingClient()
    client.run()