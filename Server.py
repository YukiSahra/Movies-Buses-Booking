import socket
import threading
import json
import datetime
import uuid

class BookingServer:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.clients = []
        
        self.buses = {
            'XE001': {
                'id': 'XE001',
                'route': 'Hà Nội - Hải Phòng',
                'departure': '08:00',
                'arrival': '10:30',
                'price': 120000,
                'total_seats': 40,
                'booked_seats': []
            },
            'XE002': {
                'id': 'XE002',
                'route': 'TP.HCM - Đà Lạt',
                'departure': '06:00',
                'arrival': '12:00',
                'price': 200000,
                'total_seats': 35,
                'booked_seats': []
            },
            'XE003': {
                'id': 'XE003',
                'route': 'Hà Nội - Sapa',
                'departure': '22:00',
                'arrival': '06:00+1',
                'price': 300000,
                'total_seats': 30,
                'booked_seats': []
            }
        }
        
        self.movies = {
            'PHIM001': {
                'id': 'PHIM001',
                'title': 'Avengers: Endgame',
                'showtime': '19:30',
                'duration': '181 phút',
                'price': 80000,
                'cinema': 'CGV Vincom',
                'total_seats': 100,
                'booked_seats': []
            },
            'PHIM002': {
                'id': 'PHIM002',
                'title': 'Spider-Man: No Way Home',
                'showtime': '14:00',
                'duration': '148 phút',
                'price': 75000,
                'cinema': 'Lotte Cinema',
                'total_seats': 80,
                'booked_seats': []
            },
            'PHIM003': {
                'id': 'PHIM003',
                'title': 'Fast & Furious 10',
                'showtime': '21:00',
                'duration': '142 phút',
                'price': 85000,
                'cinema': 'Galaxy Cinema',
                'total_seats': 90,
                'booked_seats': []
            }
        }
        
        self.bookings = {}
    
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"🎫 Server đặt vé đang chạy tại {self.host}:{self.port}")
            print("Đang chờ khách hàng kết nối...")
            
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"🎭 Khách hàng {client_address} đã kết nối")
                
                self.clients.append(client_socket)
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            print(f"❌ Lỗi server: {e}")
        finally:
            server_socket.close()
    
    def handle_client(self, client_socket, client_address):
        try:
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                try:
                    request = json.loads(data)
                    response = self.process_request(request)
                    client_socket.send(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                except json.JSONDecodeError:
                    error_response = {"status": "error", "message": "Dữ liệu không hợp lệ"}
                    client_socket.send(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
                    
        except Exception as e:
            print(f"❌ Lỗi xử lý client {client_address}: {e}")
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            print(f"👋 Khách hàng {client_address} đã ngắt kết nối")
    
    def process_request(self, request):
        action = request.get('action')
        
        if action == 'get_buses':
            return self.get_buses()
        elif action == 'get_movies':
            return self.get_movies()
        elif action == 'book_bus':
            return self.book_bus(request.get('bus_id'), request.get('seats'), request.get('customer'))
        elif action == 'book_movie':
            return self.book_movie(request.get('movie_id'), request.get('seats'), request.get('customer'))
        elif action == 'get_bookings':
            return self.get_bookings(request.get('customer_phone'))
        elif action == 'cancel_booking':
            return self.cancel_booking(request.get('booking_id'))
        else:
            return {"status": "error", "message": "Hành động không hợp lệ"}
    
    def get_buses(self):
        buses_info = []
        for bus in self.buses.values():
            available_seats = bus['total_seats'] - len(bus['booked_seats'])
            buses_info.append({
                'id': bus['id'],
                'route': bus['route'],
                'departure': bus['departure'],
                'arrival': bus['arrival'],
                'price': bus['price'],
                'available_seats': available_seats,
                'total_seats': bus['total_seats']
            })
        
        return {"status": "success", "data": buses_info}
    
    def get_movies(self):
        movies_info = []
        for movie in self.movies.values():
            available_seats = movie['total_seats'] - len(movie['booked_seats'])
            movies_info.append({
                'id': movie['id'],
                'title': movie['title'],
                'showtime': movie['showtime'],
                'duration': movie['duration'],
                'cinema': movie['cinema'],
                'price': movie['price'],
                'available_seats': available_seats,
                'total_seats': movie['total_seats']
            })
        
        return {"status": "success", "data": movies_info}
    
    def book_bus(self, bus_id, num_seats, customer_info):
        if bus_id not in self.buses:
            return {"status": "error", "message": "Mã xe không tồn tại"}
        
        bus = self.buses[bus_id]
        available_seats = bus['total_seats'] - len(bus['booked_seats'])
        
        if num_seats > available_seats:
            return {"status": "error", "message": f"Chỉ còn {available_seats} chỗ trống"}
        
        # Tạo số ghế tự động
        booked_seat_numbers = []
        for i in range(num_seats):
            seat_num = len(bus['booked_seats']) + 1
            bus['booked_seats'].append(seat_num)
            booked_seat_numbers.append(seat_num)
        
        # Tạo mã đặt vé
        booking_id = str(uuid.uuid4())[:8].upper()
        total_price = bus['price'] * num_seats
        
        booking_info = {
            'booking_id': booking_id,
            'type': 'bus',
            'service_id': bus_id,
            'service_name': bus['route'],
            'customer': customer_info,
            'seats': booked_seat_numbers,
            'total_price': total_price,
            'booking_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.bookings[booking_id] = booking_info
        
        return {
            "status": "success",
            "message": "Đặt vé xe thành công!",
            "booking_info": booking_info
        }
    
    def book_movie(self, movie_id, num_seats, customer_info):
        """Đặt vé phim"""
        if movie_id not in self.movies:
            return {"status": "error", "message": "Mã phim không tồn tại"}
        
        movie = self.movies[movie_id]
        available_seats = movie['total_seats'] - len(movie['booked_seats'])
        
        if num_seats > available_seats:
            return {"status": "error", "message": f"Chỉ còn {available_seats} chỗ trống"}
        
        # Tạo số ghế tự động (dạng A1, A2, B1, B2...)
        booked_seat_numbers = []
        for i in range(num_seats):
            seat_num = len(movie['booked_seats']) + 1
            row = chr(65 + (seat_num - 1) // 10)
            col = (seat_num - 1) % 10 + 1
            seat_name = f"{row}{col}"
            movie['booked_seats'].append(seat_name)
            booked_seat_numbers.append(seat_name)
        
        # Tạo mã đặt vé
        booking_id = str(uuid.uuid4())[:8].upper()
        total_price = movie['price'] * num_seats
        
        booking_info = {
            'booking_id': booking_id,
            'type': 'movie',
            'service_id': movie_id,
            'service_name': f"{movie['title']} - {movie['showtime']}",
            'customer': customer_info,
            'seats': booked_seat_numbers,
            'total_price': total_price,
            'booking_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.bookings[booking_id] = booking_info
        
        return {
            "status": "success",
            "message": "Đặt vé phim thành công!",
            "booking_info": booking_info
        }
    
    def get_bookings(self, customer_phone):
        customer_bookings = []
        for booking in self.bookings.values():
            if booking['customer']['phone'] == customer_phone:
                customer_bookings.append(booking)
        
        return {
            "status": "success",
            "data": customer_bookings,
            "count": len(customer_bookings)
        }
    
    def cancel_booking(self, booking_id):
        if booking_id not in self.bookings:
            return {"status": "error", "message": "Mã đặt vé không tồn tại"}
        
        booking = self.bookings[booking_id]
        service_id = booking['service_id']
        seats = booking['seats']
        
        # Trả lại ghế
        if booking['type'] == 'bus':
            for seat in seats:
                if seat in self.buses[service_id]['booked_seats']:
                    self.buses[service_id]['booked_seats'].remove(seat)
        else:  # movie
            for seat in seats:
                if seat in self.movies[service_id]['booked_seats']:
                    self.movies[service_id]['booked_seats'].remove(seat)
        
        # Xóa booking
        del self.bookings[booking_id]
        
        return {
            "status": "success",
            "message": "Hủy vé thành công!",
            "refund_amount": booking['total_price']
        }

if __name__ == "__main__":
    server = BookingServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Đang tắt server...")