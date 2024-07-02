import socket
import struct
import threading

class Producer:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()

    def handle_client(self, client_socket, address):
        try:
            while True:
                data = client_socket.recv(1)
                if not data:
                    break
                
                if data.decode('utf-8') == 'R':
                    with self.lock:
                        if not self.results or self.results[-1]['end'] < 1000:
                            start = self.results[-1]['end'] + 1 if self.results else 1
                            end = start + 99 if start + 99 <= 1000 else 1000
                            calc_range = struct.pack('ii', start, end)
                            client_socket.send(calc_range)
                        else:
                            break

                    data = client_socket.recv(1)
                    if data.decode('utf-8') == 'S':
                        result = client_socket.recv(12)
                        start, end, sum_result = struct.unpack('iii', result)
                        with self.lock:
                            self.results.append({'start': start, 'end': end, 'sum': sum_result})
                            print(f"Received result: start={start}, end={end}, sum={sum_result}")
                else:
                    print(f"Unexpected data received: {data}")
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()

    def main(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('0.0.0.0', 9999))
            server.listen(10)
            print('Producer listening on port 9999')

            while True:
                client_socket, addr = server.accept()
                print(f"Accepted connection from {addr}")
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                client_handler.start()
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.summarize_results()

    def summarize_results(self):
        total_sum = sum(result['sum'] for result in self.results)
        print(f"Total sum from 1 to 1000 is {total_sum}")

if __name__ == "__main__":
    producer = Producer()
    producer.main()
