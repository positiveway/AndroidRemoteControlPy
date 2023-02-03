from kivy.uix.label import Label
from code_map import *
from common_layout import UniversalButton, Layout, make_common_buttons


def make_buttons(app):
    app.shift_btn = UniversalButton(
        "Shift", app,
        button_codes=Shift
    )
    app.caps_btn = UniversalButton(
        "Caps", app,
        button_codes=Caps
    )
    app.up_btn = UniversalButton(
        "Up", app,
        buttons="Up"
    )
    app.down_btn = UniversalButton(
        "Down", app,
        buttons="Down"
    )
    app.left_btn = UniversalButton(
        "Left", app,
        buttons="Left"
    )
    app.right_btn = UniversalButton(
        "Right", app,
        buttons="Right"
    )
    app.left_click = UniversalButton(
        "Left", app,
        button_codes=LeftMouse
    )
    app.right_click = UniversalButton(
        "Right", app,
        button_codes=RightMouse
    )
    app.middle_click = UniversalButton(
        "Middle", app,
        button_codes=MiddleMouse
    )

    app.scroll_btn = UniversalButton(
        "Scroll", app,
        func=app.toggle_scroll,
    )
    app.double_click_btn = UniversalButton(
        "X2", app,
        func=app.double_click
    )
    app.space_btn = UniversalButton(
        "Space", app,
        button_codes=Space, on_press_only=True
    )
    app.copy_btn = UniversalButton(
        "Copy", app,
        buttons='Copy', on_press_only=True
    )
    app.cut_btn = UniversalButton(
        "Cut", app,
        buttons='Cut', on_press_only=True
    )
    app.paste_btn = UniversalButton(
        "Paste", app,
        buttons='Paste', on_press_only=True
    )
    app.select_all_btn = UniversalButton(
        "Select", app,
        buttons='Select', on_press_only=True
    )
    app.format_btn = UniversalButton(
        "Format", app,
        buttons='Format', on_press_only=True
    )
    app.search_btn = UniversalButton(
        "Search", app,
        buttons='Search', on_press_only=True
    )
    app.replace_btn = UniversalButton(
        "Replace", app,
        buttons='Replace', on_press_only=True
    )
    app.undo_btn = UniversalButton(
        "Undo", app,
        buttons='Undo', on_press_only=True
    )
    app.redo_btn = UniversalButton(
        "Redo", app,
        buttons='Redo', on_press_only=True
    )


def fill_layout(app):
    app.root = Layout(cols=2, rows=1)
    # app.root = BoxLayout()
    # app.root.padding = 110

    app.label = Label(font_size=app.font_size)
    # app.label.size_hint_x = 0.25
    # app.label.size_hint_y = 0.9

    release_all_layout = Layout(cols=2, rows=2)
    release_all_layout.add(2, 1, app.release_all_btn)
    release_all_layout.fill()

    arrows_layout = Layout(cols=3, rows=2)
    arrows_layout.add(1, 2, app.up_btn)
    arrows_layout.add(2, 1, app.left_btn)
    arrows_layout.add(2, 2, app.down_btn)
    arrows_layout.add(2, 3, app.right_btn)
    arrows_layout.fill()

    arrows_compact_layout = Layout(rows=2, cols=1, inverted=True)
    arrows_compact_layout.add(1, 1, arrows_layout)
    arrows_compact_layout.fill()

    typing_layout = Layout(cols=2, rows=2, inverted=True)
    typing_layout.add(1, 1, app.typing_buttons)
    typing_layout.add(1, 2, arrows_compact_layout)
    typing_layout.add(2, 1, app.label)
    typing_layout.fill()

    touchpad_layout = Layout(cols=2, rows=2, inverted=True)
    touchpad_layout.add(1, 1, app.middle_click)
    touchpad_layout.add(1, 2, app.right_click)

    touchpad_layout.add(2, 1, release_all_layout)
    touchpad_layout.add(2, 2, app.double_click_btn)
    touchpad_layout.fill()

    right_side = Layout(cols=1, rows=2, inverted=True)
    right_side.add(1, 1, app.touchpad)
    right_side.add(2, 1, touchpad_layout)
    right_side.fill()

    app.root.add(1, 1, typing_layout)
    app.root.add(1, 2, right_side)
    app.root.fill()


def build_layout(app):
    make_common_buttons(app)
    make_buttons(app)
    fill_layout(app)
