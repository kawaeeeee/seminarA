import socket
import struct

def xorshift(seed):
    seed = seed ^ (seed << 13 & 0xFFFFFFFF)
    seed = seed ^ (seed >> 17 & 0xFFFFFFFF)
    seed = seed ^ (seed << 5 & 0xFFFFFFFF)
    return seed & 0xFFFFFFFF

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
        seed = int(data)
        print(f"Received seed: seed={seed}")
        
        result_rand = xorshift(seed)
        data = f'{seed},{result_rand}'.encode()
        client.sendall(b'S')
        client.sendall(struct.pack('!I', len(data)) + data)  # 先にデータの長さを送る
        print(f"Sent result: seed={seed}, random number={result_rand}")
    
    client.close()

if __name__ == '__main__':
    main()
