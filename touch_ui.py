import gc

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.button import Button

from code_map import reverse_code_map, code_map
from garden_joystick import Joystick
from touchpad import TouchpadWidget

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


class APISenderApp(App):
    def toggle_scroll(self, button):
        self.touchpad.is_mouse_mode = not self.touchpad.is_mouse_mode

    def build(self):
        self.visuals_for_joystick = True

        buttons_font_size = 50

        self.reverse_code_map = reverse_code_map

        self.touchpad = TouchpadWidget()
        self.touchpad.init()
        self.controller = self.touchpad.controller

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

        self.label = Label(font_size=buttons_font_size)
        # self.label.size_hint_x = 0.25
        # self.label.size_hint_y = 0.9

        joystick_layout = GridLayout(cols=3, rows=3)
        self.shift_btn = Button(text="Shift", font_size=buttons_font_size)
        self.caps_btn = Button(text="Caps", font_size=buttons_font_size)
        self.clear_btn = Button(text="BS", font_size=buttons_font_size, on_release=self.clear)
        self.copy_btn = Button(text="Copy", font_size=buttons_font_size)
        self.cut_btn = Button(text="Cut", font_size=buttons_font_size)
        self.paste_btn = Button(text="Paste", font_size=buttons_font_size)

        joystick_layout.add_widget(self.copy_btn)
        joystick_layout.add_widget(self.cut_btn)
        joystick_layout.add_widget(self.paste_btn)
        joystick_layout.add_widget(Label())
        joystick_layout.add_widget(joystick)
        joystick_layout.add_widget(self.clear_btn)
        joystick_layout.add_widget(Label())
        joystick_layout.add_widget(self.caps_btn)
        joystick_layout.add_widget(self.shift_btn)

        hints_layout = GridLayout(cols=3, rows=3)
        self.hint0 = Label(font_size=buttons_font_size)
        self.hint1 = Label(font_size=buttons_font_size)
        self.hint2 = Label(font_size=buttons_font_size)
        self.hint3 = Label(font_size=buttons_font_size)
        self.hint4 = Label(font_size=buttons_font_size)
        self.hint5 = Label(font_size=buttons_font_size)
        self.hint6 = Label(font_size=buttons_font_size)
        self.hint7 = Label(font_size=buttons_font_size)
        hints_layout.add_widget(self.hint3)
        hints_layout.add_widget(self.hint2)
        hints_layout.add_widget(self.hint1)
        hints_layout.add_widget(self.hint4)
        hints_layout.add_widget(Label())
        hints_layout.add_widget(self.hint0)
        hints_layout.add_widget(self.hint5)
        hints_layout.add_widget(self.hint6)
        hints_layout.add_widget(self.hint7)

        self.release_all_btn = Button(
            text="Release all", font_size=buttons_font_size,
            on_release=self.release_all
        )

        label_col_1 = GridLayout(cols=1, rows=2)
        label_col_1.add_widget(self.label)
        label_col_1.add_widget(self.release_all_btn)

        label_layout = GridLayout(cols=2, rows=1)
        label_layout.add_widget(label_col_1)
        label_layout.add_widget(hints_layout)

        left_side = GridLayout(cols=1, rows=3)
        left_side.add_widget(joystick_layout)
        left_side.add_widget(label_layout)

        self.scroll_btn = Button(
            text="Scroll", font_size=buttons_font_size,
            on_release=self.toggle_scroll,
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

        touchpad_layout = GridLayout(cols=2, rows=2)
        touchpad_layout.add_widget(self.scroll_btn)
        touchpad_layout.add_widget(self.left_click)
        touchpad_layout.add_widget(self.middle_click)
        touchpad_layout.add_widget(self.right_click)

        right_side = GridLayout(cols=1, rows=2)
        right_side.add_widget(self.touchpad)
        right_side.add_widget(touchpad_layout)

        self.root.add_widget(left_side)
        self.root.add_widget(right_side)

        self.prev_letter = code_map['/']
        self.empty_hints = ["" for _ in range(8)]
        self.update_label()

        gc.disable()
        gc.collect()

    def release_all(self, button):
        self.controller.release_all()
        gc.collect()

    def clear(self, button):
        if self.controller.cur_stage == 1.0:
            self.controller.reset_typing()
            self.prev_letter = code_map['/']
            self.update_label()
        else:
            self.controller.send_type(code_map["Bs"])

    def left_pressed(self, button):
        self.controller.send_pressed(self.controller.LeftMouse)

    def left_released(self, button):
        self.controller.send_released(self.controller.LeftMouse)

    def right_pressed(self, button):
        self.controller.send_pressed(self.controller.RightMouse)

    def right_released(self, button):
        self.controller.send_released(self.controller.RightMouse)

    def middle_pressed(self, button):
        self.controller.send_pressed(self.controller.MiddleMouse)

    def middle_released(self, button):
        self.controller.send_released(self.controller.MiddleMouse)

    def update_label(self):
        if not self.visuals_for_joystick:
            return

        cur_stage = self.controller.cur_stage
        if cur_stage < 1:  # cur_stage == 0 or cur_stage == 0.5:
            zone = self.controller.stick_pos_1
        else:  # elif cur_stage == 1 or cur_stage == 1.5:
            zone = self.controller.stick_pos_2

        letter = ''
        if cur_stage == 1.5 or cur_stage == 0:
            letter = self.reverse_code_map[self.prev_letter]

        if cur_stage == 0.5 or cur_stage == 1:
            hints = self.controller.get_direction_hints(self.controller.stick_pos_1)
        else:
            hints = self.empty_hints

        self.hint0.text = hints[0]
        self.hint1.text = hints[1]
        self.hint2.text = hints[2]
        self.hint3.text = hints[3]
        self.hint4.text = hints[4]
        self.hint5.text = hints[5]
        self.hint6.text = hints[6]
        self.hint7.text = hints[7]

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

        self.label.text = f'{letter}\n{cur_stage}: {zone}'

    def update_coordinates(self, joystick, pad):
        # print(joystick.magnitude, joystick.angle)

        letter = self.controller.update_zone(joystick.magnitude, joystick.angle)
        if letter is not None:
            self.controller.send_type(letter)
            self.prev_letter = letter

            #     if is_vibro_enabled():
            #         vibrator.vibrate(0.5)

        self.update_label()


def main():
    APISenderApp().run()


if __name__ == '__main__':
    main()
