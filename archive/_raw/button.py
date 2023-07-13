from common import *
from code_map import *

class _State(LockedMap):
    def release(self, button):
        state = self.map[button]
        if state != 0:
            self.put(button, 0)
            return True
        else:
            return False

    def is_pressed(self, button):
        return self.map[button]


class BtnState(_State):
    def __init__(self) -> None:
        super().__init__()

        for button in code_map.values():
            if not is_iterable(button) and button > 0:
                self.put(button, 0)

        self.lock()

    def press(self, button):
        state = self.map[button]
        if state != 1:
            self.put(button, 1)
            return True
        else:
            return False

    def all_pressed(self):
        return [button for button, value in self.map.items() if value != 0]


class ModifiersState(_State):
    def __init__(self) -> None:
        super().__init__()

        for code in [Shift, Ctrl, Alt]:
            self.put(code, 0)

        self.lock()

    def get_set_state(self, modifier):
        def actual_func(new_state):
            if not (0 <= new_state <= 2):
                raise ValueError(f'Incorrect state: {new_state}')

            if self.map[modifier] != new_state:
                self.put(modifier, new_state)
                return True
            else:
                return False

        return actual_func

    def all_pressed_except_caps(self):
        return [button for button, value in self.map.items() if value == 1]


class Button:
    btn_state = BtnState()
    mod_state = ModifiersState

    def __init__(self, keys) -> None:
        if not is_iterable(keys):
            keys = [keys]

        self.keys = keys

        self.codes = []
        for key in keys:
            self.codes.append(code_map[key])

        self.reverse_codes = reverse(self.codes)

    def __eq__(self, o: 'Button') -> bool:
        for ind, key1 in enumerate(self.keys):
            if key1 != o.keys[ind]:
                return False

        return True

    def send_type(self, buttons):
        send_pressed = self.get_send_pressed(buttons)
        send_released = self.get_send_released(buttons)

        def actual_func():
            send_pressed()
            send_released()

        return actual_func()

    def convert_buttons(self, buttons):
        if not is_iterable(buttons):
            buttons = [buttons]

        for idx, button in buttons:
            buttons[idx] = code_map[button]

        return buttons

    def inline_funcs(self, buttons, func, is_reverse):
        buttons = self.convert_buttons(buttons)

        if is_reverse:
            buttons = reverse(buttons)

        length = len(buttons)

        if length == 1:
            def actual_func():
                func(buttons[0])
        elif length == 2:
            def actual_func():
                func(buttons[0])
                func(buttons[1])
        elif length == 3:
            def actual_func():
                func(buttons[0])
                func(buttons[1])
                func(buttons[2])
        elif length == 4:
            def actual_func():
                func(buttons[0])
                func(buttons[1])
                func(buttons[2])
                func(buttons[3])
        else:
            raise ValueError(length)

        return actual_func

    def get_send_pressed(self, buttons):
        return self.inline_funcs(buttons, self._send_pressed_single, False)

    def get_send_released(self, buttons):
        return self.inline_funcs(buttons, self._send_released_single, True)

    def get_send_pressed_single(self, button):
        if button == self.Caps:
            modifier = self.Shift
        else:
            modifier = button

        if modifier in self.modifiers.all:
            press_modifier = self.get_press_modifier(modifier)
            release_modifier = self.get_release_modifier(modifier)

            def actual_func():
                cur_state = self.modifiers.map[modifier]
                if cur_state == 0:
                    if button == self.Caps:
                        press_modifier(2)
                    else:
                        press_modifier(1)

                elif cur_state == 1:
                    if button == self.Caps:
                        release_modifier()
                    else:
                        release_modifier()

                elif cur_state == 2:
                    if button == self.Caps:
                        release_modifier()
                else:
                    raise ValueError(f'incorrect state: {self.modifiers.cur_state}')

            return actual_func

        send_pressed_raw = self.get_send_pressed_raw(button)

        if button == self.Esc:
            def actual_func():
                self.release_mouse_and_pressed()

                if self.btn_states.press(button):
                    send_pressed_raw()

            return actual_func

        if button in self.mouse_buttons:
            def actual_func():
                if not self.is_mouse_mode:
                    return

                if self.btn_states.press(button):
                    send_pressed_raw()

            return actual_func

        def actual_func():
            if self.btn_states.press(button):
                send_pressed_raw()

        return actual_func

    def get_send_released_single(self, button):
        if button == self.Caps:
            modifier = self.Shift
        else:
            modifier = button

        if modifier in self.modifiers.all:
            def actual_func():
                pass

            return actual_func

        send_released_raw = self.get_send_released_raw(button)

        def actual_func():
            if self.btn_states.release(button):
                send_released_raw()
                self.release_all_modifiers()

        return actual_func

    def release_all_modifiers(self):
        for modifier in self.modifiers.all_pressed_except_caps():
            self.get_send_released_raw(modifier)()
            self.modifiers.release(modifier)

    def force_release_modifiers(self):
        for modifier in self.modifiers.all:
            self.get_send_released_raw(modifier)()
            self.modifiers.release(modifier)

    def get_press_modifier(self, modifier):
        send_pressed_raw = self.get_send_pressed_raw(modifier)
        set_state = self.modifiers.get_set_state(modifier)

        def actual_func(state):
            send_pressed_raw()
            set_state(state)

        return actual_func

    def get_release_modifier(self, modifier):
        send_released_raw = self.get_send_released_raw(modifier)

        def actual_func():
            send_released_raw()
            self.modifiers.release(modifier)

        return actual_func

    def get_send_pressed_raw(self, button):
        def actual_func():
            self.msg[0] = button + 128
            self.sock.send(self.msg)

        return actual_func

    def get_send_released_raw(self, button):
        def actual_func():
            self.msg[0] = button
            self.sock.send(self.msg)

        return actual_func

    def force_release(self, button):
        self._send_released_raw(button)()
        self.btn_states.release(button)
