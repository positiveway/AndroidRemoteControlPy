from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse

from backend import Controller


class TouchpadWidget(Widget):
    def update_coord_get_number_to_move(self, cur, prev):
        move_every_n_pixels = self.controller.move_every_n_pixels

        diff = cur - prev
        if abs(diff) >= move_every_n_pixels:  # greater or EQUAL
            multiplier, remainder = divmod(diff, move_every_n_pixels)

            prev = cur - remainder
            move_by = multiplier * self.controller.move_by_n_pixels

            return prev, move_by
        else:
            return prev, 0

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
                self.controller.send_pressed(self.controller.LeftMouse)
                # print("Double tap")
            return True
        else:
            return super(TouchpadWidget, self).on_touch_down(touch_event)

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
            if self.move_x != 0 or self.move_y != 0:
                self.offset = 0
                self.convert_to_send(self.move_x)
                self.offset = 1
                self.convert_to_send(self.move_y)
                self.controller.send(self.mouse_bytes)
        else:
            if self.move_y != 0:
                self.mouse_bytes[0] = 128
                self.offset = 1
                self.convert_to_send(self.move_y)
                self.controller.send(self.mouse_bytes)

    def on_touch_move(self, touch_event):
        if self.collide_point(touch_event.x, touch_event.y):
            self.cur_x = round(touch_event.x)
            self.cur_y = round(touch_event.y)

            if self.prev_x == self.value_not_set:
                self.prev_x = self.cur_x
                self.prev_y = self.cur_y
            else:
                # self.prev_x, move_x = update_coord_get_number_to_move(touch_event.x, self.prev_x)
                # self.prev_y, move_y = update_coord_get_number_to_move(touch_event.y, self.prev_y)

                self.move_x = self.cur_x - self.prev_x
                self.move_y = self.cur_y - self.prev_y

                self.prev_x = self.cur_x
                self.prev_y = self.cur_y

                self.send_if_not_empty()

            self.draw_touch(touch_event)
            return True
        else:
            self.full_reset()
            return super(TouchpadWidget, self).on_touch_move(touch_event)

    def full_reset(self):
        self.prev_x = self.value_not_set

    def init(self):
        self.visuals_for_touchpad = False

        self.mouse_bytes = bytearray(2)

        self.is_mouse_mode = True

        self.controller = Controller()

        self.value_not_set = 1000

        self.offset = 0
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

    def on_touch_up(self, touch_event):
        self.full_reset()

        self.controller.send_released(self.controller.LeftMouse)

        if self.collide_point(touch_event.x, touch_event.y):
            self.clear_canvas()
            return True
        else:
            return super(TouchpadWidget, self).on_touch_up(touch_event)

    def on_size(self, obj, values):
        self.full_reset()
