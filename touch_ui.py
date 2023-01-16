import gc
from functools import partial

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.button import Button

from backend import Controller
from code_map import reverse_code_map, code_map
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

    def get_pressed_func(self, button_code):
        def pressed(button):
            self.controller.send_pressed(button_code)

        return pressed

    def get_released_func(self, button_code):
        def released(button):
            self.controller.send_released(button_code)

        return released

    def build(self):
        self.touchpad = TouchpadWidget()
        self.touchpad.init()
        self.controller = self.touchpad.controller

        self.visuals_for_typing = self.controller.visuals_for_typing

        self.font_size = self.controller.font_size
        self.small_font_size = self.controller.small_font_size

        self.reverse_code_map = reverse_code_map

        self.root = GridLayout(cols=2, rows=1)
        # self.root = BoxLayout()
        # self.root.padding = 110

        self.label = Label(font_size=self.font_size)
        # self.label.size_hint_x = 0.25
        # self.label.size_hint_y = 0.9

        self.shift_btn = Button(text="Shift", font_size=self.font_size)
        self.caps_btn = Button(text="Caps", font_size=self.font_size)
        self.clear_btn = Button(text="Bs", font_size=self.font_size, on_release=self.clear)
        self.enter_btn = Button(text="Enter", font_size=self.font_size,
                                on_press=self.get_pressed_func(code_map["Enter"]),
                                on_release=self.get_released_func(code_map["Enter"])
                                )
        self.copy_btn = Button(text="Copy", font_size=self.font_size)
        self.cut_btn = Button(text="Cut", font_size=self.font_size)
        self.paste_btn = Button(text="Paste", font_size=self.font_size)

        typing_extra_buttons = GridLayout(cols=3, rows=2)
        typing_extra_buttons.add_widget(self.caps_btn)
        typing_extra_buttons.add_widget(self.enter_btn)
        typing_extra_buttons.add_widget(self.shift_btn)

        typing_extra_buttons.add_widget(self.copy_btn)
        typing_extra_buttons.add_widget(self.cut_btn)
        typing_extra_buttons.add_widget(self.paste_btn)

        typing_buttons = GridLayout(cols=3, rows=3)
        self.typing_btn_1 = Button(on_press=self.get_typing_btn_func(button_num=1))
        self.typing_btn_2 = Button(on_press=self.get_typing_btn_func(button_num=2))
        self.typing_btn_3 = Button(on_press=self.get_typing_btn_func(button_num=3))
        self.typing_btn_4 = Button(on_press=self.get_typing_btn_func(button_num=4))
        self.typing_btn_5 = Button(on_press=self.get_typing_btn_func(button_num=5))
        self.typing_btn_6 = Button(on_press=self.get_typing_btn_func(button_num=6))
        self.typing_btn_7 = Button(on_press=self.get_typing_btn_func(button_num=7))
        self.typing_btn_8 = Button(on_press=self.get_typing_btn_func(button_num=8))
        self.typing_btn_9 = Button(on_press=self.get_typing_btn_func(button_num=9))
        typing_buttons.add_widget(self.typing_btn_1)
        typing_buttons.add_widget(self.typing_btn_2)
        typing_buttons.add_widget(self.typing_btn_3)
        typing_buttons.add_widget(self.typing_btn_4)
        typing_buttons.add_widget(self.clear_btn)
        typing_buttons.add_widget(self.typing_btn_6)
        typing_buttons.add_widget(self.typing_btn_7)
        typing_buttons.add_widget(self.typing_btn_8)
        typing_buttons.add_widget(self.typing_btn_9)

        typing_layout = GridLayout(cols=1, rows=2)
        typing_layout.add_widget(typing_buttons)
        typing_layout.add_widget(typing_extra_buttons)

        self.release_all_btn = Button(
            text="Release all", font_size=self.font_size,
            on_press=self.release_all
        )

        label_col_1 = GridLayout(cols=1, rows=2)
        label_col_1.add_widget(self.label)
        label_col_1.add_widget(self.release_all_btn)

        label_col_2 = GridLayout(cols=1, rows=2)
        label_col_2.add_widget(Label())
        label_col_2.add_widget(Label())

        label_layout = GridLayout(cols=2, rows=1)
        label_layout.add_widget(label_col_1)
        label_layout.add_widget(label_col_2)

        left_side = GridLayout(cols=1, rows=2)
        left_side.add_widget(typing_layout)
        left_side.add_widget(label_layout)

        self.scroll_btn = Button(
            text="Scroll", font_size=self.font_size,
            on_release=self.toggle_scroll,
        )
        self.left_click = Button(
            text="Left", font_size=self.font_size,
            on_press=self.get_pressed_func(self.controller.LeftMouse),
            on_release=self.get_released_func(self.controller.LeftMouse)
        )
        self.right_click = Button(
            text="Right", font_size=self.font_size,
            on_press=self.get_pressed_func(self.controller.RightMouse),
            on_release=self.get_released_func(self.controller.RightMouse)
        )
        self.middle_click = Button(
            text="Middle", font_size=self.font_size,
            on_press=self.get_pressed_func(self.controller.MiddleMouse),
            on_release=self.get_released_func(self.controller.MiddleMouse)
        )

        touchpad_layout = GridLayout(cols=2, rows=2)
        touchpad_layout.add_widget(self.middle_click)
        touchpad_layout.add_widget(self.right_click)

        touchpad_layout.add_widget(self.scroll_btn)
        touchpad_layout.add_widget(self.left_click)

        right_side = GridLayout(cols=1, rows=2)
        right_side.add_widget(self.touchpad)
        right_side.add_widget(touchpad_layout)

        self.root.add_widget(left_side)
        self.root.add_widget(right_side)

        self.reverse_button_nums = {
            1: 'UpLeft', 2: 'Up', 3: 'UpRight',
            4: 'Left', 5: 'Central', 6: 'Right',
            7: 'DownLeft', 8: 'Down', 9: 'DownRight',
        }
        self.prev_letter = code_map['/']
        self.update_label()

        gc.disable()
        gc.collect()

    def release_all(self, button):
        self.controller.release_all()
        gc.collect()

    def clear(self, button):
        if self.controller.typing_btn_1 is not None:
            self.controller.reset_typing()
            self.prev_letter = code_map['/']
            self.update_label()
        else:
            self.controller.send_type(code_map["Bs"])

    def get_typing_btn_func(self, button_num):
        def typing_btn_pressed(button):
            letter = self.controller.update_zone(button_num)
            if letter is not None:
                self.controller.send_type(letter)
                self.prev_letter = letter

                #     if is_vibro_enabled():
                #         vibrator.vibrate(0.5)

            self.update_label()

        return typing_btn_pressed

    def update_label(self):
        if not self.visuals_for_typing:
            return

        if self.controller.typing_btn_1 is None:
            cur_stage = 0
            direction = ""
        else:
            cur_stage = 1
            direction = self.reverse_button_nums[self.controller.typing_btn_1]

        letter = ''
        if cur_stage == 0:
            letter = self.reverse_code_map[self.prev_letter]

        font_size = self.small_font_size
        if cur_stage == 1:
            font_size = self.font_size

        self.typing_btn_1.font_size = font_size
        self.typing_btn_2.font_size = font_size
        self.typing_btn_3.font_size = font_size
        self.typing_btn_4.font_size = font_size
        self.typing_btn_5.font_size = font_size
        self.typing_btn_6.font_size = font_size
        self.typing_btn_7.font_size = font_size
        self.typing_btn_8.font_size = font_size
        self.typing_btn_9.font_size = font_size

        hints = self.controller.get_direction_hints()

        if cur_stage == 1:
            hints = hints[self.controller.typing_btn_1]

            self.typing_btn_1.text = hints[1]
            self.typing_btn_2.text = hints[2]
            self.typing_btn_3.text = hints[3]
            self.typing_btn_4.text = hints[4]
            self.typing_btn_5.text = hints[5]
            self.typing_btn_6.text = hints[6]
            self.typing_btn_7.text = hints[7]
            self.typing_btn_8.text = hints[8]
            self.typing_btn_9.text = hints[9]
        else:
            self.typing_btn_1.text = hints[1][0]
            self.typing_btn_2.text = hints[2][0]
            self.typing_btn_3.text = hints[3][0]
            self.typing_btn_4.text = hints[4][0]
            self.typing_btn_5.text = hints[5][0]
            self.typing_btn_6.text = hints[6][0]
            self.typing_btn_7.text = hints[7][0]
            self.typing_btn_8.text = hints[8][0]
            self.typing_btn_9.text = hints[9][0]

        self.label.text = f'{letter}\n{cur_stage}: {direction}'

    def on_stop(self):
        self.controller.release_mouse_and_pressed()


def main():
    APISenderApp().run()
    Controller().release_mouse()


if __name__ == '__main__':
    main()
