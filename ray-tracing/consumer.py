import socket
import struct
import time
import ppm_maker

"""
ここ大域変数
sampleとsupersamples
"""
width = 640
height = 480
samples = 10
supersamples = 2

def main():
	producer_ip = 'producer'#producer
	producer_port = 8081
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	retry_interval = 1  # 再試行までの待機時間（秒）
	retry_num = 0


	while True:
		try:
			if retry_num == 100:
				break
			client.connect((producer_ip, producer_port))

			while True:
				client.sendall(b'R')
				length = struct.unpack('!I', client.recv(4))[0]  # データの長さを受信
				recv_data = client.recv(length).decode()
				if recv_data == 'F':
					with open("log.txt",'a') as f:
						f.write("receive finish signal\n")
					print("receive finish signal")
					break
				row = int(recv_data)
				with open("log.txt",'a') as f:
					f.write(f"row: {row}")
				print(f"row:{row}")
				"""
				try:
					result = ppm_maker.get_ppm_line(width,height,samples,supersamples,row)
				except UnicodeDecodeError:
					pass
				"""

				send_data = f'{row},{ppm_maker.get_ppm_line(width,height,samples,supersamples,row)}'.encode()
				# while True:
				# 	try:	
				# 		send_data = f'{row},{ppm_maker.get_ppm_line(width,height,samples,supersamples,row)}'.encode()
				# 		break
				# 	except Exception as e:
				# 		print(f"error occurred row {row}: {e}, retrying...")
				
				client.sendall(b'S')
				client.sendall(struct.pack('!I', len(send_data)) + send_data) #送信
				with open("log.txt",'a') as f:
					f.write(f"Sent result: row={row}\n")
				print(f"Sent result: row={row}")
			break


		except (socket.error, OSError) as e:
			print(f"Failed to connect to the producer: {e}")
			print(f"Retrying in {retry_interval} seconds...")
			time.sleep(retry_interval)  # 再試行まで待機
		finally:
			retry_num += 1
			client.close()  # 再試行のためにソケットを閉じる
			client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 新しいソケットを作成

if __name__ == '__main__':
	main()