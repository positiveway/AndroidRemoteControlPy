from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from code_map import reverse_code_map, code_map


def make_buttons(app):
    app.shift_btn = Button(text="Shift", font_size=app.font_size)
    app.caps_btn = Button(text="Caps", font_size=app.font_size)

    app.clear_btn = Button(text="Bs", font_size=app.font_size, on_press=app.clear)
    app.enter_btn = Button(text="Enter", font_size=app.font_size,
                           on_press=app.get_send_type_func(code_map["Enter"]))

    app.copy_btn = Button(text="Copy", font_size=app.font_size,
                          on_press=app.get_send_seq_func([app.Ctrl, code_map["C"]]))
    app.cut_btn = Button(text="Cut", font_size=app.font_size,
                         on_press=app.get_send_seq_func([app.Ctrl, code_map["X"]]))
    app.paste_btn = Button(text="Paste", font_size=app.font_size,
                           on_press=app.get_send_seq_func([app.Ctrl, code_map["V"]]))

    app.undo_btn = Button(text="Undo", font_size=app.font_size,
                          on_press=app.get_send_seq_func([app.Ctrl, code_map["Z"]]))
    app.redo_btn = Button(text="Redo", font_size=app.font_size,
                          on_press=app.get_send_seq_func([app.Ctrl, app.Shift, code_map["Z"]]))

    app.up_btn = Button(text="Up", font_size=app.font_size,
                        on_press=app.get_send_type_func(code_map["Up"]))
    app.down_btn = Button(text="Down", font_size=app.font_size,
                          on_press=app.get_send_type_func(code_map["Down"]))
    app.left_btn = Button(text="Left", font_size=app.font_size,
                          on_press=app.get_send_type_func(code_map["Left"]))
    app.right_btn = Button(text="Right", font_size=app.font_size,
                           on_press=app.get_send_type_func(code_map["Right"]))

    app.release_all_btn = Button(
        text="Release all", font_size=app.font_size,
        on_press=app.release_all
    )

    app.scroll_btn = Button(
        text="Scroll", font_size=app.font_size,
        on_press=app.toggle_scroll,
    )
    app.left_click = Button(
        text="Left", font_size=app.font_size,
        on_press=app.get_pressed_func(app.controller.LeftMouse),
        on_release=app.get_released_func(app.controller.LeftMouse)
    )
    app.right_click = Button(
        text="Right", font_size=app.font_size,
        on_press=app.get_pressed_func(app.controller.RightMouse),
        on_release=app.get_released_func(app.controller.RightMouse)
    )
    app.middle_click = Button(
        text="Middle", font_size=app.font_size,
        on_press=app.get_pressed_func(app.controller.MiddleMouse),
        on_release=app.get_released_func(app.controller.MiddleMouse)
    )


def fill_layout(app):
    app.root = GridLayout(cols=2, rows=1)
    # app.root = BoxLayout()
    # app.root.padding = 110

    app.label = Label(font_size=app.font_size)
    # app.label.size_hint_x = 0.25
    # app.label.size_hint_y = 0.9

    typing_extra_buttons = GridLayout(cols=3, rows=2)
    typing_extra_buttons.add_widget(app.caps_btn)
    typing_extra_buttons.add_widget(app.enter_btn)
    typing_extra_buttons.add_widget(app.shift_btn)

    typing_extra_buttons.add_widget(app.copy_btn)
    typing_extra_buttons.add_widget(app.cut_btn)
    typing_extra_buttons.add_widget(app.paste_btn)

    typing_layout = GridLayout(cols=1, rows=2)
    typing_row_1 = GridLayout(cols=2, rows=1)
    typing_row_1.add_widget(app.typing_buttons)
    typing_row_1.add_widget(Label())
    typing_layout.add_widget(typing_row_1)
    typing_layout.add_widget(typing_extra_buttons)

    release_all_layout = GridLayout(cols=2, rows=2)
    release_all_layout.add_widget(Label())
    release_all_layout.add_widget(Label())
    release_all_layout.add_widget(app.release_all_btn)
    release_all_layout.add_widget(Label())

    label_row_2 = GridLayout(cols=2, rows=1)
    label_row_2.add_widget(release_all_layout)
    label_row_2.add_widget(app.label)

    extra_buttons_2 = GridLayout(cols=2, rows=1)
    extra_buttons_2_left = GridLayout(cols=3, rows=2)
    extra_buttons_2_right = GridLayout(cols=3, rows=2)

    extra_buttons_2_left.add_widget(Label())
    extra_buttons_2_left.add_widget(app.up_btn)
    extra_buttons_2_left.add_widget(Label())
    extra_buttons_2_left.add_widget(app.left_btn)
    extra_buttons_2_left.add_widget(app.down_btn)
    extra_buttons_2_left.add_widget(app.right_btn)

    extra_buttons_2_right.add_widget(Label())
    extra_buttons_2_right.add_widget(Label())
    extra_buttons_2_right.add_widget(Label())
    extra_buttons_2_right.add_widget(Label())
    extra_buttons_2_right.add_widget(app.undo_btn)
    extra_buttons_2_right.add_widget(app.redo_btn)

    extra_buttons_2.add_widget(extra_buttons_2_left)
    extra_buttons_2.add_widget(extra_buttons_2_right)

    label_layout = GridLayout(cols=1, rows=2)
    label_layout.add_widget(extra_buttons_2)
    label_layout.add_widget(label_row_2)

    left_side = GridLayout(cols=1, rows=2)
    left_side.add_widget(typing_layout)
    left_side.add_widget(label_layout)

    touchpad_layout = GridLayout(cols=2, rows=2)
    touchpad_layout.add_widget(app.middle_click)
    touchpad_layout.add_widget(app.right_click)

    touchpad_layout.add_widget(app.scroll_btn)
    touchpad_layout.add_widget(app.left_click)

    right_side = GridLayout(cols=1, rows=2)
    right_side.add_widget(app.touchpad)
    right_side.add_widget(touchpad_layout)

    app.root.add_widget(left_side)
    app.root.add_widget(right_side)


def make_typing_buttons(app):
    app.typing_buttons = GridLayout(cols=3, rows=3)
    app.typing_btn_1 = Button(on_press=app.get_typing_btn_func(button_num=1))
    app.typing_btn_2 = Button(on_press=app.get_typing_btn_func(button_num=2))
    app.typing_btn_3 = Button(on_press=app.get_typing_btn_func(button_num=3))
    app.typing_btn_4 = Button(on_press=app.get_typing_btn_func(button_num=4))
    app.typing_btn_5 = Button(on_press=app.get_typing_btn_func(button_num=5))
    app.typing_btn_6 = Button(on_press=app.get_typing_btn_func(button_num=6))
    app.typing_btn_7 = Button(on_press=app.get_typing_btn_func(button_num=7))
    app.typing_btn_8 = Button(on_press=app.get_typing_btn_func(button_num=8))
    app.typing_btn_9 = Button(on_press=app.get_typing_btn_func(button_num=9))
    app.typing_buttons.add_widget(app.typing_btn_1)
    app.typing_buttons.add_widget(app.typing_btn_2)
    app.typing_buttons.add_widget(app.typing_btn_3)
    app.typing_buttons.add_widget(app.typing_btn_4)
    app.typing_buttons.add_widget(app.clear_btn)
    app.typing_buttons.add_widget(app.typing_btn_6)
    app.typing_buttons.add_widget(app.typing_btn_7)
    app.typing_buttons.add_widget(app.typing_btn_8)
    app.typing_buttons.add_widget(app.typing_btn_9)


def build_layout(app):
    make_buttons(app)
    make_typing_buttons(app)
    fill_layout(app)
