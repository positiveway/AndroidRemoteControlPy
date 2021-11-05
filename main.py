import requests

from controller import controller
from kivy.app import App
from garden_joystick import Joystick
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


def get_zone_number(attr_prefix):
    zone = controller.get_zone(attr_prefix)
    return {
        "🢂": 1,
        "🢅": 2,
        "🢁": 3,
        "🢄": 4,
        "🢀": 5,
        "🢇": 6,
        "🢃": 7,
        "🢆": 8,
        controller.NEUTRAL_ZONE: -1,
        controller.EDGE_ZONE: -2,
    }[zone]


class DemoApp(App):
    def build(self):
        self.root = BoxLayout()
        self.root.padding = 50

        left_joystick = Joystick()
        left_joystick.bind(pad=self.update_left)
        self.root.add_widget(left_joystick)
        self.left_label = Label()
        self.root.add_widget(self.left_label)

        right_joystick = Joystick()
        right_joystick.bind(pad=self.update_right)
        self.root.add_widget(right_joystick)
        self.right_label = Label()
        self.root.add_widget(self.right_label)

    def update_coordinates(self, joystick, pad, attr_prefix):
        x = str(pad[0])[0:5]
        y = str(pad[1])[0:5]
        radians = str(joystick.radians)[0:5]
        magnitude = str(joystick.magnitude)[0:5]
        angle = str(joystick.angle)[0:5]

        letter = controller.update_zone(joystick.magnitude, joystick.angle, attr_prefix)
        if letter:
            print(letter)

            letter = ord(letter[0])

        text = "Zone: {}\nletter: {}\nx: {}\ny: {}\nradians: {}\nmagnitude: {}\nangle: {}"

        return text.format(get_zone_number(attr_prefix), letter, x, y, radians, magnitude, angle)

    def update_left(self, joystick, pad):
        self.left_label.text = self.update_coordinates(joystick, pad, "Left")

    def update_right(self, joystick, pad):
        self.right_label.text = self.update_coordinates(joystick, pad, "Right")


class APISenderApp(App):
    server_ip_num = 54
    server_ip = '192.168.1.'
    server_port = 8000
    server_address = f'{server_ip}{server_ip_num}:{server_port}'

    def send_letter(self, letter):
        requests.post(f'{self.server_address}/send_letter', data={'letter': letter})
        return letter

    def build(self):
        self.root = BoxLayout()
        self.root.padding = 50

        left_joystick = Joystick()
        left_joystick.bind(pad=self.update_left)
        self.root.add_widget(left_joystick)

        right_joystick = Joystick()
        right_joystick.bind(pad=self.update_right)
        self.root.add_widget(right_joystick)

        self.label = Label()
        self.root.add_widget(self.label)

    def update_coordinates(self, joystick, pad, attr_prefix):
        letter = controller.update_zone(joystick.magnitude, joystick.angle, attr_prefix)
        if letter:
            letter = self.send_letter(letter)
            self.label.text = letter

    def update_left(self, joystick, pad):
        self.update_coordinates(joystick, pad, "Left")

    def update_right(self, joystick, pad):
        self.update_coordinates(joystick, pad, "Right")


if __name__ == '__main__':
    # DemoApp().run()
    APISenderApp().run()
