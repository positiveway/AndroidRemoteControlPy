import socket

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from backend import controller
from garden_joystick import Joystick

ENABLE_VIBRATE = False


def is_vibro_enabled():
    if ENABLE_VIBRATE:
        from kivy.utils import platform
        return platform == "android"
    else:
        return False


if is_vibro_enabled():
    from android.permissions import request_permissions, Permission

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


def send_mouse_move(x, y):
    send_command_to_ws('m', f'{int(x)},{int(y)}')


from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line


def update_coord_get_number_to_move(cur, prev):
    diff = cur - prev
    if abs(diff) > controller.move_every_n_pixels:
        prev = cur - diff % controller.move_every_n_pixels
        move_by = diff // controller.move_every_n_pixels * controller.move_by_n_pixels
        return prev, move_by
    else:
        return prev, 0


def is_in_zone(x, y, height, width):
    y = height - y

    x_sector = width / cols
    y_sector = height / rows

    max_x = x_sector * col_num
    max_y = y_sector * row_num

    min_x = max_x - x_sector
    min_y = max_y - y_sector

    return min_x < x < max_x and min_y < y < max_y


max_color = 255
color = (80 / max_color, 200 / max_color, 1 / max_color)

cols = 2
rows = 3
root = GridLayout(cols=cols, rows=rows)
col_num = 2
row_num = 1


class TouchpadWidget(Widget):
    def draw_touch(self, touch):
        self.canvas.clear()

        with self.canvas:
            Color(*color)
            d = 30.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))

    def on_touch_down(self, touch):
        if not is_in_zone(touch.x, touch.y, root.height, root.width):
            return

        self.prev_x = touch.x
        self.prev_y = touch.y

        self.draw_touch(touch)

    def on_touch_move(self, touch):
        if not is_in_zone(touch.x, touch.y, root.height, root.width):
            return

        self.prev_x, move_x = update_coord_get_number_to_move(touch.x, self.prev_x)
        self.prev_y, move_y = update_coord_get_number_to_move(touch.y, self.prev_y)
        send_mouse_move(move_x, move_y)

        self.draw_touch(touch)


class APISenderApp(App):
    def clear_canvas(self, obj):
        self.touchpad.canvas.clear()

    def build(self):
        self.root = root

        self.touchpad = TouchpadWidget()
        clearbtn = Button(text='Clear')
        clearbtn.bind(on_release=self.clear_canvas)

        # self.root = BoxLayout()
        # self.root.padding = 110

        self.buttons = GridLayout(cols=2, rows=2)
        self.buttons.add_widget(Button())
        self.buttons.add_widget(Button())
        self.buttons.add_widget(Button())
        self.buttons.add_widget(Button())

        self.label = Label()
        self.label.font_size = 50
        self.root.add_widget(self.label)

        # self.label.size_hint_x = 0.25
        # self.label.size_hint_y = 0.9

        self.root.add_widget(Label())
        self.root.add_widget(self.buttons)

        joystick = Joystick()

        # joystick.size_hint_x = 0.25
        # joystick.size_hint_y = 0.25
        # joystick.pos_hint = {'top': 0.5}

        joystick.pad_size = 0.4
        joystick.inner_size = 0

        joystick.bind(pad=self.update_coordinates)
        self.root.add_widget(joystick)

        self.root.add_widget(self.touchpad)
        self.root.add_widget(clearbtn)

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
        # send_typing_params(joystick.magnitude, joystick.angle)

        # print(joystick.magnitude, joystick.angle)

        letter = controller.update_zone(joystick.magnitude, joystick.angle)
        if letter is not None:
            #     if is_vibro_enabled():
            #         vibrator.vibrate(0.5)

            self.prev_letter = letter
            if letter != controller.UNMAPPED_POSITION:
                send_typing_letter(letter)

        self.update_label()


def main():
    APISenderApp().run()


if __name__ == '__main__':
    main()
