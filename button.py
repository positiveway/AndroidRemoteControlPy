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

        self.current = 0

        for code in [Shift, Ctrl, Alt]:
            self.put(code, 0)

        self.lock()

    def set_state(self, new_state):
        if not (0 <= new_state <= 2):
            raise ValueError(f'Incorrect state: {new_state}')

        if self.cur_state != new_state:
            self.put(self.current, new_state)
            return True
        else:
            return False

    @property
    def cur_state(self):
        return self.map[self.current]

    def all_pressed_except_caps(self):
        return [button for button, value in self.map.items() if value == 1]


class Button:
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
