import gc

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window

from common_layout import Pair
from normal_layout import *
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
        self.touchpad.toggle_scroll()

    def release_all(self, button):
        self.touchpad.full_reset()
        self.controller.release_all()

        if not self.controller.is_game_mode:
            self.set_typing_mode(False)

        gc.collect()

    def double_click(self, button):
        self.controller.double_click()

    def tune_gc(self):
        # Clean up what might be garbage so far.
        gc.collect(2)
        # Exclude current items from future GC.
        gc.freeze()

        allocs, gen1, gen2 = gc.get_threshold()
        allocs = 50_000  # Start the GC sequence every 50K not 700 allocations.
        gen1 = gen1 * 2
        gen2 = gen2 * 2
        gc.set_threshold(allocs, gen1, gen2)

    def delayed_init(self, dt):
        max_window_size = Window.size
        max_window_size = Pair(*max_window_size)

        resize_layout(self, max_window_size)

    def build(self):
        self.touchpad = TouchpadWidget()
        self.touchpad.init()
        Clock.schedule_interval(self.touchpad.send_buffer, 0.001)

        self.controller = self.touchpad.controller

        self.is_game_mode = self.controller.is_game_mode

        self.Backspace = Backspace
        self.LeftMouse = LeftMouse
        self.ClearBtnCode = code_map['Clear']
        self.Switch_code = Switch_code
        self.EmptyLetterCode = EmptyLetterCode

        self.reverse_code_map = reverse_code_map

        self.font_size = self.controller.font_size

        Window.maximize()

        if self.is_game_mode:
            from archive.game_layout import build_layout
            build_layout(self)
        else:
            from normal_layout import build_layout
            build_layout(self)

            self.set_typing_mode(False)

        self.tune_gc()

        Clock.schedule_once(self.delayed_init, 0.5)

    def set_typing_mode(self, state):
        self.typing_mode = state

    def toggle_typing_mode(self):
        self.set_typing_mode(not self.typing_mode)

    def reset_typing(self):
        self.controller.reset_typing()

    def on_stop(self):
        self.controller.release_mouse_and_pressed()


def main():
    APISenderApp().run()


if __name__ == '__main__':
    main()
