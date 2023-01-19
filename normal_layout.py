from kivy.uix.button import Button
from kivy.uix.label import Label
from code_map import code_map
from common_layout import PressReleaseButton, PressFuncButton, Layout


def make_buttons(app):
    app.shift_btn = PressReleaseButton(
        "Shift", app,
        button_code=app.Shift
    )
    app.caps_btn = PressReleaseButton(
        "Caps", app,
        button_code=app.Caps
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
        button_code=app.controller.LeftMouse
    )
    app.right_click = PressReleaseButton(
        "Right", app,
        button_code=app.controller.RightMouse
    )
    app.middle_click = PressReleaseButton(
        "Middle", app,
        button_code=app.controller.MiddleMouse
    )

    app.double_click_btn = PressFuncButton(
        "X2", app,
        func=app.double_click
    )

    app.clear_btn = PressFuncButton(
        "Bs", app,
        func=app.clear
    )
    app.enter_btn = PressFuncButton(
        "Enter", app,
        func=app.get_send_type_func(code_map["Enter"])
    )
    app.space_btn = PressFuncButton(
        "Space", app,
        func=app.get_send_type_func(code_map["Space"])
    )
    app.copy_btn = PressFuncButton(
        "Copy", app,
        func=app.get_send_seq_func([app.Ctrl, code_map["C"]])
    )
    app.cut_btn = PressFuncButton(
        "Cut", app,
        func=app.get_send_seq_func([app.Ctrl, code_map["X"]])
    )
    app.paste_btn = PressFuncButton(
        "Paste", app,
        func=app.get_send_seq_func([app.Ctrl, code_map["V"]])
    )
    app.select_all_btn = PressFuncButton(
        "Select", app,
        func=app.get_send_seq_func([app.Ctrl, code_map["A"]])
    )
    app.format_btn = PressFuncButton(
        "Format", app,
        func=app.get_send_seq_func([app.Ctrl, code_map["L"]])
    )
    app.search_btn = PressFuncButton(
        "Search", app,
        func=app.get_send_seq_func([app.Ctrl, code_map["F"]])
    )
    app.replace_btn = PressFuncButton(
        "Replace", app,
        func=app.get_send_seq_func([app.Ctrl, code_map["R"]])
    )
    app.undo_btn = PressFuncButton(
        "Undo", app,
        func=app.get_send_seq_func([app.Ctrl, code_map["Z"]])
    )
    app.redo_btn = PressFuncButton(
        "Redo", app,
        func=app.get_send_seq_func([app.Ctrl, app.Shift, code_map["Z"]])
    )
    app.esc_btn = PressFuncButton(
        "Esc", app,
        func=app.get_send_type_func(app.controller.Esc)
    )
    app.release_all_btn = PressFuncButton(
        "Release", app,
        func=app.release_all
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

    typing_extra_buttons = Layout(cols=3, rows=2)
    typing_extra_buttons.add(1, 1, app.caps_btn)
    typing_extra_buttons.add(1, 2, app.enter_btn)
    typing_extra_buttons.add(1, 3, app.shift_btn)

    typing_extra_buttons.add(2, 1, app.copy_btn)
    typing_extra_buttons.add(2, 2, app.cut_btn)
    typing_extra_buttons.add(2, 3, app.paste_btn)
    typing_extra_buttons.fill()

    right_of_typing_layout = Layout(cols=2, rows=2)
    right_of_typing_layout.add(1, 2, app.double_click_btn)
    right_of_typing_layout.add(2, 2, app.space_btn)
    right_of_typing_layout.fill()

    typing_row_1 = Layout(cols=2, rows=1)
    typing_row_1.add(1, 1, app.typing_buttons)
    typing_row_1.add(1, 2, right_of_typing_layout)
    typing_row_1.fill()

    typing_layout = Layout(cols=1, rows=2)
    typing_layout.add(1, 1, typing_row_1)
    typing_layout.add(2, 1, typing_extra_buttons)
    typing_layout.fill()

    release_all_layout = Layout(cols=2, rows=2)
    release_all_layout.add(2, 1, app.release_all_btn)
    release_all_layout.fill()

    label_row_2 = Layout(cols=2, rows=1)
    label_row_2.add(1, 1, release_all_layout)
    label_row_2.add(1, 2, app.label)
    label_row_2.fill()

    extra_buttons_2 = Layout(cols=2, rows=1)
    extra_buttons_2_left = Layout(cols=3, rows=2)
    extra_buttons_2_right = Layout(cols=3, rows=2)

    extra_buttons_2_left.add(1, 2, app.up_btn)
    extra_buttons_2_left.add(2, 1, app.left_btn)
    extra_buttons_2_left.add(2, 2, app.down_btn)
    extra_buttons_2_left.add(2, 3, app.right_btn)
    extra_buttons_2_left.fill()

    extra_buttons_2_right.add(1, 1, app.select_all_btn)
    extra_buttons_2_right.add(1, 2, app.undo_btn)
    extra_buttons_2_right.add(1, 3, app.redo_btn)
    extra_buttons_2_right.fill()

    extra_buttons_2.add(1, 1, extra_buttons_2_left)
    extra_buttons_2.add(1, 2, extra_buttons_2_right)
    extra_buttons_2.fill()

    label_layout = Layout(cols=1, rows=2)
    label_layout.add(1, 1, extra_buttons_2)
    label_layout.add(2, 1, label_row_2)
    label_layout.fill()

    left_side = Layout(cols=1, rows=2)
    left_side.add(1, 1, typing_layout)
    left_side.add(2, 1, label_layout)
    left_side.fill()

    touchpad_layout = Layout(cols=2, rows=2)
    touchpad_layout.add(1, 1, app.middle_click)
    touchpad_layout.add(1, 2, app.right_click)

    touchpad_layout.add(2, 1, app.search_btn)
    touchpad_layout.add(2, 2, app.replace_btn)
    touchpad_layout.fill()

    right_side = Layout(cols=1, rows=2)
    right_side.add(1, 1, app.touchpad)
    right_side.add(2, 1, touchpad_layout)
    right_side.fill()

    app.root.add(1, 1, left_side)
    app.root.add(1, 2, right_side)
    app.root.fill()


def make_typing_buttons(app):
    app.typing_buttons = Layout(cols=3, rows=3)
    app.typing_btn_1 = Button(on_press=app.get_typing_btn_func(button_num=1))
    app.typing_btn_2 = Button(on_press=app.get_typing_btn_func(button_num=2))
    app.typing_btn_3 = Button(on_press=app.get_typing_btn_func(button_num=3))
    app.typing_btn_4 = Button(on_press=app.get_typing_btn_func(button_num=4))
    app.typing_btn_5 = Button(on_press=app.get_typing_btn_func(button_num=5))
    app.typing_btn_6 = Button(on_press=app.get_typing_btn_func(button_num=6))
    app.typing_btn_7 = Button(on_press=app.get_typing_btn_func(button_num=7))
    app.typing_btn_8 = Button(on_press=app.get_typing_btn_func(button_num=8))
    app.typing_btn_9 = Button(on_press=app.get_typing_btn_func(button_num=9))
    app.typing_buttons.add(1, 1, app.typing_btn_1)
    app.typing_buttons.add(1, 2, app.typing_btn_2)
    app.typing_buttons.add(1, 3, app.typing_btn_3)
    app.typing_buttons.add(2, 1, app.typing_btn_4)
    app.typing_buttons.add(2, 2, app.clear_btn)
    app.typing_buttons.add(2, 3, app.typing_btn_6)
    app.typing_buttons.add(3, 1, app.typing_btn_7)
    app.typing_buttons.add(3, 2, app.typing_btn_8)
    app.typing_buttons.add(3, 3, app.typing_btn_9)
    app.typing_buttons.fill()


def build_layout(app):
    make_buttons(app)
    make_typing_buttons(app)
    fill_layout(app)
