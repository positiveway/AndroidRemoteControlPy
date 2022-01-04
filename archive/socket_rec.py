import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet, UDP
    sock.bind((UDP_IP, UDP_PORT))
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print(data.decode(encoding='utf-8'))
