import socket
import struct

def main():
    producer_ip = 'producer'
    producer_port = 9999

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((producer_ip, producer_port))
        print('Connected to producer')

        client.send(b'R')
        
        data = client.recv(8)
        start, end = struct.unpack('ii', data)
        print(f"Received range: start={start}, end={end}")

        sum_result = sum(range(start, end + 1))

        client.send(b'S')
        result = struct.pack('iii', start, end, sum_result)
        client.send(result)
        print(f"Sent result: start={start}, end={end}, sum={sum_result}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
