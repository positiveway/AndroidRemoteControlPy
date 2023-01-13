import socket

connected_over_phone = False

if connected_over_phone:
    server_ip_num = 200
    server_ip = f'192.168.161.{server_ip_num}'
else:
    server_ip_num = 104
    server_ip = f'192.168.1.{server_ip_num}'

server_port = 5005
