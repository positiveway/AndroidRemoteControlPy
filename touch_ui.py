import gc

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

    def get_send_type_func(self, button_code):
        def send_type(button):
            self.controller.send_type(button_code)

        return send_type

    def get_send_seq_func(self, seq):
        def send_seq(button):
            self.controller.send_sequence(seq)

        return send_seq

    def build(self):
        self.touchpad = TouchpadWidget()
        self.touchpad.init()
        self.touchpad.reset_typed_text = self.reset_typed_text

        self.controller = self.touchpad.controller

        self.Ctrl = self.controller.Ctrl
        self.Shift = self.controller.Shift
        self.Backspace = self.controller.Backspace

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
        self.clear_btn = Button(text="Bs", font_size=self.font_size, on_press=self.clear)
        self.enter_btn = Button(text="Enter", font_size=self.font_size,
                                on_press=self.get_send_type_func(code_map["Enter"]),
                                )
        self.copy_btn = Button(text="Copy", font_size=self.font_size,
                               on_press=self.get_send_seq_func([self.Ctrl, code_map["C"]]))
        self.cut_btn = Button(text="Cut", font_size=self.font_size,
                              on_press=self.get_send_seq_func([self.Ctrl, code_map["X"]]))
        self.paste_btn = Button(text="Paste", font_size=self.font_size,
                                on_press=self.get_send_seq_func([self.Ctrl, code_map["V"]]))

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
        typing_row_1 = GridLayout(cols=2, rows=1)
        typing_row_1.add_widget(typing_buttons)
        typing_row_1.add_widget(Label())
        typing_layout.add_widget(typing_row_1)
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
            on_press=self.toggle_scroll,
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

        self.transform_for_display = {
            'Space': ' ',
            'Tab': '\t',
            'Enter': '\n',
            'Del': '',
        }
        self.reset_typed_text()
        self.update_label()

        gc.disable()
        gc.collect()

    def release_all(self, button):
        self.controller.release_all()
        gc.collect()

    def reset_typed_text(self):
        self.typed_text = ""
        self.label.text = self.typed_text

    def update_typed_text(self, letter):
        if letter == self.Backspace:
            if self.typed_text:
                self.typed_text = self.typed_text[:-1]
        else:
            letter = self.reverse_code_map[letter]
            letter = self.transform_for_display.get(letter, letter)
            self.typed_text += letter

        self.label.text = self.typed_text

    def clear(self, button):
        if self.controller.typing_btn_1 is not None:
            self.controller.reset_typing()
            self.update_label()
        else:
            self.controller.send_type(self.Backspace)
            self.update_typed_text(self.Backspace)

    def get_typing_btn_func(self, button_num):
        def typing_btn_pressed(button):
            letter = self.controller.update_typing_state(button_num)
            if letter is not None:
                self.controller.send_type(letter)
                self.update_typed_text(letter)

                #     if is_vibro_enabled():
                #         vibrator.vibrate(0.5)

            self.update_label()

        return typing_btn_pressed

    def update_label(self):
        if self.controller.typing_btn_1 is None:
            font_size = self.small_font_size
            hints = self.controller.get_preview_hints()
        else:
            font_size = self.font_size
            hints = self.controller.get_detailed_hints(self.controller.typing_btn_1)

        self.typing_btn_1.font_size = font_size
        self.typing_btn_2.font_size = font_size
        self.typing_btn_3.font_size = font_size
        self.typing_btn_4.font_size = font_size
        self.typing_btn_5.font_size = font_size
        self.typing_btn_6.font_size = font_size
        self.typing_btn_7.font_size = font_size
        self.typing_btn_8.font_size = font_size
        self.typing_btn_9.font_size = font_size

        self.typing_btn_1.text = hints[1]
        self.typing_btn_2.text = hints[2]
        self.typing_btn_3.text = hints[3]
        self.typing_btn_4.text = hints[4]
        self.typing_btn_5.text = hints[5]
        self.typing_btn_6.text = hints[6]
        self.typing_btn_7.text = hints[7]
        self.typing_btn_8.text = hints[8]
        self.typing_btn_9.text = hints[9]

    def on_stop(self):
        self.controller.release_mouse_and_pressed()


def main():
    APISenderApp().run()
    Controller().release_mouse()


if __name__ == '__main__':
    main()
