from kivy.uix.label import Label
from code_map import *
from common_layout import Layout, make_common_buttons, UniversalButton


def make_buttons(app):
    app.w_btn = UniversalButton(
        "W", app,
        buttons="W"
    )
    app.a_btn = UniversalButton(
        "A", app,
        buttons="A"
    )
    app.s_btn = UniversalButton(
        "S", app,
        buttons="S"
    )
    app.d_btn = UniversalButton(
        "D", app,
        buttons="D"
    )
    app.wa_btn = UniversalButton(
        "WA", app,
        buttons=["W", "A"]
    )
    app.wd_btn = UniversalButton(
        "WD", app,
        buttons=["W", "D"]
    )
    app.space_btn = UniversalButton(
        "Space", app,
        buttons="Space"
    )


def fill_layout(app):
    app.root = Layout(cols=2, rows=1)

    wasd_layout = Layout(cols=3, rows=2)
    wasd_layout.add(1, 1, app.wa_btn)
    wasd_layout.add(1, 2, app.w_btn)
    wasd_layout.add(1, 3, app.wd_btn)
    wasd_layout.add(2, 1, app.a_btn)
    wasd_layout.add(2, 2, app.s_btn)
    wasd_layout.add(2, 3, app.d_btn)
    wasd_layout.fill()

    upper_left_side = Layout(cols=2, rows=2)
    upper_left_side.add(1, 1, app.space_btn)
    upper_left_side.add(1, 2, app.esc_btn)
    upper_left_side.add(2, 1, wasd_layout)
    upper_left_side.fill()

    lower_left_side = Layout(cols=3, rows=3)
    lower_left_side.add(3, 1, app.release_all_btn)
    lower_left_side.fill()

    left_side = Layout(cols=1, rows=2)
    left_side.add(1, 1, upper_left_side)
    left_side.add(2, 1, lower_left_side)
    left_side.fill()

    right_side = Layout(cols=1, rows=2)
    right_side.add(1, 1, app.touchpad)
    right_side.fill()

    app.root.add(1, 1, left_side)
    app.root.add(1, 2, right_side)
    app.root.fill()


def build_layout(app):
    make_common_buttons(app)
    make_buttons(app)
    fill_layout(app)
