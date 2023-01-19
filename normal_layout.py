from kivy.uix.label import Label
from code_map import *
from common_layout import PressReleaseButton, PressFuncButton, Layout, make_common_buttons


def make_buttons(app):
    app.shift_btn = PressReleaseButton(
        "Shift", app,
        button_code=Shift
    )
    app.caps_btn = PressReleaseButton(
        "Caps", app,
        button_code=Caps
    )
    app.up_btn = PressReleaseButton(
        "Up", app,
        button="Up"
    )
    app.down_btn = PressReleaseButton(
        "Down", app,
        button="Down"
    )
    app.left_btn = PressReleaseButton(
        "Left", app,
        button="Left"
    )
    app.right_btn = PressReleaseButton(
        "Right", app,
        button="Right"
    )
    app.left_click = PressReleaseButton(
        "Left", app,
        button_code=LeftMouse
    )
    app.right_click = PressReleaseButton(
        "Right", app,
        button_code=RightMouse
    )
    app.middle_click = PressReleaseButton(
        "Middle", app,
        button_code=MiddleMouse
    )

    app.double_click_btn = PressFuncButton(
        "X2", app,
        func=app.double_click
    )
    app.space_btn = PressFuncButton(
        "Space", app,
        func=app.get_send_type_func(Space)
    )
    app.copy_btn = PressFuncButton(
        "Copy", app,
        func=app.get_send_type_func(code_map['Copy'])
    )
    app.cut_btn = PressFuncButton(
        "Cut", app,
        func=app.get_send_type_func(code_map['Cut'])
    )
    app.paste_btn = PressFuncButton(
        "Paste", app,
        func=app.get_send_type_func(code_map['Paste'])
    )
    app.select_all_btn = PressFuncButton(
        "Select", app,
        func=app.get_send_type_func(code_map['Select'])
    )
    app.format_btn = PressFuncButton(
        "Format", app,
        func=app.get_send_type_func(code_map['Format'])
    )
    app.search_btn = PressFuncButton(
        "Search", app,
        func=app.get_send_type_func(code_map['Search'])
    )
    app.replace_btn = PressFuncButton(
        "Replace", app,
        func=app.get_send_type_func(code_map['Replace'])
    )
    app.undo_btn = PressFuncButton(
        "Undo", app,
        func=app.get_send_type_func(code_map['Undo'])
    )
    app.redo_btn = PressFuncButton(
        "Redo", app,
        func=app.get_send_type_func(code_map['Redo'])
    )
    app.scroll_btn = PressFuncButton(
        "Scroll", app,
        func=app.toggle_scroll,
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

    arrows_compact_layout = Layout(rows=2, cols=1)
    arrows_compact_layout.add(1, 1, arrows_layout)
    arrows_compact_layout.fill()

    typing_layout = Layout(cols=2, rows=2)
    typing_layout.add(1, 1, app.typing_buttons)
    typing_layout.add(2, 1, arrows_compact_layout)
    typing_layout.add(2, 2, app.label)
    typing_layout.fill()

    touchpad_layout = Layout(cols=2, rows=2)
    touchpad_layout.add(1, 1, app.middle_click)
    touchpad_layout.add(1, 2, app.right_click)

    touchpad_layout.add(2, 1, release_all_layout)
    touchpad_layout.add(2, 2, app.double_click_btn)
    touchpad_layout.fill()

    right_side = Layout(cols=1, rows=2)
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
