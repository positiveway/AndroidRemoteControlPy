import json

from common import *
from code_map import code_map, reverse_code_map, EmptyLetterCode

langs = ['en', 'ru']

arrows_to_btn_num = {
    "🢄": 1, "🢁": 2, "🢅": 3,
    "🢀": 4, "⬤": 5, "🢂": 6,
    "🢇": 7, "🢃": 8, "🢆": 9,
}

DIRECTIONS = tuple(range(9))

CELL_ROWS = 3
BLOCK_ROWS = 9

CELL_ELEMENTS = 3
BLOCK_ELEMENTS = 9


def _extract_raw_cell_or_block(start_line, rows_amount, input_layout):
    start_line += 1
    return input_layout[start_line:start_line + rows_amount]


def _split_block_or_cell(raw_source, elements_amount, is_reverse):
    split_source = []
    for dir1, line in enumerate(raw_source):
        line = line.split()

        if len(line) != elements_amount:
            raise ValueError(len(line))

        if is_reverse:  # for right_first layout. no longer needed. left for potential future use
            line = reverse(line)

        converted = []
        for dir2, letter in enumerate(line):
            if letter not in code_map:
                letter = letter.lower().capitalize()
                if letter not in code_map:
                    raise ValueError(f'Wrong spelling at position [{dir1 + 1}, {dir2 + 1}]: {letter}')

            code = code_map[letter]
            converted.append(code)
        split_source.append(converted)

    return split_source


def extract_split_block_or_cell(start_line, rows_amount, elements_amount, process_split_func, input_layout, is_reverse):
    raw_source = _extract_raw_cell_or_block(start_line, rows_amount, input_layout)
    split_source = _split_block_or_cell(raw_source, elements_amount, is_reverse)
    return process_split_func(split_source)


def process_split_cell(split_cell):
    cell = []
    for row in range(0, 3):
        for col in range(0, 3):
            cell.append(split_cell[row][col])

    return cell


def process_split_block(split_block):
    block = []
    for row in range(0, 9, 3):
        for col in range(0, 9, 3):
            cell = []
            for i in range(row, row + 3):
                for j in range(col, col + 3):
                    cell.append(split_block[i][j])
            block.append(cell)

    return block


def process_cell(start_line, input_layout):
    return extract_split_block_or_cell(start_line, CELL_ROWS, CELL_ELEMENTS, process_split_cell, input_layout,
                                       is_reverse=False)


def process_block(start_line, input_layout, is_reverse=False):
    return extract_split_block_or_cell(start_line, BLOCK_ROWS, BLOCK_ELEMENTS, process_split_block, input_layout,
                                       is_reverse)


def load_layout():
    with open("layout.txt", encoding='utf8') as file:
        raw_input_layout = file.readlines()

    input_layout = []
    for line in raw_input_layout:
        line = line.replace('||', '')
        line = ' '.join(line.split())

        if line and not line.startswith('='):
            input_layout.append(line)

    for ind, line in enumerate(input_layout):
        if line == 'mouse_mode':
            mouse_mode_layout = process_cell(ind, input_layout)

        elif line == 'EN':
            en_layout = process_block(ind, input_layout)

        elif line == 'RU':
            ru_layout = process_block(ind, input_layout)

    multi_lang_layout = {
        'en': en_layout,
        'ru': ru_layout,
    }

    return mouse_mode_layout, multi_lang_layout


def convert_to_hint(code):
    if code == EmptyLetterCode:
        return ''
    else:
        return reverse_code_map[code]


def generate_mouse_hints(layout):
    hints = ['' for _ in DIRECTIONS]

    for dir1 in DIRECTIONS:
        hints[dir1] = convert_to_hint(layout[dir1])

    return hints


def generate_hints(layout):
    detailed_hints = {}
    preview_hints = {}

    for lang in langs:
        detailed_hints[lang] = [['' for _ in DIRECTIONS] for _ in DIRECTIONS]
        preview_hints[lang] = ['' for _ in DIRECTIONS]

        for dir1 in DIRECTIONS:
            for dir2 in DIRECTIONS:
                code = layout[lang][dir1][dir2]

                detailed_hints[lang][dir1][dir2] = convert_to_hint(code)

            dirs2 = detailed_hints[lang][dir1]
            dirs2 = [d for d in dirs2 if d]
            row_len = 2
            row1 = ' '.join(dirs2[:row_len])
            row2 = ' '.join(dirs2[row_len:row_len * 2])
            row3 = ' '.join(dirs2[row_len * 2:row_len * 3])
            row4 = ' '.join(dirs2[row_len * 3:])
            representation = '\n'.join((row1, row2, row3, row4))

            preview_hints[lang][dir1] = representation

    return detailed_hints, preview_hints


def load_configs():
    with open("configs.json", encoding="utf8") as file:
        return json.load(file)
