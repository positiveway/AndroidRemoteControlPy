import gc

from kivy.app import App

from controller import Controller
from normal_layout import *
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
        self.touchpad.toggle_scroll()

    def release_all(self, button):
        self.controller.release_all()
        self.set_typing_mode(False)

    def double_click(self, button):
        self.controller.double_click()

    def build(self):
        self.touchpad = TouchpadWidget()
        self.touchpad.init()

        self.controller = self.touchpad.controller

        self.is_game_mode = self.controller.is_game_mode

        self.Backspace = Backspace
        self.LeftMouse = LeftMouse
        self.ClearBtnCode = code_map['Clear']
        self.Switch_code = Switch_code
        self.EmptyW_code = EmptyW_code

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
                'Shift': '',
                'Caps': '',
            }

            self.set_typing_mode(False)

        gc.disable()
        gc.collect()

    def clear_typed_text(self):
        self.typed_text = ""
        self.label.text = self.typed_text

    def set_typing_mode(self, state):
        self.typing_mode = state
        self.touchpad_or_btn_layout.toggle()

        self.clear_selection()
        self.clear_typed_text()
        self.update_hints()

    def toggle_typing_mode(self):
        self.set_typing_mode(not self.typing_mode)

    def update_typed_text(self, letter):
        if letter == self.Backspace:
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
        self.update_hints()

    def typing_btn_pressed(self, btn: TypingButton):
        if self.typing_mode:
            letter = self.controller.update_typing_state(btn.direction, btn.is_left)
        else:
            letter = self.controller.mouse_mode_btn_pressed(btn.direction)

        if letter is not None:
            if letter == self.EmptyW_code:
                return
            elif letter == self.ClearBtnCode:
                self.clear_selection()
            elif letter == self.Switch_code:
                self.toggle_typing_mode()
            elif letter == code_map['X2']:
                self.controller.double_click()
            else:
                self.controller.send_type(letter)
                self.update_typed_text(letter)

                #     if is_vibro_enabled():
                #         vibrator.vibrate(0.5)

        self.update_hints()

    def update_button_hints(self, prefix, hints, font_size):
        for num in DIRECTIONS:
            button = getattr(self, f'{prefix}_typing_btn_{num}')
            setattr(button, 'font_size', font_size)
            setattr(button, 'text', hints[button.direction])

    def clear_buttons(self):
        self.update_button_hints('l', self.controller.empty_hints, self.font_size)
        self.update_button_hints('r', self.controller.empty_hints, self.font_size)

    def update_hints(self):
        self.clear_buttons()

        if self.typing_mode:
            if self.controller.typing_btn_1 is None:
                font_size = self.small_font_size

                hints = self.controller.get_preview_hints(is_left=True)
                self.update_button_hints('l', hints, font_size)

                hints = self.controller.get_preview_hints(is_left=False)
                self.update_button_hints('r', hints, font_size)
            else:
                font_size = self.font_size
                hints = self.controller.get_detailed_hints()

                if self.controller.is_left:
                    self.update_button_hints('r', hints, font_size)
                else:
                    self.update_button_hints('l', hints, font_size)
        else:
            font_size = self.font_size
            hints = self.controller.mouse_hints
            self.update_button_hints('l', hints, font_size)

    def on_stop(self):
        self.controller.release_mouse_and_pressed()


def main():
    APISenderApp().run()
    Controller().release_mouse()


if __name__ == '__main__':
    main()
