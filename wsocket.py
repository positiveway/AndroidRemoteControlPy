import socket

server_ip_num = 104
server_ip = f'192.168.1.{server_ip_num}'
server_port = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP


def send_command_to_ws(command: str):
    sock.sendto(command.encode('utf-8'), (server_ip, server_port))


def send_typing_letter(letter):
    send_command_to_ws(f'l{letter}')


def send_pressed(button):
    send_command_to_ws(f'p{button}')


def send_released(button):
    send_command_to_ws(f'r{button}')


def send_mouse_move(x, y):
    send_command_to_ws(f'{x}{y}')
