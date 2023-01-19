from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from code_map import code_map


def make_common_buttons(app):
    app.enter_btn = PressFuncButton(
        "Enter", app,
        func=app.get_send_type_func(code_map["Enter"])
    )
    app.esc_btn = PressFuncButton(
        "Esc", app,
        func=app.get_send_type_func(app.controller.Esc)
    )
    app.release_all_btn = PressFuncButton(
        "Release", app,
        func=app.release_all
    )


class Layout(GridLayout):
    def __init__(self, rows, cols):
        self.grid = [[None for i in range(cols)] for j in range(rows)]
        super().__init__(rows=rows, cols=cols)

    def add(self, row, col, widget):
        row -= 1
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


class PressReleaseButton(Button):
    def __init__(self, text, app, button=None, button_code=None):
        if button_code is None and button is None:
            raise ValueError()
        if button_code is None:
            button_code = code_map[button]

        super().__init__(
            text=text, font_size=app.font_size,
            on_press=app.get_on_press_func(button_code),
            on_release=app.get_on_release_func(button_code)
        )


class PressFuncButton(Button):
    def __init__(self, text, app, func):
        super().__init__(
            text=text, font_size=app.font_size,
            on_press=func
        )
