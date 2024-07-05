import socket
import struct

def compute_sum(start, end):
    return sum(range(start, end + 1))

def main():
    producer_ip = 'producer'
    producer_port = 9999
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((producer_ip, producer_port))
    print('Connected to producer')
    
    while True:
        client.sendall(b'R')
        length = struct.unpack('!I', client.recv(4))[0]  # データの長さを受信
        data = client.recv(length).decode()
        if data == 'F':
            break
        start, end = map(int, data.split(','))
        print(f"Received range: start={start}, end={end}")
        
        result_sum = compute_sum(start, end)
        data = f'{start},{end},{result_sum}'.encode()
        client.sendall(b'S')
        client.sendall(struct.pack('!I', len(data)) + data)  # 先にデータの長さを送る
        print(f"Sent result: start={start}, end={end}, sum={result_sum}")
    
    client.close()

if __name__ == '__main__':
    main()
