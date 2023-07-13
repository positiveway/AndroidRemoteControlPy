from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse

from controller import Controller


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

    def init_prev_and_count(self, touch_event):
        self.touch_down_count += 1
        if self.touch_down_count > self.MAX_FINGERS_SUPPORTED:
            # self.touch_down_count = 0
            raise ValueError(f'Down or move: {self.touch_down_count}')

        self.prev_x = round(touch_event.x)
        self.prev_y = round(touch_event.y)

    def on_touch_down(self, touch_event):
        if self.is_in_zone(touch_event):

            self.init_prev_and_count(touch_event)

            if touch_event.is_double_tap:
                if self.controller.is_mouse_mode:
                    self.double_tap_func()
                else:
                    # self.two_fingers_func()
                    self.controller.is_mouse_mode = True

            return True
        else:
            return super().on_touch_down(touch_event)

    def get_convert_to_send(self, offset, bytes_msg):
        def actual_func(x):
            if bytes_msg[offset] > 128:
                bytes_msg[offset] -= 256

            x = bytes_msg[offset] + x

            if x > 127:
                x = 127
                # print(f"value is too much: {x}")
            elif x < -127:
                x = -127
                # print(f"value is too much: {x}")

            if x < 0:
                x += 256

            bytes_msg[offset] = x

        return actual_func

    def on_touch_move(self, touch_event):
        if self.is_in_zone(touch_event) and self.touch_down_count <= 1:

            if self.prev_x == self.value_not_set:
                self.init_prev_and_count(touch_event)
            else:
                self.cur_x = round(touch_event.x)
                self.cur_y = round(touch_event.y)

                self.move_x = self.cur_x - self.prev_x
                self.move_y = self.cur_y - self.prev_y

                self.prev_x = self.cur_x
                self.prev_y = self.cur_y

                if self.controller.is_mouse_mode:
                    self.write_mouse_x_byte(self.move_x)
                    self.write_mouse_y_byte(-self.move_y)
                else:
                    self.write_scroll_byte(self.move_y * self.scroll_by)

            # self.draw_touch(touch_event)
            return True
        else:
            # don't reset here it will prevent releasing pressed button on touch_up
            # if finger goes out of touchpad zone and then touch_up happens
            return super().on_touch_move(touch_event)

    def on_touch_up(self, touch_event):
        in_zone = self.is_in_zone(touch_event)
        originated_within_element = self.prev_x != self.value_not_set  # originated within this element

        if self.touch_down_count <= 1:
            if originated_within_element:
                self.reset()
                self.release_func()
        else:
            if in_zone or originated_within_element:
                if not self.mult_fingers_handled:
                    if self.touch_down_count == 2:
                        self.mult_fingers_handled = True
                        self.two_fingers_func()

                    elif self.touch_down_count == 3:
                        self.mult_fingers_handled = True
                        self.three_fingers_func()

        if in_zone or originated_within_element:
            if self.touch_down_count > 0:
                self.touch_down_count -= 1

        if in_zone:
            # self.clear_canvas()
            return True
        else:
            return super().on_touch_up(touch_event)

    def reset(self):
        self.prev_x = self.value_not_set
        self.cur_x = self.value_not_set

        self.mult_fingers_handled = False

    def full_reset(self):
        self.touch_down_count = 0
        self.reset()
        self.cur_game_button = self.LeftMouse

    def is_in_zone(self, touch_event):
        return self.x <= touch_event.x <= self.max_x and self.y <= touch_event.y <= self.max_y

    def recalc_size(self):
        self.max_x = self.x + self.width
        self.max_y = self.y + self.height

    def on_size(self, obj, values):
        self.full_reset()
        self.recalc_size()

    def send_buffer(self, dt):
        self.mouse_sock.send(self.mouse_msg)
        self.mouse_msg[0] = 0
        self.mouse_msg[1] = 0

        self.scroll_sock.send(self.scroll_msg)
        self.scroll_msg[0] = 0

    def game_aim(self):
        self.controller.send_pressed_mouse(self.RightMouse)

    def game_release_aim(self):
        self.controller.send_released_mouse(self.RightMouse)

    def game_toggle_aim(self):
        pass

    def game_fire(self):
        self.game_aim()
        self.controller.send_pressed_mouse(self.LeftMouse)

    def game_release_fire(self):
        self.controller.send_released_mouse(self.LeftMouse)
        self.game_release_aim()

    def left_press(self):
        self.controller.send_pressed_mouse(self.LeftMouse)

    def release_left(self):
        self.controller.send_released_mouse(self.LeftMouse)

    def right_click(self):
        self.controller.is_mouse_mode = True
        self.controller.send_type(self.RightMouse)

    def toggle_scroll(self):
        self.controller.is_mouse_mode = not self.controller.is_mouse_mode

    def switch_to_scroll(self):
        self.controller.is_mouse_mode = False


    def init(self):
        self.always_release = True  # kivy behavior

        self.MAX_FINGERS_SUPPORTED = 3

        self.value_not_set = 1000

        self.controller = Controller()
        self.scroll_by = self.controller.scroll_by

        self.LeftMouse = self.controller.LeftMouse
        self.RightMouse = self.controller.RightMouse

        if self.controller.is_game_mode:
            self.double_tap_func = self.game_fire
            self.two_fingers_func = self.game_aim
            self.three_fingers_func = self.empty_func
            self.release_func = self.game_release_fire
        else:
            self.double_tap_func = self.left_press
            self.two_fingers_func = self.toggle_scroll
            self.three_fingers_func = self.right_click
            self.release_func = self.release_left

        self.mouse_sock = self.controller.mouse_sock
        self.scroll_sock = self.controller.scroll_sock

        self.mouse_msg = bytearray(2)
        self.scroll_msg = bytearray(1)

        self.write_mouse_x_byte = self.get_convert_to_send(0, self.mouse_msg)
        self.write_mouse_y_byte = self.get_convert_to_send(1, self.mouse_msg)

        self.write_scroll_byte = self.get_convert_to_send(0, self.scroll_msg)

        self.visuals_for_touchpad = self.controller.visuals_for_touchpad

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
