from enum import Enum

import pygame


class ReversedEnum(Enum):
    @classmethod
    def get_reversed_map(cls):
        filter_func = lambda attr: not attr.startswith('__')
        attr_list = list(filter(filter_func, dir(cls)))
        return {getattr(cls, attr): attr for attr in attr_list}


class ButtonsMap(ReversedEnum):
    Cross = 0
    Circle = 1
    Square = 2
    Triangle = 3
    Share = 4
    PS = 5
    Options = 6
    L_StickIn = 7
    R_StickIn = 8
    LeftBumper = 9
    RightBumper = 10
    D_pad_Up = 11
    D_pad_Down = 12
    D_pad_Left = 13
    D_pad_Right = 14
    TouchPadClick = 15


class Axis(ReversedEnum):
    LeftStickHorizon = 0
    LeftStickVert = 1
    RightStickHorizon = 2
    RightStickVert = 3
    LeftTrigger = 4
    RightTrigger = 5


buttons_reversed_map = ButtonsMap.get_reversed_map()
axis_reversed_map = Axis.get_reversed_map()
print(buttons_reversed_map)
print(axis_reversed_map)

pygame.init()
clock = pygame.time.Clock()


class Dualshock:
    CLOCK_TICK = 60

    def __init__(self) -> None:
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        try:
            while self.is_running:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.JOYAXISMOTION:
                        print(event.dict, event.joy, event.axis, event.value)
                    elif event.type == pygame.JOYBALLMOTION:
                        print(event.dict, event.joy, event.ball, event.rel)
                    elif event.type == pygame.JOYBUTTONDOWN:
                        print(event.dict, event.joy, event.button, 'pressed')
                    elif event.type == pygame.JOYBUTTONUP:
                        print(event.dict, event.joy, event.button, 'released')
                    elif event.type == pygame.JOYHATMOTION:
                        print(event.dict, event.joy, event.hat, event.value)

                clock.tick(self.CLOCK_TICK)

        except KeyboardInterrupt:
            self.stop()
            print("EXITING NOW")
            self.joystick.quit()


if __name__ == '__main__':
    dualshock = Dualshock()
    dualshock.run()
