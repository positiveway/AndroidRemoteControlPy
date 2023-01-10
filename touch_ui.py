from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from backend import controller
from garden_joystick import Joystick
from wsocket import send_typing_letter, sock, server_ip, server_port

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


class TouchpadWidget(Widget):
    visuals_for_touchpad = False

    max_color = 255
    color = (80 / max_color, 200 / max_color, 1 / max_color)

    diameter = 30.
    radius = diameter / 2
    ellipse_size = (diameter, diameter)

    def clear_canvas(self):
        if not self.visuals_for_touchpad:
            return

        self.canvas.clear()

    def draw_touch(self, touch):
        if not self.visuals_for_touchpad:
            return

        self.canvas.clear()

        with self.canvas:
            Color(*self.color)
            Ellipse(pos=(touch.x - self.radius, touch.y - self.radius), size=self.ellipse_size)

    def on_touch_down(self, touch_event):
        if self.collide_point(touch_event.x, touch_event.y):
            if touch_event.is_double_tap:
                # print("Double tap")
                controller.press_and_send(controller.LeftMouse)

            self.prev_x = touch_event.x
            self.prev_y = touch_event.y

            self.draw_touch(touch_event)
            return True
        else:
            self.full_reset()
            return super(TouchpadWidget, self).on_touch_down(touch_event)

    def convert_to_send(self, x, offset):
        x = round(x)

        if x > 127:
            x = 127
            # print(f"value is too much: {x}")
        elif x < -127:
            x = -127
            # print(f"value is too much: {x}")

        if x < 0:
            x += 256

        if self.is_mouse_mode:
            self.mouse_bytes[offset] = x
        else:
            self.scroll_bytes[offset + 1] = x

    def send_if_not_empty(self, move_x, move_y):
        # print(move_x, move_y)
        if move_x != 0 or move_y != 0:
            self.convert_to_send(move_x, 0)
            self.convert_to_send(move_y, 1)

            if self.is_mouse_mode:
                sock.sendto(self.mouse_bytes, (server_ip, server_port))
            else:
                sock.sendto(self.scroll_bytes, (server_ip, server_port))

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

                self.send_if_not_empty(move_x, move_y)

            self.draw_touch(touch_event)
            return True
        else:
            self.full_reset()
            return super(TouchpadWidget, self).on_touch_move(touch_event)

    def full_reset(self):
        self.prev_x = None

    def init(self):
        self.mouse_bytes = bytearray(2)
        self.scroll_bytes = bytearray(3)
        self.scroll_bytes[0] = 5

        self.is_mouse_mode = True

        self.full_reset()

    def on_touch_up(self, touch_event):
        if self.collide_point(touch_event.x, touch_event.y):
            controller.release_and_send(controller.LeftMouse)

            self.clear_canvas()

            self.full_reset()

            return True
        else:
            return super(TouchpadWidget, self).on_touch_up(touch_event)

    def on_size(self, obj, values):
        self.full_reset()


class APISenderApp(App):
    def toggle_scroll(self, button):
        self.touchpad.is_mouse_mode = not self.touchpad.is_mouse_mode

    def build(self):
        buttons_font_size = 50

        self.touchpad = TouchpadWidget()
        self.touchpad.init()

        joystick = Joystick()

        # joystick.size_hint_x = 0.25
        # joystick.size_hint_y = 0.25
        # joystick.pos_hint = {'top': 0.5}

        joystick.pad_size = 0.4
        joystick.inner_size = 0

        joystick.bind(pad=self.update_coordinates)

        self.root = GridLayout(cols=2, rows=1)

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

        self.scroll_btn = Button(
            text="Scroll", font_size=buttons_font_size,
            on_press=self.toggle_scroll,
        )
        self.left_click = Button(
            text="Left", font_size=buttons_font_size,
            on_press=self.left_pressed,
            on_release=self.left_released
        )
        self.right_click = Button(
            text="Right", font_size=buttons_font_size,
            on_press=self.right_pressed,
            on_release=self.right_released
        )
        self.middle_click = Button(
            text="Middle", font_size=buttons_font_size,
            on_press=self.middle_pressed,
            on_release=self.middle_released
        )

        self.right_buttons = GridLayout(cols=2, rows=2)
        self.right_buttons.add_widget(self.middle_click)
        self.right_buttons.add_widget(self.right_click)

        self.right_buttons.add_widget(self.scroll_btn)
        self.right_buttons.add_widget(self.left_click)

        self.right_side = GridLayout(cols=1, rows=2)
        self.right_side.add_widget(self.right_buttons)
        self.right_side.add_widget(self.touchpad)

        self.root.add_widget(self.left_side)
        self.root.add_widget(self.right_side)

    def left_pressed(self, button):
        controller.press_and_send(controller.LeftMouse)

    def left_released(self, button):
        controller.release_and_send(controller.LeftMouse)

    def right_pressed(self, button):
        controller.press_and_send(controller.RightMouse)

    def right_released(self, button):
        controller.release_and_send(controller.RightMouse)

    def middle_pressed(self, button):
        controller.press_and_send(controller.MiddleMouse)

    def middle_released(self, button):
        controller.release_and_send(controller.MiddleMouse)

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
