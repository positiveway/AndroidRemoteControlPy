from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from code_map import reverse_code_map, code_map
from normal_layout import PressReleaseButton


def make_buttons(app):
    app.w_btn = PressReleaseButton(
        "W", app,
        button="W"
    )
    app.a_btn = PressReleaseButton(
        "A", app,
        button="A"
    )
    app.s_btn = PressReleaseButton(
        "S", app,
        button="S"
    )
    app.d_btn = PressReleaseButton(
        "D", app,
        button="D"
    )


def fill_layout(app):
    app.root = GridLayout(cols=2, rows=1)

    wasd_layout = GridLayout(cols=3, rows=2)
    wasd_layout.add_widget(Label())
    wasd_layout.add_widget(app.w_btn)
    wasd_layout.add_widget(Label())
    wasd_layout.add_widget(app.a_btn)
    wasd_layout.add_widget(app.s_btn)
    wasd_layout.add_widget(app.d_btn)

    upper_left_side = GridLayout(cols=3, rows=3)

    left_side = GridLayout(cols=1, rows=2)
    left_side.add_widget(wasd_layout)
    left_side.add_widget(Label())

    right_side = GridLayout(cols=1, rows=2)
    right_side.add_widget(app.touchpad)
    right_side.add_widget(Label())

    app.root.add_widget(left_side)
    app.root.add_widget(right_side)


def build_layout(app):
    make_buttons(app)
    fill_layout(app)
