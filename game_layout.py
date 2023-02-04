from kivy.uix.label import Label
from code_map import *
from common_layout import Layout, make_common_buttons, GameButton


def make_movement_buttons(app, arrows_mode):
    app.w_btn = GameButton(
        "W", app,
        buttons="W", arrows_mode=arrows_mode
    )
    app.a_btn = GameButton(
        "A", app,
        buttons="A", arrows_mode=arrows_mode
    )
    app.s_btn = GameButton(
        "S", app,
        buttons="S", arrows_mode=arrows_mode
    )
    app.d_btn = GameButton(
        "D", app,
        buttons="D", arrows_mode=arrows_mode
    )
    app.wa_btn = GameButton(
        "WA", app,
        buttons=["W", "A"], arrows_mode=arrows_mode
    )
    app.wd_btn = GameButton(
        "WD", app,
        buttons=["W", "D"], arrows_mode=arrows_mode
    )
    app.sa_btn = GameButton(
        "SA", app,
        buttons=["S", "A"], arrows_mode=arrows_mode
    )
    app.sd_btn = GameButton(
        "SD", app,
        buttons=["S", "D"], arrows_mode=arrows_mode
    )


def make_buttons(app):
    app.space_btn = GameButton(
        "Space", app,
        buttons="Space"
    )
    app.shift_btn = GameButton(
        "Shift", app,
        button_codes=Shift
    )


def fill_layout(app):
    app.root = Layout(cols=2)

    wasd_layout = Layout(cols=3, rows=3)
    wasd_layout.add(1, 1, app.wa_btn)
    wasd_layout.add(1, 2, app.w_btn)
    wasd_layout.add(1, 3, app.wd_btn)
    wasd_layout.add(2, 1, app.a_btn)
    wasd_layout.add(2, 2, app.s_btn)
    wasd_layout.add(2, 3, app.d_btn)
    wasd_layout.add(3, 1, app.sa_btn)
    wasd_layout.add(3, 3, app.sd_btn)
    wasd_layout.fill()

    esc_layout = Layout(cols=2, rows=2)
    esc_layout.add(1, 2, app.esc_btn)
    esc_layout.fill()

    shift_layout = Layout(rows=2)
    shift_layout.add(1, 1, app.shift_btn)
    shift_layout.fill()

    upper_left_side = Layout(cols=2, rows=2)
    upper_left_side.add(2, 2, app.space_btn)
    upper_left_side.add(1, 2, esc_layout)
    upper_left_side.add(2, 1, wasd_layout)
    upper_left_side.add(1, 1, shift_layout)
    upper_left_side.fill()

    release_all_layout = Layout(cols=2, rows=2)
    release_all_layout.add(2, 2, app.release_all_btn)
    release_all_layout.fill()

    lower_left_side = Layout(cols=3, rows=3)
    lower_left_side.add(3, 3, release_all_layout)
    lower_left_side.fill()

    left_side = Layout(rows=2)
    left_side.add(1, 1, upper_left_side)
    left_side.add(2, 1, lower_left_side)
    left_side.fill()

    right_side = Layout(rows=2)
    right_side.add(1, 1, app.touchpad)
    right_side.fill()

    app.root.add(1, 1, left_side)
    app.root.add(1, 2, right_side)
    app.root.fill()


def build_layout(app):
    make_common_buttons(app)
    make_movement_buttons(app, False)
    make_buttons(app)
    fill_layout(app)
