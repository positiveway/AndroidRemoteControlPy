import gc

from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse

from controller import Controller


def divide_with_reminder(a, b: int):
    multiplier = int(a / b)
    reminder = a - (multiplier * b)
    return multiplier, reminder


class TouchpadWidget(Widget):
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
        if self.is_in_zone(touch_event):
            self.prev_x = round(touch_event.x)
            self.prev_y = round(touch_event.y)

            self.touch_down_count += 1

            if touch_event.is_double_tap:
                if self.controller.is_mouse_mode:
                    self.double_tap_func()
                # else:
                #     self.controller.is_mouse_mode = True
            else:
                if self.controller.is_mouse_mode:
                    pass

            self.clear_typed_text()
            return True
        else:
            return super().on_touch_down(touch_event)

    def update_coord_get_scroll_dir(self, cur, prev):
        scroll_every_n_pixels = self.controller.scroll_every_n_pixels
        diff = cur - prev
        if abs(diff) >= scroll_every_n_pixels:  # greater or EQUAL
            multiplier, remainder = divide_with_reminder(diff, scroll_every_n_pixels)
            prev = cur - remainder
            return prev, multiplier * self.controller.scroll_by
        else:
            return prev, 0

    def convert_to_send(self, x):
        if x > 127:
            x = 127
            # print(f"value is too much: {x}")
        elif x < -127:
            x = -127
            # print(f"value is too much: {x}")

        if x < 0:
            x += 256

        self.mouse_bytes[self.offset] = x

    def send_if_not_empty(self):
        if self.controller.is_mouse_mode:
            self.move_x = self.cur_x - self.prev_x
            self.move_y = self.cur_y - self.prev_y

            self.prev_x = self.cur_x
            self.prev_y = self.cur_y

            if self.move_x != 0 or self.move_y != 0:
                self.offset = 0
                self.convert_to_send(self.move_x)
                self.offset = 1
                self.convert_to_send(self.move_y)
                self.controller.sock.send(self.mouse_bytes)
        else:
            self.prev_x, self.move_x = self.update_coord_get_scroll_dir(self.cur_x, self.prev_x)
            self.prev_y, self.move_y = self.update_coord_get_scroll_dir(self.cur_y, self.prev_y)

            if self.move_y != 0:
                self.mouse_bytes[0] = 128
                self.offset = 1
                self.convert_to_send(self.move_y)
                self.controller.sock.send(self.mouse_bytes)

    def on_touch_move(self, touch_event):
        if self.is_in_zone(touch_event):
            self.cur_x = round(touch_event.x)
            self.cur_y = round(touch_event.y)

            if self.prev_x == self.value_not_set:
                self.prev_x = self.cur_x
                self.prev_y = self.cur_y
            else:
                self.send_if_not_empty()

            self.draw_touch(touch_event)
            return True
        else:
            # don't reset here it will prevent releasing pressed button on touch_up
            # if finger goes out of touchpad zone and then touch_up happens
            return super().on_touch_move(touch_event)

    def on_touch_up(self, touch_event):
        if self.is_in_zone(touch_event):
            if self.touch_down_count == 2:
                self.two_fingers_func()

            self.touch_down_count -= 1

        if self.prev_x != self.value_not_set:  # originated within this element
            self.reset()
            self.controller.send_released(self.controller.LeftMouse)
            gc.collect()

        if self.is_in_zone(touch_event):
            self.clear_canvas()
            return True
        else:
            return super().on_touch_up(touch_event)

    def reset(self):
        self.prev_x = self.value_not_set
        self.cur_x = self.value_not_set

    def full_reset(self):
        self.reset()
        self.touch_down_count = 0

    def is_in_zone(self, touch_event):
        return self.x <= touch_event.x <= self.max_x and self.y <= touch_event.y <= self.max_y

    def recalc_size(self):
        self.max_x = self.x + self.width
        self.max_y = self.y + self.height

    def on_size(self, obj, values):
        self.full_reset()
        self.recalc_size()

    def game_right_click(self):
        self.controller.send_type(self.controller.RightMouse)
        self.controller.is_mouse_mode = True

    def left_press(self):
        self.controller.send_pressed(self.controller.LeftMouse)

    def toggle_scroll(self):
        self.is_mouse_mode = not self.is_mouse_mode

    def switch_to_scroll(self):
        self.controller.is_mouse_mode = False

    def init(self):
        self.always_release = True  # kivy behavior

        self.value_not_set = 1000

        self.controller = Controller()

        self.double_tap_func = self.left_press

        if self.controller.is_game_mode:
            self.two_fingers_func = self.game_right_click
        else:
            self.two_fingers_func = self.switch_to_scroll

        self.mouse_bytes = bytearray(2)
        self.visuals_for_touchpad = self.controller.visuals_for_touchpad

        self.offset = 0
        self.touch_down_count = 0
        self.prev_x = 0
        self.prev_y = 0
        self.move_x = 0
        self.move_y = 0

        self.full_reset()

        max_color = 255
        self.color = (80 / max_color, 200 / max_color, 1 / max_color)

        diameter = 30.
        self.radius = diameter / 2
        self.ellipse_size = (diameter, diameter)
