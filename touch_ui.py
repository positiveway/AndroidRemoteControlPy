from collections import deque
from statistics import mean

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
    if abs(diff) >= move_every_n_pixels:  # greater or EQUAL
        multiplier, remainder = divmod(diff, move_every_n_pixels)

        prev = cur - remainder
        move_by = multiplier * controller.move_by_n_pixels

        return prev, move_by
    else:
        return prev, 0


max_color = 255
color = (80 / max_color, 200 / max_color, 1 / max_color)

diameter = 30.
radius = diameter / 2
ellipse_size = (diameter, diameter)

buttons_font_size = 50

visuals_for_touchpad = False

history_size = 3
diff_for_new_touch = 10


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

    def on_touch_down(self, touch_event):
        # self.history_x = deque()
        # self.history_y = deque()

        if self.collide_point(touch_event.x, touch_event.y):
            if touch_event.is_double_tap:
                # print("Double tap")
                controller.press_and_send(controller.LeftMouse)

            if self.prev_x is not None:
                diff_x = touch_event.x - self.prev_x
                diff_y = touch_event.y - self.prev_y

                if abs(diff_x) < diff_for_new_touch and abs(diff_y) < diff_for_new_touch:
                    send_mouse_move(diff_x, diff_y)

            self.prev_x = touch_event.x
            self.prev_y = touch_event.y

            self.draw_touch(touch_event)
            return True
        else:
            self.prev_x = None
            return super(TouchpadWidget, self).on_touch_down(touch_event)

    def calc_move(self, cur_x, prev_x, diff_history: deque):
        diff = cur_x, prev_x
        diff_history.append(diff)

        if len(diff_history) == history_size:
            move_by = mean(diff_history)
            return move_by
        else:
            return 0

    def on_touch_move(self, touch_event):
        if self.collide_point(touch_event.x, touch_event.y):
            if self.prev_x is None:
                self.prev_x = touch_event.x
                self.prev_y = touch_event.y
            else:
                # self.prev_x, move_x = update_coord_get_number_to_move(touch_event.x, self.prev_x)
                # self.prev_y, move_y = update_coord_get_number_to_move(touch_event.y, self.prev_y)

                move_x = touch_event.x - self.prev_x
                move_y = touch_event.y - self.prev_y

                self.prev_x = touch_event.x
                self.prev_y = touch_event.y

                send_mouse_move(move_x, move_y)

            self.draw_touch(touch_event)
            return True
        else:
            return super(TouchpadWidget, self).on_touch_move(touch_event)

    def on_touch_up(self, touch_event):
        if self.collide_point(touch_event.x, touch_event.y):
            controller.release_and_send(controller.LeftMouse)

            self.clear_canvas()
            return True
        else:
            return super(TouchpadWidget, self).on_touch_up(touch_event)

    def on_size(self, obj, values):
        self.prev_x = None


class APISenderApp(App):
    def left_pressed(self, button):
        controller.press_and_send(controller.LeftMouse)

    def left_released(self, button):
        controller.release_and_send(controller.LeftMouse)

    def build(self):
        self.touchpad = TouchpadWidget()

        joystick = Joystick()

        # joystick.size_hint_x = 0.25
        # joystick.size_hint_y = 0.25
        # joystick.pos_hint = {'top': 0.5}

        joystick.pad_size = 0.4
        joystick.inner_size = 0

        joystick.bind(pad=self.update_coordinates)

        self.root = GridLayout(cols=2, rows=1)

        # clearbtn = Button(text='Clear')
        # clearbtn.bind(on_release=self.clear_canvas)

        # self.root = BoxLayout()
        # self.root.padding = 110

        self.label = Label()
        self.label.font_size = 50

        # self.label.size_hint_x = 0.25
        # self.label.size_hint_y = 0.9

        self.left_buttons = GridLayout(cols=2, rows=1)
        self.shift_button = Button(text="Shift", font_size=buttons_font_size)
        self.caps_button = Button(text="Caps", font_size=buttons_font_size)
        self.left_buttons.add_widget(self.caps_button)
        self.left_buttons.add_widget(self.shift_button)

        self.left_side = GridLayout(cols=1, rows=3)
        self.left_side.add_widget(self.label)
        self.left_side.add_widget(joystick)
        self.left_side.add_widget(self.left_buttons)

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

        self.right_buttons = GridLayout(cols=2, rows=2)
        self.right_buttons.add_widget(self.button1)
        self.right_buttons.add_widget(self.middle_click)
        self.right_buttons.add_widget(self.left_click)
        self.right_buttons.add_widget(self.right_click)

        self.right_side = GridLayout(cols=1, rows=2)

        self.right_side.add_widget(self.right_buttons)
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
