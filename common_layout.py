from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout

from code_map import *
from common import *


def make_common_buttons(app):
    app.enter_btn = UniversalButtonUI(
        "Enter", app,
        button_codes=Enter
    )
    app.release_all_btn = UniversalButtonUI(
        "Release", app,
        func=app.release_all
    )


class Pair:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def as_tuple(self):
        return self.x, self.y


class UniversalButtonUI(Button):
    def set_pos(self, x, y):
        self.pos = (x, y)

    def __init__(
            self, text, app,
            size_rel: Pair = None,
            buttons=None, button_codes=None, func=None,
            on_press_only=True
    ):
        if size_rel is None:
            size_rel = Pair(10, 10)

        def self_init(**kwargs):
            super(UniversalButtonUI, self).__init__(
                size_hint=size_rel.as_tuple(),
                text=text, font_size=app.font_size,
                **kwargs,
            )

        if func is not None:
            self_init(on_press=func)
            return

        if buttons is None and button_codes is None:
            raise ValueError('At least one should be provided')

        elif buttons is not None:
            button_codes = apply_to_seq_or_one(buttons, lambda button: code_map[button])

        if on_press_only:
            def on_press(button):
                app.controller.send_type(button_codes)

            self_init(on_press=on_press)
        else:
            def on_press(button):
                app.controller.send_pressed(button_codes)

            def on_release(button):
                app.controller.send_released(button_codes)

            self_init(
                on_press=on_press,
                on_release=on_release,
            )



class AutoGridLayout(GridLayout):
    def __init__(self, rows=1, cols=1, inverted=''):
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.inverted = inverted
        super().__init__(rows=rows, cols=cols)

    def add(self, row, col, widget):
        if 'y' in self.inverted:
            row = self.rows - row
        else:
            row -= 1

        if 'x' in self.inverted:
            col = self.cols - col
        else:
            col -= 1

        if self.grid[row][col] is not None:
            raise ValueError("Duplicate position")

        self.grid[row][col] = widget

    def fill(self):
        for row in range(self.rows):
            for col in range(self.cols):
                widget = self.grid[row][col]
                if widget is None:
                    widget = Label()

                self.add_widget(widget)
