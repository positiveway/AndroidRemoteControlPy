from kivy.uix.label import Label
from code_map import *
from common import apply_to_seq_or_one
from common_layout import AutoGridLayout, make_common_buttons, UniversalButtonUI


class GameButtonUI(UniversalButtonUI):
    def __init__(self, text, app, buttons=None, button_codes=None, func=None):
        super().__init__(text, app, buttons=buttons,
                         button_codes=button_codes, func=func,
                         on_press_only=False)


def replace_by_arrow(button):
    return {
        'w': 'Up',
        's': 'Down',
        'a': 'Left',
        'd': 'Right',
    }[button.lower()]


class ArrowButtonUI(GameButtonUI):
    def __init__(self, text, app, buttons):
        if app.controller.arrows_mode:
            buttons = apply_to_seq_or_one(buttons, replace_by_arrow)

        super().__init__(text, app, buttons=buttons)


def make_movement_buttons(app):
    app.w_btn = ArrowButtonUI(
        "W", app,
        buttons="W",
    )
    app.a_btn = ArrowButtonUI(
        "A", app,
        buttons="A",
    )
    app.s_btn = ArrowButtonUI(
        "S", app,
        buttons="S",
    )
    app.d_btn = ArrowButtonUI(
        "D", app,
        buttons="D",
    )
    app.wa_btn = ArrowButtonUI(
        "WA", app,
        buttons=["W", "A"],
    )
    app.wd_btn = ArrowButtonUI(
        "WD", app,
        buttons=["W", "D"],
    )
    app.sa_btn = ArrowButtonUI(
        "SA", app,
        buttons=["S", "A"],
    )
    app.sd_btn = ArrowButtonUI(
        "SD", app,
        buttons=["S", "D"],
    )


def make_buttons(app):
    app.space_btn = GameButtonUI(
        "Space", app,
        buttons="Space"
    )
    app.shift_btn = GameButtonUI(
        "Shift", app,
        button_codes=Shift
    )

    app.esc_btn = GameButtonUI(
        "Esc", app,
        button_codes=Esc
    )


def fill_layout(app):
    app.root = AutoGridLayout(cols=2)

    wasd_layout = AutoGridLayout(cols=3, rows=3)
    wasd_layout.add(1, 1, app.wa_btn)
    wasd_layout.add(1, 2, app.w_btn)
    wasd_layout.add(1, 3, app.wd_btn)
    wasd_layout.add(2, 1, app.a_btn)
    wasd_layout.add(2, 2, app.s_btn)
    wasd_layout.add(2, 3, app.d_btn)
    wasd_layout.add(3, 1, app.sa_btn)
    wasd_layout.add(3, 3, app.sd_btn)
    wasd_layout.fill()

    esc_layout = AutoGridLayout(cols=2, rows=2)
    esc_layout.add(1, 2, app.esc_btn)
    esc_layout.fill()

    shift_layout = AutoGridLayout(rows=2)
    shift_layout.add(1, 1, app.shift_btn)
    shift_layout.fill()

    upper_left_side = AutoGridLayout(cols=2, rows=2)
    upper_left_side.add(2, 2, app.space_btn)
    upper_left_side.add(1, 2, esc_layout)
    upper_left_side.add(2, 1, wasd_layout)
    upper_left_side.add(1, 1, shift_layout)
    upper_left_side.fill()

    release_all_layout = AutoGridLayout(cols=2, rows=2)
    release_all_layout.add(2, 2, app.release_all_btn)
    release_all_layout.fill()

    lower_left_side = AutoGridLayout(cols=3, rows=3)
    lower_left_side.add(3, 3, release_all_layout)
    lower_left_side.fill()

    left_side = AutoGridLayout(rows=2, inverted='y')
    left_side.add(1, 1, upper_left_side)
    left_side.add(2, 1, lower_left_side)
    left_side.fill()

    right_side = AutoGridLayout(rows=2, inverted='y')
    right_side.add(1, 1, app.touchpad)
    right_side.fill()

    app.root.add(1, 1, left_side)
    app.root.add(1, 2, right_side)
    app.root.fill()


def build_layout(app):
    make_common_buttons(app)
    make_movement_buttons(app)
    make_buttons(app)
    fill_layout(app)
