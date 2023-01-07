import socket
from backend import controller

port = 5005


def custom_ws():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    server_address = ('0.0.0.0', port)
    s.bind(server_address)
    print("####### Server is listening #######")

    while True:
        data, address = s.recvfrom(1024)
        data = data.decode('utf-8')
        # print(data)

        command_type = data[0]
        command = data[1:]

        if command_type == 'l':  # letter
            print(command)

        elif command_type == 't':  # typing
            magnitude, angle = command.split(',')
            magnitude, angle = float(magnitude), float(angle)
            letter = controller.update_zone(magnitude, angle)
            if letter is not None:
                print(letter)

        #######
        # s.sendto(send_data.encode('utf-8'), address)


if __name__ == '__main__':
    custom_ws()
