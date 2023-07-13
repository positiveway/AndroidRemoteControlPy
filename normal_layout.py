from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout

from code_map import *
from common_layout import UniversalButtonUI, AutoGridLayout, make_common_buttons
from typing_layout import DIRECTIONS


def make_buttons(app):
    app.shift_btn = UniversalButtonUI(
        "Shift", app,
        button_codes=Shift
    )
    app.caps_btn = UniversalButtonUI(
        "Caps", app,
        button_codes=Caps
    )
    app.up_btn = UniversalButtonUI(
        "Up", app,
        buttons="Up", on_press_only=False
    )
    app.down_btn = UniversalButtonUI(
        "Down", app,
        buttons="Down", on_press_only=False
    )
    app.left_btn = UniversalButtonUI(
        "Left", app,
        buttons="Left", on_press_only=False
    )
    app.right_btn = UniversalButtonUI(
        "Right", app,
        buttons="Right", on_press_only=False
    )

    app.left_click = UniversalButtonUI(
        "Left", app,
        button_codes=LeftMouse, on_press_only=False
    )
    app.right_click = UniversalButtonUI(
        "Right", app,
        button_codes=RightMouse
    )
    app.middle_click = UniversalButtonUI(
        "Middle", app,
        button_codes=MiddleMouse
    )

    app.scroll_btn = UniversalButtonUI(
        "Scroll", app,
        func=app.toggle_scroll,
    )
    app.double_click_btn = UniversalButtonUI(
        "X2", app,
        func=app.double_click
    )
    app.switch_btn = UniversalButtonUI(
        "Switch", app,
        button_codes=Switch_code
    )
    app.space_btn = UniversalButtonUI(
        "Space", app,
        button_codes=Space, on_press_only=False
    )
    app.bs_btn = UniversalButtonUI(
        "BS", app,
        buttons='BS', on_press_only=False
    )

    app.copy_btn = UniversalButtonUI(
        "Copy", app,
        buttons='Copy'
    )
    app.cut_btn = UniversalButtonUI(
        "Cut", app,
        buttons='Cut'
    )
    app.paste_btn = UniversalButtonUI(
        "Paste", app,
        buttons='Paste'
    )
    app.select_all_btn = UniversalButtonUI(
        "Select", app,
        buttons='Select'
    )
    app.format_btn = UniversalButtonUI(
        "Format", app,
        buttons='Format'
    )
    app.search_btn = UniversalButtonUI(
        "Search", app,
        buttons='Search'
    )
    app.replace_btn = UniversalButtonUI(
        "Replace", app,
        buttons='Replace'
    )
    app.undo_btn = UniversalButtonUI(
        "Undo", app,
        buttons='Undo'
    )
    app.redo_btn = UniversalButtonUI(
        "Redo", app,
        buttons='Redo'
    )

    app.esc_btn = UniversalButtonUI(
        "Esc", app,
        button_codes=Esc
    )


PANEL_WIDTH = 10


def resize_layout(app, max_window_size):
    app.l_buttons_panel.size_hint_max_x = PANEL_WIDTH
    app.r_buttons_panel.size_hint_max_x = PANEL_WIDTH
    actual_width = app.l_buttons_panel.width
    app.r_buttons_panel.pos = (max_window_size.x - actual_width, 0)

    app.touchpad.size_hint_max_x = max_window_size.x - actual_width * 2
    app.touchpad.pos = (actual_width, 0)

    app.background.size_hint_max_x = max_window_size.x - actual_width * 2
    app.background.pos = (actual_width, 0)

    app.root.do_layout()
    # app.root.canvas.ask_update()

def fill_layout(app):
    app.root = FloatLayout()
    # app.root.padding = 110

    app.background = Image(source="background.jpg", allow_stretch=True, keep_ratio=False)

    overlay_layout = FloatLayout()

    l_buttons_panel = BoxLayout(orientation='vertical')
    r_buttons_panel = BoxLayout(orientation='vertical')
    app.l_buttons_panel = l_buttons_panel
    app.r_buttons_panel = r_buttons_panel


    r_buttons_panel.add_widget(app.cut_btn)
    r_buttons_panel.add_widget(app.copy_btn)
    r_buttons_panel.add_widget(app.paste_btn)
    r_buttons_panel.add_widget(app.right_click)
    r_buttons_panel.add_widget(app.switch_btn)
    r_buttons_panel.add_widget(app.format_btn)
    r_buttons_panel.add_widget(app.enter_btn)
    r_buttons_panel.add_widget(app.space_btn)

    l_buttons_panel.add_widget(app.release_all_btn)

    l_buttons_panel.add_widget(app.up_btn)
    l_buttons_panel.add_widget(app.down_btn)
    l_buttons_panel.add_widget(app.left_btn)
    l_buttons_panel.add_widget(app.right_btn)

    l_buttons_panel.add_widget(app.bs_btn)
    l_buttons_panel.add_widget(app.undo_btn)

    overlay_layout.add_widget(l_buttons_panel)
    overlay_layout.add_widget(app.touchpad)
    overlay_layout.add_widget(r_buttons_panel)

    app.root.add_widget(app.background)
    app.root.add_widget(overlay_layout)


class LayeredLayout(GridLayout):
    def __init__(self, app):
        self.app = app
        super().__init__(cols=1, rows=1)

    def toggle(self):
        self.clear_widgets()

        if self.app.typing_mode:
            self.app.touchpad.disabled = True
            self.app.r_typing_buttons.disabled = False
            self.add_widget(self.app.r_buttons_layout)
        else:
            self.app.touchpad.disabled = False
            self.app.r_typing_buttons.disabled = True
            self.add_widget(self.app.touchpad)


def build_layout(app):
    make_common_buttons(app)
    make_buttons(app)
    fill_layout(app)
