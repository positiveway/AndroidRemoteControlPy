from math import hypot
from threading import Timer

from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse

from backend import Controller


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

    def timer_func(self):
        if self.init_x != self.value_not_set:
            if self.cur_x == self.value_not_set or \
                    hypot(self.cur_x - self.init_x, self.cur_y - self.init_y) <= self.controller.hold_dist:

                if self.is_mouse_mode:
                    self.controller.send_pressed(self.controller.LeftMouse)
                else:
                    self.is_mouse_mode = True

    def on_touch_down(self, touch_event):
        if self.is_in_zone(touch_event):
            self.prev_x = round(touch_event.x)
            self.prev_y = round(touch_event.y)

            if touch_event.is_double_tap:
                self.toggle_scroll()
            else:
                self.init_x = self.prev_x
                self.init_y = self.prev_y
                self.make_new_timer()
                self.timer.start()

            return True
        else:
            return super(TouchpadWidget, self).on_touch_down(touch_event)

    def update_coord_get_scroll_dir(self, cur, prev):
        scroll_every_n_pixels = self.controller.scroll_every_n_pixels
        diff = cur - prev
        if abs(diff) >= scroll_every_n_pixels:  # greater or EQUAL
            multiplier, remainder = divide_with_reminder(diff, scroll_every_n_pixels)
            prev = cur - remainder
            return prev, multiplier
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
        # print(move_x, move_y)
        if self.is_mouse_mode:
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
            # self.prev_x, self.move_x = self.update_coord_get_scroll_dir(self.cur_x, self.prev_x)
            # self.prev_y, self.move_y = self.update_coord_get_scroll_dir(self.cur_y, self.prev_y)

            self.move_x = self.cur_x - self.prev_x
            self.move_y = self.cur_y - self.prev_y

            self.move_x = int(self.move_x / self.controller.scroll_every_n_pixels)
            self.move_y = int(self.move_y / self.controller.scroll_every_n_pixels)

            self.prev_x = self.cur_x
            self.prev_y = self.cur_y

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
                # self.prev_x, move_x = update_coord_get_number_to_move(touch_event.x, self.prev_x)
                # self.prev_y, move_y = update_coord_get_number_to_move(touch_event.y, self.prev_y)

                self.send_if_not_empty()

            self.draw_touch(touch_event)
            return True
        else:
            self.reset()
            return super(TouchpadWidget, self).on_touch_move(touch_event)

    def on_touch_up(self, touch_event):
        self.reset()
        self.controller.send_released(self.controller.LeftMouse)

        if self.is_in_zone(touch_event):
            self.clear_canvas()
            return True
        else:
            return super(TouchpadWidget, self).on_touch_up(touch_event)

    def reset(self):
        self.timer.cancel()
        self.prev_x = self.value_not_set
        self.cur_x = self.value_not_set
        self.init_x = self.value_not_set

    def is_in_zone(self, touch_event):
        return self.x <= touch_event.x <= self.max_x and self.y <= touch_event.y <= self.max_y

    def recalc_size(self):
        self.max_x = self.x + self.width
        self.max_y = self.y + self.height

    def on_size(self, obj, values):
        self.reset()
        self.recalc_size()

    def toggle_scroll(self):
        self.is_mouse_mode = not self.is_mouse_mode

    def make_new_timer(self):
        hold_time = self.controller.hold_time_normal if self.is_mouse_mode \
            else self.controller.hold_time_during_scroll
        self.timer = Timer(hold_time, self.timer_func)

    def init(self):
        self.value_not_set = 1000

        self.controller = Controller()

        self.mouse_bytes = bytearray(2)
        self.is_mouse_mode = True
        self.visuals_for_touchpad = self.controller.visuals_for_touchpad
        self.make_new_timer()

        self.offset = 0
        self.prev_x = 0
        self.prev_y = 0
        self.move_x = 0
        self.move_y = 0

        self.reset()

        max_color = 255
        self.color = (80 / max_color, 200 / max_color, 1 / max_color)

        diameter = 30.
        self.radius = diameter / 2
        self.ellipse_size = (diameter, diameter)
