from kivy.app import App

from backend import controller
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


def send_typing_params(magnitude, angle):
    send_command_to_ws('t', f'{magnitude},{angle}')


def send_typing_letter(letter):
    send_command_to_ws('l', letter)


class APISenderApp(App):
    def build(self):
        self.root = BoxLayout()
        # self.root.padding = 100

        self.label = Label()
        self.label.font_size = 50
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

        self.prev_letter = ""
        self.update_label()

    def update_label(self):
        cur_stage = controller.cur_stage
        if cur_stage == 0 or cur_stage == 0.5:
            zone = controller.stick_pos_1
        elif cur_stage == 1 or cur_stage == 1.5:
            zone = controller.stick_pos_2

        letter = ''
        if cur_stage == 1.5 or cur_stage == 0:
            letter = f'{self.prev_letter}'

        hints = ''
        if cur_stage == 0.5 or cur_stage == 1:
            hints = f'{controller.get_direction_hints(controller.stick_pos_1)}'

        zone = {
            "🢂": 'Right',
            "🢅": 'UpRight',
            "🢁": 'Up',
            "🢄": 'UpLeft',
            "🢀": 'Left',
            "🢇": 'DownLeft',
            "🢃": 'Down',
            "🢆": 'DownRight',
            "⬤": 'Neutral',
            "❌": 'Unmapped',
        }[zone]

        self.label.text = f'{letter}\n{hints}\n{cur_stage}: {zone}'

    def update_coordinates(self, joystick, pad):
        send_typing_params(joystick.magnitude, joystick.angle)

        # print(joystick.magnitude, joystick.angle)

        letter = controller.update_zone(joystick.magnitude, joystick.angle)
        if letter is not None:
            #     if is_vibro_enabled():
            #         vibrator.vibrate(0.5)
            send_typing_letter(letter)
            self.prev_letter = letter

        self.update_label()


def main():
    APISenderApp().run()


if __name__ == '__main__':
    main()
