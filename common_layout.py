from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from code_map import *


def make_common_buttons(app):
    app.enter_btn = UniversalButton(
        "Enter", app,
        button_codes=Enter, on_press_only=True
    )
    app.esc_btn = UniversalButton(
        "Esc", app,
        button_codes=Esc, on_press_only=True
    )
    app.release_all_btn = UniversalButton(
        "Release", app,
        func=app.release_all
    )
    app.clear_btn = UniversalButton(
        "Clear", app,
        func=app.clear_as_button
    )


class UniversalButton(Button):
    def __init__(self, text, app, buttons=None, button_codes=None, func=None, on_press_only=False):
        if func is not None:
            super().__init__(
                text=text, font_size=app.font_size,
                on_press=func,
            )
            return

        if buttons is None and button_codes is None:
            raise ValueError('At least one should be provided')
        elif buttons is not None:
            if not isinstance(buttons, (tuple, list)):
                buttons = tuple([buttons])

            button_codes = [code_map[button] for button in buttons]

        else:
            if not isinstance(button_codes, (tuple, list)):
                button_codes = tuple([button_codes])

        reverse_codes = tuple(reversed(button_codes))

        if on_press_only:
            def on_press(button):
                for button_code in button_codes:
                    app.controller.send_pressed(button_code)

                for button_code in reverse_codes:
                    app.controller.send_released(button_code)

            super().__init__(
                text=text, font_size=app.font_size,
                on_press=on_press
            )
        else:
            def on_press(button):
                for button_code in button_codes:
                    app.controller.send_pressed(button_code)

            def on_release(button):
                for button_code in reverse_codes:
                    app.controller.send_released(button_code)

            super().__init__(
                text=text, font_size=app.font_size,
                on_press=on_press,
                on_release=on_release,
            )


class Layout(GridLayout):
    def __init__(self, rows, cols, inverted=False):
        self.grid = [[None for i in range(cols)] for j in range(rows)]
        self.inverted = inverted
        super().__init__(rows=rows, cols=cols)

    def add(self, row, col, widget):
        col -= 1

        if self.inverted:
            row = self.rows - row
        else:
            row -= 1

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
