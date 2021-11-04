from functools import partial

import uvicorn
from kivy.app import App
from pydantic import BaseModel

from garden_joystick import Joystick
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from fastapi import FastAPI, Response
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

middleware = Middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'],
                        allow_headers=['*'])

app = FastAPI(middleware=[middleware])


# app = FastAPI()


class SticksParams(BaseModel):
    left_magnitude: float
    right_magnitude: float
    left_angle: int
    right_angle: int


@app.get("/")
def root():
    return {"hello world": ""}


@app.post("/get_letter/")
async def get_letter(stick_params: SticksParams):
    letter1 = controller.update_zone(stick_params.left_magnitude, stick_params.left_angle, "Left")
    letter2 = controller.update_zone(stick_params.right_magnitude, stick_params.right_angle, "Right")

    if letter1:
        letter = letter1
    else:
        letter = letter2

    if letter:
        print('=' * 40)
        print(letter)
        print('=' * 40)

    return letter


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


class Controller:
    def detect_zone(self, magnitude, angle):
        angle = int(angle)
        if magnitude > self.magnitude_threshold:
            return self.boundary_mapping.get(angle, self.EDGE_ZONE)
        else:
            return self.NEUTRAL_ZONE

    def _gen_range(self, lower_bound, upper_bound, boundary_mapping, arrow):
        for cur_angle in range(lower_bound, upper_bound):
            boundary_mapping[cur_angle] = arrow

    def gen_boundary_mapping(self):
        mapping = {
            0: "🢂",
            45: "🢅",
            90: "🢁",
            135: "🢄",
            180: "🢀",
            225: "🢇",
            270: "🢃",
            315: "🢆",
        }
        boundary_mapping = {}

        for map_angle, arrow in mapping.items():
            gen_range = partial(self._gen_range, boundary_mapping=boundary_mapping, arrow=arrow)

            upper_bound = map_angle + self.angle_margin
            gen_range(map_angle, upper_bound)
            if map_angle == 0:
                lower_bound = 360 - self.angle_margin
                gen_range(lower_bound, 360)
            else:
                lower_bound = map_angle - self.angle_margin
                gen_range(lower_bound, map_angle)

        return boundary_mapping

    def detect_letter(self):
        cur_zones = (self.LeftStickZone, self.RightStickZone)
        for zone in cur_zones:
            if zone == self.NEUTRAL_ZONE:
                return None
            elif zone == self.EDGE_ZONE:
                raise ValueError()

        self.awaiting_neutral_pos = True
        try:
            return self.layout[cur_zones]
        except KeyError as error:
            print(error)
            return 'Undefined'

    def get_zone(self, attr_prefix):
        attr_name = attr_prefix + "StickZone"
        zone = getattr(self, attr_name)
        return {
            "🢂": 1,
            "🢅": 2,
            "🢁": 3,
            "🢄": 4,
            "🢀": 5,
            "🢇": 6,
            "🢃": 7,
            "🢆": 8,
            "⬤": -1,
            "❌": -2,
        }[zone]

    def update_zone(self, magnitude, angle, attr_prefix):
        letter = self._update_zone(magnitude, angle, attr_prefix)
        if letter is None:
            letter = ""
        return letter

    def _update_zone(self, magnitude, angle, attr_prefix):
        angle = int(angle)
        attr_name = attr_prefix + "StickZone"
        prev_zone = getattr(self, attr_name)
        new_zone = self.detect_zone(magnitude, angle)
        if new_zone == self.EDGE_ZONE:
            return None

        if new_zone != prev_zone:
            setattr(self, attr_name, new_zone)
            if self.awaiting_neutral_pos:
                if new_zone == self.NEUTRAL_ZONE:
                    self.awaiting_neutral_pos = False
            else:
                return self.detect_letter()

        return None

    NEUTRAL_ZONE = '⬤'
    EDGE_ZONE = '❌'
    angle_margin = 15
    magnitude_threshold_pct = 75
    magnitude_threshold = magnitude_threshold_pct / 100

    def __init__(self) -> None:
        self.layout = load_layout()
        self.boundary_mapping = self.gen_boundary_mapping()

        self.LeftStickZone = self.NEUTRAL_ZONE
        self.RightStickZone = self.NEUTRAL_ZONE

        self.awaiting_neutral_pos = False


controller = Controller()


class DemoApp(App):
    def build(self):
        self.root = BoxLayout()
        self.root.padding = 50

        left_joystick = Joystick()
        left_joystick.bind(pad=self.update_left)
        self.root.add_widget(left_joystick)
        self.left_label = Label()
        self.root.add_widget(self.left_label)

        right_joystick = Joystick()
        right_joystick.bind(pad=self.update_right)
        self.root.add_widget(right_joystick)
        self.right_label = Label()
        self.root.add_widget(self.right_label)

    def update_coordinates(self, joystick, pad, attr_prefix):
        x = str(pad[0])[0:5]
        y = str(pad[1])[0:5]
        radians = str(joystick.radians)[0:5]
        magnitude = str(joystick.magnitude)[0:5]
        angle = str(joystick.angle)[0:5]

        letter = controller.update_zone(joystick.magnitude, joystick.angle, attr_prefix)
        if letter:
            print(letter)

            letter = ord(letter[0])

        text = "Zone: {}\nletter: {}\nx: {}\ny: {}\nradians: {}\nmagnitude: {}\nangle: {}"

        return text.format(controller.get_zone(attr_prefix), letter, x, y, radians, magnitude, angle)

    def update_left(self, joystick, pad):
        self.left_label.text = self.update_coordinates(joystick, pad, "Left")

    def update_right(self, joystick, pad):
        self.right_label.text = self.update_coordinates(joystick, pad, "Right")


if __name__ == '__main__':
    # DemoApp().run()
    uvicorn.run(app, host="0.0.0.0", port=8000)
