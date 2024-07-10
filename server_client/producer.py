import socket
import threading
from queue import Queue
import struct
import time
import selectors

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
    try:
        while True:
            ready_signal = conn.recv(1).decode()
            if ready_signal == 'R':
                with lock:
                    if ranges.empty():
                        data = b'F'
                        conn.sendall(struct.pack('!I', len(data)) + data)
                        conn.close()
                        break
                    range_to_compute = ranges.get()
                data = f'{range_to_compute.start},{range_to_compute.end}'.encode()
                conn.sendall(struct.pack('!I', len(data)) + data)  # 先にデータの長さを送る
                
                completion_signal = conn.recv(1).decode()
                if completion_signal == 'S':
                    length_data = conn.recv(4)
                    if not length_data:
                        break
                    length = struct.unpack('!I', length_data)[0]
                    result_data = conn.recv(length).decode()
                    start, end, sum = map(int, result_data.split(','))
                    result = Result(start, end, sum)
                    with lock:
                        print(f"start: {result.start}")
                        results.append(result)
                        if len(results) == 100:
                            print("receive all results")
                            print("all tasks done")
                            all_tasks_done.set()
    except Exception as e:
        print(f"Error handling worker: {e}")
    finally:
        conn.close()
        conn.close()

def main():
    print('Program start')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8081))
    server.listen(5)
    print('Producer is running...')

    selector = selectors.DefaultSelector()
    selector.register(server, selectors.EVENT_READ)

    try:
        while not all_tasks_done.is_set():
            # イベント待ち
            events = selector.select(timeout=0.001)
            for key, mask in events:
                if key.fileobj == server:
                    # 新しい接続がある場合
                    print("before accept")
                    conn, addr = server.accept()
                    print(f'Connected by {addr}')
                    threading.Thread(target=handle_worker, args=(conn,)).start()
    finally:
        server.close()

    print("All ranges computed, finalizing results...")

    # 結果を統合
    total_sum = sum([result.sum for result in results])
    print(f"Total Sum: {total_sum}")

    # サーバー終了後の処理を続けるためのループ
    # while True:
    #     time.sleep(5)

if __name__ == '__main__':
    main()
