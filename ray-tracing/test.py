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
samples = 5
supersamples = 2

def main():
	send_data = f'{439},{ppm_maker.get_ppm_line(width,height,samples,supersamples,439)}'.encode()
	print(f"{send_data}")


if __name__ == '__main__':
	main()