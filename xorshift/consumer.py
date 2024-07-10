import socket
import struct
import time

def xorshift(seed):
    seed = seed ^ (seed << 13 & 0xFFFFFFFF)
    seed = seed ^ (seed >> 17 & 0xFFFFFFFF)
    seed = seed ^ (seed << 5 & 0xFFFFFFFF)
    return seed & 0xFFFFFFFF



def main():
    producer_ip = 'producer'
    producer_port = 8081
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    retry_interval = 1  # 再試行までの待機時間（秒）
    retry_num = 0

    while True:
        try:
            if retry_num == 100:
                break
            client.connect((producer_ip, producer_port))
            #print("Successfully connected to the producer")
            # ここで通信処理を行う
            #print('Connected to producer')

            while True:
                client.sendall(b'R')
                length = struct.unpack('!I', client.recv(4))[0]  # データの長さを受信
                data = client.recv(length).decode()
                if data == 'F':
                    break
                seed = int(data)
                #print(f"Received seed: seed={seed}")
                result_rand = seed
                for i in range(10000000):
                    result_rand = xorshift(result_rand)
                data = f'{seed},{result_rand}'.encode()
                client.sendall(b'S')
                client.sendall(struct.pack('!I', len(data)) + data)  # 先にデータの長さを送る
                print(f"Sent result: seed={seed}, random number={result_rand}")
            break


        except (socket.error, OSError) as e:
            print(f"Failed to connect to the producer: {e}")
            print(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)  # 再試行まで待機
        finally:
            retry_num += 1
            client.close()  # 再試行のためにソケットを閉じる
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 新しいソケットを作成


    
    # condition = True
    # while condition:
    #     time.sleep(5)

if __name__ == '__main__':
    main()
