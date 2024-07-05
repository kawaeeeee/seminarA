import socket
import threading
from queue import Queue
import struct

# 計算範囲
class Range:
    def __init__(self, start, end):
        self.start = start
        self.end = end

# 計算結果
class Result:
    def __init__(self, start, end, sum):
        self.start = start
        self.end = end
        self.sum = sum

# グローバル変数
ranges = Queue()
results = []
lock = threading.Lock()
all_tasks_done = threading.Event()

# 計算範囲をキューに追加
for i in range(1, 10001, 100):
    ranges.put(Range(i, i + 99))

def handle_worker(conn):
    while True:
        ready_signal = conn.recv(1).decode()
        if ready_signal == 'R':
            with lock:
                if ranges.empty():
                    conn.sendall(b'F')
                    conn.close()
                    break
                range_to_compute = ranges.get()
            data = f'{range_to_compute.start},{range_to_compute.end}'.encode()
            conn.sendall(struct.pack('!I', len(data)) + data)  # 先にデータの長さを送る
            
            completion_signal = conn.recv(1).decode()
            if completion_signal == 'S':
                length = struct.unpack('!I', conn.recv(4))[0]
                data = conn.recv(length).decode()
                start, end, sum = map(int, data.split(','))
                result = Result(start, end, sum)
                with lock:
                    results.append(result)
                    if ranges.empty():
                        all_tasks_done.set()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    print('Producer is running...')

    while not all_tasks_done.is_set():
        conn, addr = server.accept()
        print(f'Connected by {addr}')
        threading.Thread(target=handle_worker, args=(conn,)).start()

    server.close()
    print("All ranges computed, finalizing results...")

    # 結果を統合
    total_sum = sum([result.sum for result in results])
    print(f"Total Sum: {total_sum}")
    
    

if __name__ == '__main__':
    main()
