import socket
import threading
from queue import Queue
import struct
import time
import selectors

# 計算結果
class Result:
    def __init__(self, seed, rand):
        self.seed = seed
        self.rand = rand



# グローバル変数
seeds = Queue()
results = []
lock = threading.Lock()
all_tasks_done = threading.Event()
now_time = int(time.time())

# 計算範囲をキューに追加
for i in range(10):
    seeds.put(now_time + i)

def handle_worker(conn):
    try:
        while True:
            ready_signal = conn.recv(1).decode()
            if ready_signal == 'R':
                with lock:
                    if seeds.empty():
                        data = b'F'
                        conn.sendall(struct.pack('!I', len(data)) + data)
                        conn.close()
                        break
                    seed = seeds.get()
                data = f'{seed}'.encode()
                conn.sendall(struct.pack('!I', len(data)) + data)  # 先にデータの長さを送る
                
                completion_signal = conn.recv(1).decode()
                if completion_signal == 'S':
                    length_data = conn.recv(4)
                    if not length_data:
                        break
                    length = struct.unpack('!I', length_data)[0]
                    data = conn.recv(length).decode()
                    seed, rand = map(int, data.split(','))
                    result = Result(seed, rand)
                    with lock:
                        print(f"seed: {result.seed}")
                        print(f"rand: {result.rand}")
                        results.append(result)
                        if len(results) == 10:
                            print("receive all results")
                            print("all tasks done")
                            all_tasks_done.set()
    except Exception as e:
        print(f"Error handling worker: {e}")
    finally:
        conn.close()
        conn.close()

def compute_rand(results):
    random_number = 0
    for result in results:
        random_number = (random_number << 32) | result.rand
    return random_number

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
    total_rand = compute_rand(results)
    print(f"Total Sum: {total_rand}")

    # サーバー終了後の処理を続けるためのループ
    # while True:
    #     time.sleep(5)

if __name__ == '__main__':
    main()
