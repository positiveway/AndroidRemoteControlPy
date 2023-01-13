code_map = {
    "Esc": 1,
    "1": 2,
    "2": 3,
    "3": 4,
    "4": 5,
    "5": 6,
    "6": 7,
    "7": 8,
    "8": 9,
    "9": 10,
    "0": 11,
    "Minus": 12,
    "=": 13,
    "Bs": 14,
    "Tab": 15,
    "Q": 16,
    "W": 17,
    "E": 18,
    "R": 19,
    "T": 20,
    "Y": 21,
    "U": 22,
    "I": 23,
    "O": 24,
    "P": 25,
    "[": 26,
    "]": 27,
    "Enter": 28,
    "Ctrl": 29,
    "A": 30,
    "S": 31,
    "D": 32,
    "F": 33,
    "G": 34,
    "H": 35,
    "J": 36,
    "K": 37,
    "L": 38,
    ";": 39,
    "'": 40,
    "Grave": 41,
    "Shift": 42,
    "\\": 43,
    "Z": 44,
    "X": 45,
    "C": 46,
    "V": 47,
    "B": 48,
    "N": 49,
    "M": 50,
    "Comma": 51,
    "Dot": 52,
    "/": 53,
    "Alt": 56,
    "Space": 57,
    "Caps": 58,
    "LeftMouse": 90,
    "RightMouse": 91,
    "MiddleMouse": 92,
    "Up": 103,
    "Left": 105,
    "Right": 106,
    "Down": 108,
    "Del": 111,
    "Mute": 113,
    "VolumeDown": 114,
    "VolumeUp": 115,
    "Scale": 120,
    "Win": 125,
}

reverse_code_map = {}
for key, val in code_map.items():
    reverse_code_map[val] = key
