import uvicorn
from pydantic import BaseModel

from fastapi import FastAPI, Response
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from controller import controller

middleware = Middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'],
                        allow_headers=['*'])

app = FastAPI(middleware=[middleware])


class SticksParams(BaseModel):
    left_magnitude: float
    right_magnitude: float
    left_angle: int
    right_angle: int


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


@app.post("/send_letter")
def send_letter(letter: str):
    print(letter)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
