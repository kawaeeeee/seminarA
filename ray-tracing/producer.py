import socket
import threading
from queue import Queue
import struct
import time
import selectors

width = 640
height = 480

# グローバル変数
tasks = Queue() #未割当の行
allocated_tasks = set() #割当済みだけど計算まだの行(集合で管理)
finished_tasks = set() #計算終わった行
results = dict()

lock = threading.Lock() #セマフォ
all_tasks_done = threading.Event() #シグナリング
start_time = time.time() #開始時間

def data_check(s):
	#データに不足がないか判定
	parts = s.split()
	count = sum(1 for part in parts if part.isdigit())
	if count == (width * 3):
		return True
	else:
		return False

def create_ppm():
	with open("image.ppm", 'w') as f:
		# PPM header
		f.write(f'P3\n{width} {height}\n255\n')

		for v in range(height,0,-1):
			f.write(f'{results[v-1]}')
		f.write('\n')

def handle_worker(conn):
	try:
		while True:
			ready_signal = conn.recv(1).decode()
			if ready_signal == 'R':
				with lock:
					if tasks.empty() and len(allocated_tasks)==0 :
						send_data = b'F'
						conn.sendall(struct.pack('!I', len(send_data)) + send_data)
						conn.close()
						break
					#以下割り当て
					if tasks.qsize()!=0:
						row = tasks.get()
						allocated_tasks.add(row)
					else:
						row = allocated_tasks.pop()
						allocated_tasks.add(row)
				send_data = f'{row}'.encode()
				conn.sendall(struct.pack('!I', len(send_data)) + send_data)  # 先にデータの長さを送る
				
				completion_signal = conn.recv(1).decode()
				if completion_signal == 'S':
					length_data = conn.recv(4)
					if not length_data:
						break
					length = struct.unpack('!I', length_data)[0]
					recv_data = conn.recv(length).decode()
					first_part, separator, second_part = recv_data.partition(",")
					cul_row = int(first_part)
					rgb_string = second_part
					if data_check(rgb_string):
						with lock:
							with open("log.txt",'a') as f:
								f.write(f"receive row :{cul_row}\n")
							allocated_tasks.discard(cul_row)
							finished_tasks.add(cul_row)
							results[cul_row]=rgb_string
							if len(finished_tasks) == height:
								all_tasks_done.set()
	except Exception as e:
		print(f"Error handling worker: {e}")
	finally:
		conn.close()

def main():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(('0.0.0.0', 8081))
	server.listen(5)

	selector = selectors.DefaultSelector()
	selector.register(server, selectors.EVENT_READ)

	# 計算範囲をキューに追加
	for i in range(height):
		tasks.put(i)

	try:
		while not all_tasks_done.is_set():
			# イベント待ち
			events = selector.select(timeout=0.001)
			for key, mask in events:
				if key.fileobj == server:
					# 新しい接続がある場合
					conn, addr = server.accept()
					with open("log2.txt",'a') as f2:
						f2.write(f"acccept by {addr}\n")
					threading.Thread(target=handle_worker, args=(conn,)).start()
	finally:
		server.close()

	# 結果をファイルに出力
	create_ppm()
	with open("log2.txt",'a') as f2:
		f2.write(f"execution time {time.time() - start_time}\n")
	print(f"execution time {time.time() - start_time}") # 終了時刻の出力

if __name__ == '__main__':
	main()