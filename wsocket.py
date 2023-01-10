import socket

connected_over_phone = False

if connected_over_phone:
    server_ip_num = 200
    server_ip = f'192.168.161.{server_ip_num}'
else:
    server_ip_num = 104
    server_ip = f'192.168.1.{server_ip_num}'

server_port = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP


def send_command_to_ws(command: str):
    # print(command)
    sock.sendto(command.encode('utf-8'), (server_ip, server_port))


def send_typing_letter(letter):
    send_command_to_ws(f'ty{letter}')


def send_pressed(button):
    send_command_to_ws(f'pr{button}')


def send_released(button):
    send_command_to_ws(f're{button}')
