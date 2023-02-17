from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

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
    app.clear_btn = UniversalButtonUI(
        "Clear", app,
        func=app.clear_as_button
    )


class UniversalButtonUI(Button):
    def __init__(self, text, app, buttons=None, button_codes=None, func=None, on_press_only=True):
        if func is not None:
            super().__init__(
                text=text, font_size=app.font_size,
                on_press=func,
            )
            return

        if buttons is None and button_codes is None:
            raise ValueError('At least one should be provided')

        elif buttons is not None:
            button_codes = apply_to_seq_or_one(buttons, lambda button: code_map[button])

        if on_press_only:
            def on_press(button):
                app.controller.send_type(button_codes)

            super().__init__(
                text=text, font_size=app.font_size,
                on_press=on_press
            )
        else:
            def on_press(button):
                app.controller.send_pressed(button_codes)

            def on_release(button):
                app.controller.send_released(button_codes)

            super().__init__(
                text=text, font_size=app.font_size,
                on_press=on_press,
                on_release=on_release,
            )


class Layout(GridLayout):
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
