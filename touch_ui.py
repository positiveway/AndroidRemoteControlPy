from functools import partial

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from backend import controller
from garden_joystick import Joystick
from wsocket import send_mouse_move, send_pressed, send_released, send_typing_letter

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

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line


def update_coord_get_number_to_move(cur, prev):
    move_every_n_pixels = controller.move_every_n_pixels

    diff = cur - prev
    if abs(diff) > move_every_n_pixels:
        prev = cur - diff % move_every_n_pixels
        move_by = diff // move_every_n_pixels * controller.move_by_n_pixels
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

diameter = 30.
radius = diameter / 2
ellipse_size = (diameter, diameter)

root = GridLayout(cols=2, rows=1)

cols = 2
rows = 2
col_num = 2
row_num = 2

visuals_for_touchpad = False

buttons_font_size = 50


class TouchpadWidget(Widget):
    def clear_canvas(self):
        if not visuals_for_touchpad:
            return

        self.canvas.clear()

    def draw_touch(self, touch):
        if not visuals_for_touchpad:
            return

        self.canvas.clear()

        with self.canvas:
            Color(*color)
            Ellipse(pos=(touch.x - radius, touch.y - radius), size=ellipse_size)

    def on_touch_down(self, touch):
        if not is_in_zone(touch.x, touch.y, root.height, root.width):
            return

        if touch.is_double_tap:
            # print("Double tap")
            controller.press_and_send(controller.LeftMouse)

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

    def on_touch_up(self, touch):
        if not is_in_zone(touch.x, touch.y, root.height, root.width):
            return

        controller.release_and_send(controller.LeftMouse)

        self.clear_canvas()


class APISenderApp(App):
    def left_pressed(self, button):
        controller.press_and_send(controller.LeftMouse)

    def left_released(self, button):
        controller.release_and_send(controller.LeftMouse)

    def build(self):
        self.root = root

        # clearbtn = Button(text='Clear')
        # clearbtn.bind(on_release=self.clear_canvas)

        # self.root = BoxLayout()
        # self.root.padding = 110

        self.label = Label()
        self.label.font_size = 50

        # self.label.size_hint_x = 0.25
        # self.label.size_hint_y = 0.9

        joystick = Joystick()

        # joystick.size_hint_x = 0.25
        # joystick.size_hint_y = 0.25
        # joystick.pos_hint = {'top': 0.5}

        joystick.pad_size = 0.4
        joystick.inner_size = 0

        joystick.bind(pad=self.update_coordinates)

        self.left_side = GridLayout(cols=1, rows=3)

        self.left_side.add_widget(self.label)
        self.left_side.add_widget(joystick)
        self.left_side.add_widget(Label())

        self.prev_letter = ""
        self.update_label()

        self.button1 = Button()
        self.middle_click = Button()
        self.left_click = Button(
            text="Left", font_size=buttons_font_size,
            on_press=self.left_pressed,
            on_release=self.left_released
        )
        self.right_click = Button()

        self.buttons = GridLayout(cols=2, rows=2)
        self.buttons.add_widget(self.button1)
        self.buttons.add_widget(self.middle_click)
        self.buttons.add_widget(self.left_click)
        self.buttons.add_widget(self.right_click)

        self.touchpad = TouchpadWidget()

        self.right_side = GridLayout(cols=1, rows=2)

        self.right_side.add_widget(self.buttons)
        self.right_side.add_widget(self.touchpad)

        self.root.add_widget(self.left_side)
        self.root.add_widget(self.right_side)

    def update_label(self):
        cur_stage = controller.cur_stage
        if cur_stage < 1:  # cur_stage == 0 or cur_stage == 0.5:
            zone = controller.stick_pos_1
        else:  # elif cur_stage == 1 or cur_stage == 1.5:
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
