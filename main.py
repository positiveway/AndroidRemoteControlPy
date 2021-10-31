from time import sleep
import pygame

from inputs import get_gamepad, UnpluggedError
import math

from collections import deque


class TriggerZone:
    Up = "Up"
    Middle = "Middle"
    Down = "Down"
    NoChange = "NoChange"


def load_layout():
    layout = {}
    with open("layout.csv", encoding="utf8") as layout_csv:
        content = layout_csv.readlines()

    content = content[1:]
    for line in content:
        line = line.strip()
        if line:
            letter, leftStick, rightStick = line.split(',')
            position = (leftStick, rightStick)
            if position in layout:
                raise ValueError()

            layout[position] = letter

    return layout


class InputsController:
    @staticmethod
    def read_events():
        events = get_gamepad()
        state = {}
        for event in events:
            if event.code == 'ABS_Y':
                state["LeftJoystickY"] = event.state
            elif event.code == 'ABS_X':
                state["LeftJoystickX"] = event.state
            elif event.code == 'ABS_RY':
                state["RightJoystickY"] = event.state
            elif event.code == 'ABS_RX':
                state["RightJoystickX"] = event.state
            elif event.code == 'ABS_Z':
                state["LeftTrigger"] = event.state
            elif event.code == 'ABS_RZ':
                state["RightTrigger"] = event.state
            elif event.code == 'BTN_TL':
                state["LeftBumper"] = event.state
            elif event.code == 'BTN_TR':
                state["RightBumper"] = event.state
            elif event.code == 'BTN_SOUTH':
                state["A"] = event.state
            elif event.code == 'BTN_NORTH':
                state["X"] = event.state
            elif event.code == 'BTN_WEST':
                state["Y"] = event.state
            elif event.code == 'BTN_EAST':
                state["B"] = event.state
            elif event.code == 'BTN_THUMBL':
                state["LeftThumb"] = event.state
            elif event.code == 'BTN_THUMBR':
                state["RightThumb"] = event.state
            elif event.code == 'BTN_SELECT':
                state["Back"] = event.state
            elif event.code == 'BTN_START':
                state["Start"] = event.state
            elif event.code == 'BTN_TRIGGER_HAPPY1':
                state["LeftDPad"] = event.state
            elif event.code == 'BTN_TRIGGER_HAPPY2':
                state["RightDPad"] = event.state
            elif event.code == 'BTN_TRIGGER_HAPPY3':
                state["UpDPad"] = event.state
            elif event.code == 'BTN_TRIGGER_HAPPY4':
                state["DownDPad"] = event.state
        return state


class XboxController:

    def __init__(self):
        self.layout = load_layout()

        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self.InTriggerZone = {
            "LeftJoystickX": TriggerZone.Middle,
            "LeftJoystickY": TriggerZone.Middle,
            "RightJoystickX": TriggerZone.Middle,
            "RightJoystickY": TriggerZone.Middle,
        }

        self.awaiting_full_neutral = False

        self.val_history = {
            "LeftJoystickX": self.init_val_history(),
            "LeftJoystickY": self.init_val_history(),
            "RightJoystickX": self.init_val_history(),
            "RightJoystickY": self.init_val_history(),
        }

    def init_val_history(self, stack_size=4):
        return deque(stack_size * [0], maxlen=stack_size)

    def get_stick_last_val(self, attr_name):
        return self.val_history[attr_name][-1]

    def get_stick_first_val(self, attr_name):
        return self.val_history[attr_name][0]

    def set_stick_val(self, attr_name, val):
        self.val_history[attr_name].append(val)

    def shift_stick_val(self, attr_name):
        self.set_stick_val(attr_name, self.get_stick_last_val(attr_name))

    def set_val_from_events(self, events):
        for attr_name in self.val_history.keys():
            self.shift_stick_val(attr_name)

        for attr_name, cur_val in events.items():
            self.set_stick_val(attr_name, cur_val)

        # print("Events")
        # print(events)
        # print("History")
        # print(self.val_history)
        # print('=' * 100)

    def motion_stopped(self):
        diff_detected = False
        for attr_name in self.val_history.keys():
            oldest_measure = self.get_stick_first_val(attr_name)
            newest_measure = self.get_stick_last_val(attr_name)

            if (diff_val := abs(newest_measure - oldest_measure)) > self.diff_threshold:
                diff_detected = True
                # print({attr_name: {"diff": diff_val, "cur": newest_measure, "old": oldest_measure}})

        return not diff_detected

    def convert_to_arrow(self, attr_name):
        x_zone, y_zone = self.InTriggerZone[attr_name + "X"], self.InTriggerZone[attr_name + "Y"]
        return {
            (TriggerZone.Middle, TriggerZone.Up): "🢁",
            (TriggerZone.Up, TriggerZone.Up): "🢅",
            (TriggerZone.Up, TriggerZone.Middle): "🢂",
            (TriggerZone.Up, TriggerZone.Down): "🢆",
            (TriggerZone.Middle, TriggerZone.Down): "🢃",
            (TriggerZone.Down, TriggerZone.Down): "🢇",
            (TriggerZone.Down, TriggerZone.Middle): "🢀",
            (TriggerZone.Down, TriggerZone.Up): "🢄",
            (TriggerZone.Middle, TriggerZone.Middle): self.FULL_NEUTRAL,
        }[(x_zone, y_zone)]

    def get_arrow_directions(self):
        return self.convert_to_arrow("LeftJoystick"), self.convert_to_arrow("RightJoystick")

    def detect_current_letter(self):
        left_stick_pos, right_stick_pos = self.get_arrow_directions()

        if left_stick_pos == self.FULL_NEUTRAL or right_stick_pos == self.FULL_NEUTRAL:
            # return "Only one stick is used"
            return None
        try:
            return self.layout[left_stick_pos, right_stick_pos]
        except KeyError:
            return "Not defined"

    FULL_NEUTRAL = '⬤'
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)
    TRIGGER_HIGH_DOWN_VAL = 14000
    diff_threshold = 800

    def detect_trigger_zone(self, value):
        if value > self.TRIGGER_HIGH_DOWN_VAL:
            return TriggerZone.Up
        elif value < -self.TRIGGER_HIGH_DOWN_VAL:
            return TriggerZone.Down
        else:
            return TriggerZone.Middle

    def zone_changed(self, attr_name, value):
        new_zone = self.detect_trigger_zone(value)
        return self.InTriggerZone[attr_name] != new_zone

    def returned_to_neutral(self, zone):
        return zone == TriggerZone.Middle

    def check_full_neutral(self):
        if self.awaiting_full_neutral:
            if self.convert_to_arrow("LeftJoystick") == self.FULL_NEUTRAL or \
                    self.convert_to_arrow("RightJoystick") == self.FULL_NEUTRAL:
                self.awaiting_full_neutral = False

    def update_state(self, read_events_func):
        events = read_events_func()
        if events:
            self.set_val_from_events(events)
            return None

        motion_stopped = self.motion_stopped()

        zone_not_neutral = False
        changed_zones = {}

        for attr_name in self.val_history.keys():
            last_val = self.get_stick_last_val(attr_name)
            cur_zone = self.detect_trigger_zone(last_val)
            if self.zone_changed(attr_name, last_val):
                if motion_stopped:
                    changed_zones[attr_name] = cur_zone
                    self.InTriggerZone[attr_name] = cur_zone
                    if not self.returned_to_neutral(cur_zone):
                        zone_not_neutral = True

        self.check_full_neutral()

        if changed_zones:
            print(self.get_arrow_directions())

        if not self.awaiting_full_neutral and zone_not_neutral:
            self.awaiting_full_neutral = True
            return self.detect_current_letter()
        return None


def inputs_main():
    controller = XboxController()
    while True:
        try:
            letter = controller.update_state(InputsController.read_events)
        except UnpluggedError as error:
            print(error)
            sleep(0.5)
        else:
            if letter:
                print(letter)


class BACKEND_TYPE:
    Pygame = "Pygame"
    Inputs = "Inputs"


def pygame_read_events():
    proper_events = {}
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            value = int(XboxController.MAX_JOY_VAL * event.value)
            axis = event.axis
            try:
                attr_name = {
                    0: "LeftJoystickX",
                    1: "LeftJoystickY",
                    3: "RightJoystickX",
                    4: "RightJoystickY",
                }[axis]
            except KeyError as error:
                print(error)
                continue

            if attr_name.endswith("Y"):
                value *= -1

            proper_events[attr_name] = value
            # print(attr_name, value)

    return proper_events


def pygame_main():
    pygame.init()
    joysticks = []
    clock = pygame.time.Clock()
    keepPlaying = True

    controller = XboxController()

    # for al the connected joysticks
    for i in range(0, pygame.joystick.get_count()):
        # create an Joystick object in our list
        joysticks.append(pygame.joystick.Joystick(i))
        # initialize them all (-1 means loop forever)
        joysticks[-1].init()
        # print a statement telling what the name of the controller is
        print("Detected joystick "), joysticks[-1].get_name(), "'"
    while keepPlaying:
        clock.tick(60)
        letter = controller.update_state(pygame_read_events)
        if letter:
            print(letter)


if __name__ == '__main__':
    pygame_main()
