import socket
import threading
import time
from queue import Queue
import struct

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
    while True:
        ready_signal = conn.recv(1).decode()
        if ready_signal == 'R':
            with lock:
                if seeds.empty():
                    conn.sendall(b'F')
                    conn.close()
                    break
                seed = seeds.get()
            data = f'{seed}'.encode()
            conn.sendall(struct.pack('!I', len(data)) + data)  # 先にデータの長さを送る
            
            completion_signal = conn.recv(1).decode()
            if completion_signal == 'S':
                length = struct.unpack('!I', conn.recv(4))[0]
                data = conn.recv(length).decode()
                seed, rand = map(int, data.split(','))
                result = Result(seed, rand)
                with lock:
                    results.append(result)
                    if seeds.empty():
                        all_tasks_done.set()

def compute_rand(results):
    random_number = 0
    for result in results:
        random_number = random_number * 10 ** 32
        random_number += result.rand
    return random_number

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
    print("All random number computed, finalizing results...")

    # 結果を統合
    total_rand = compute_rand(results)
    print(f"Computed random number: {total_rand}")
    
    

if __name__ == '__main__':
    main()
