import gc
import time

from kivy.app import App

from backend import Controller
from code_map import *
from touchpad import TouchpadWidget

ENABLE_VIBRATE = False


def emtpy_func():
    pass


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

    def release_all(self, button):
        self.controller.release_all()
        gc.collect()

    def double_click(self, button):
        self.controller.send_type([self.LeftMouse])
        time.sleep(0.25)
        self.controller.send_type([self.LeftMouse])

    def build(self):
        self.touchpad = TouchpadWidget()
        self.touchpad.init()

        self.controller = self.touchpad.controller

        self.is_game_mode = self.controller.is_game_mode

        self.Backspace = Backspace
        self.LeftMouse = LeftMouse
        self.ClearBtnCode = code_map['Clear']
        self.reverse_code_map = reverse_code_map

        self.font_size = self.controller.font_size
        self.small_font_size = self.controller.small_font_size

        if self.is_game_mode:
            self.touchpad.clear_typed_text = emtpy_func

            from game_layout import build_layout
            build_layout(self)
        else:
            self.touchpad.clear_typed_text = self.clear_typed_text

            from normal_layout import build_layout
            build_layout(self)

            self.transform_for_display = {
                'Space': ' ',
                'Tab': '\t',
                'Enter': '\n',
                'Del': '',
            }
            self.clear_typed_text()
            self.update_label()

        gc.disable()
        gc.collect()

    def clear_typed_text(self):
        self.typed_text = ""
        self.label.text = self.typed_text

    def update_typed_text(self, letter):
        if letter == Backspace:
            if self.typed_text:
                self.typed_text = self.typed_text[:-1]
        else:
            letter = self.reverse_code_map[letter]
            letter = self.transform_for_display.get(letter, letter)
            self.typed_text += letter

        self.label.text = self.typed_text

    def clear_selection(self):
        self.controller.reset_typing()

    def clear_as_button(self, button):
        self.clear_selection()
        self.update_label()

    def get_typing_btn_func(self, btn_direction):
        def typing_btn_pressed(button):
            letter = self.controller.update_typing_state(btn_direction)
            if letter is not None:
                if letter == self.ClearBtnCode:
                    self.clear_selection()
                else:
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
