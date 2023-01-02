from kivy.app import App
from garden_joystick import Joystick
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import socket

ENABLE_VIBRATE = False


def is_vibro_enabled():
    if ENABLE_VIBRATE:
        from kivy.utils import platform
        return platform == "android"
    else:
        return False


if is_vibro_enabled():
    from android.permissions import request_permissions, Permission
    from plyer import vibrator

    request_permissions([Permission.VIBRATE])

server_ip_num = 104
server_ip = f'192.168.1.{server_ip_num}'
server_port = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP


def send_command_to_ws(command_type, info: str):
    msg = f'{command_type}{info}'
    sock.sendto(msg.encode('utf-8'), (server_ip, server_port))


def send_typing(magnitude, angle):
    send_command_to_ws('t', f'{magnitude},{angle}')


class APISenderApp(App):
    def build(self):
        self.root = BoxLayout()
        # self.root.padding = 100

        self.label = Label()
        self.label.font_size = 50
        self.label.text = "Empty"
        self.root.add_widget(self.label)

        self.label.size_hint_x = 0.25
        self.label.size_hint_y = 0.9

        joystick = Joystick()

        joystick.size_hint_x = 0.25
        joystick.size_hint_y = 0.25
        joystick.pos_hint = {'top': 0.5}

        joystick.pad_size = 0.4
        joystick.inner_size = 0

        joystick.bind(pad=self.update_coordinates)
        self.root.add_widget(joystick)

    def update_coordinates(self, joystick, pad):
        send_typing(joystick.magnitude, joystick.angle)

        # print(joystick.magnitude, joystick.angle)

        # letter = controller.update_zone(joystick.magnitude, joystick.angle)  # test
        # if letter is not None:
        #     if is_vibro_enabled():
        #         vibrator.vibrate(0.5)
        # self.label.text = letter


def main():
    APISenderApp().run()


if __name__ == '__main__':
    main()
