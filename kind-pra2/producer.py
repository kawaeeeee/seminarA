import socket
import struct
import threading

results = []
lock = threading.Lock()
range_counter = 0
total_ranges = 10
ranges = [(i*100 + 1, (i+1)*100) for i in range(total_ranges)]

def handle_client(client_socket, address):
    global range_counter
    try:
        while True:
            data = client_socket.recv(1)
            if data.decode('utf-8') == 'R':
                with lock:
                    if range_counter < total_ranges:
                        start, end = ranges[range_counter]
                        range_counter += 1
                    else:
                        break  # No more ranges to assign
                
                calc_range = struct.pack('ii', start, end)
                client_socket.send(calc_range)

                data = client_socket.recv(1)
                if data.decode('utf-8') == 'S':
                    result = client_socket.recv(12)
                    start, end, sum_result = struct.unpack('iii', result)
                    with lock:
                        results.append(sum_result)
                    print(f"Received result: start={start}, end={end}, sum={sum_result}")
                    break
            else:
                print(f"Unexpected data received: {data}")
    except Exception as e:
        print(f"Error handling client {address}: {e}")
    finally:
        client_socket.close()

def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 9999))
        server.listen(10)
        print('Producer listening on port 9999')

        threads = []
        for _ in range(10):
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_handler.start()
            threads.append(client_handler)
        
        for t in threads:
            t.join()

        total_sum = sum(results)
        print(f"Total sum from 1 to 1000 is {total_sum}")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()

