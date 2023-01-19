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
    "-": 12,
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
    "`": 41,
    "Shift": 42,
    "\\": 43,
    "Z": 44,
    "X": 45,
    "C": 46,
    "V": 47,
    "B": 48,
    "N": 49,
    "M": 50,
    ",": 51,
    ".": 52,
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

Ctrl = code_map['Ctrl']
Alt = code_map['Alt']
Shift = code_map['Shift']
Caps = code_map['Caps']
Enter = code_map['Enter']
Esc = code_map['Esc']
Backspace = code_map['Bs']
Space = code_map['Space']

LeftMouse = code_map['LeftMouse']
RightMouse = code_map['RightMouse']
MiddleMouse = code_map['MiddleMouse']


def append_commands():
    command_map = {
        'Select': (Ctrl, code_map['A']),
        'Undo': (Ctrl, code_map['Z']),
        'Redo': (Ctrl, Shift, code_map['Z']),
        'Copy': (Ctrl, code_map['C']),
        'Cut': (Ctrl, code_map['X']),
        'Paste': (Ctrl, code_map['V']),
        'Format': (Ctrl, Alt, code_map['L']),
        'Search': (Ctrl, code_map['F']),
        'Replace': (Ctrl, code_map['R']),
    }
    for key, val in command_map.items():
        code_map[key] = val


append_commands()

reverse_code_map = {val: key for key, val in code_map.items()}
