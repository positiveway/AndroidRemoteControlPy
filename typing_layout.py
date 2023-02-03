import json

from code_map import code_map, reverse_code_map

langs = ['en', 'ru']

arrows_to_btn_num = {
    "🢄": 1, "🢁": 2, "🢅": 3,
    "🢀": 4, "⬤": 5, "🢂": 6,
    "🢇": 7, "🢃": 8, "🢆": 9,
}

arrow_directions = arrows_to_btn_num.keys()
num_directions = arrows_to_btn_num.values()

DIRECTIONS = tuple(range(1, 10))

CELL_ROWS = 3
BLOCK_ROWS = CELL_ROWS * 3 + 2

CELL_ELEMENTS = 3
BLOCK_ELEMENTS = 9


def _extract_raw_cell_or_block(start_line, rows_amount, input_layout):
    start_line += 1
    return input_layout[start_line:start_line + rows_amount]


def _split_block_or_cell(raw_source, elements_amount):
    split_source = []
    for line in raw_source:
        if not line.startswith('='):
            line = line.split()
            if len(line) != elements_amount:
                raise ValueError(len(line))
            for ind, letter in enumerate(line):
                if letter.lower() == 'EmptyW'.lower():
                    line[ind] = ''

            split_source.append(line)

    return split_source


def extract_split_block_or_cell(start_line, rows_amount, elements_amount, process_split_func, input_layout):
    raw_source = _extract_raw_cell_or_block(start_line, rows_amount, input_layout)
    split_source = _split_block_or_cell(raw_source, elements_amount)
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
    return extract_split_block_or_cell(start_line, CELL_ROWS, CELL_ELEMENTS, process_split_cell, input_layout)


def process_block(start_line, input_layout):
    return extract_split_block_or_cell(start_line, BLOCK_ROWS, BLOCK_ELEMENTS, process_split_block, input_layout)


def convert_layout(layout):
    converted = {}
    for dir1 in DIRECTIONS:
        converted[dir1] = {}
        for dir2 in DIRECTIONS:
            try:
                letter = layout[dir1 - 1][dir2 - 1]
            except KeyError:
                continue
            else:
                if letter:
                    converted[dir1][dir2] = code_map[letter]

    return converted


def load_layout():
    with open("layout.txt", encoding='utf8') as file:
        input_layout = file.readlines()

    input_layout = [line.replace('||', '') for line in input_layout]

    mouse_mode = process_cell(1, input_layout)

    en_left_first = process_block(9, input_layout)
    en_right_first = process_block(24, input_layout)

    ru_left_first = process_block(41, input_layout)
    ru_right_first = process_block(56, input_layout)

    lang_layout = {
        'en': convert_layout(en_left_first),
        'ru': convert_layout(ru_left_first),
    }

    return lang_layout


def generate_hints(layout):
    detailed_hints = {}
    preview_hints = {}

    for lang in langs:
        detailed_hints[lang] = {}
        preview_hints[lang] = {}

        for dir1 in DIRECTIONS:
            detailed_hints[lang][dir1] = {}
            preview_hints[lang][dir1] = ''

            for dir2 in DIRECTIONS:
                try:
                    letter = layout[lang][dir1][dir2]
                except KeyError:
                    letter = ""
                else:
                    letter = reverse_code_map[letter]

                detailed_hints[lang][dir1][dir2] = letter

            dirs2 = detailed_hints[lang][dir1].values()
            dirs2 = [d for d in dirs2 if d]
            row_len = 2
            row1 = ' '.join(dirs2[:row_len])
            row2 = ' '.join(dirs2[row_len:row_len * 2])
            row3 = ' '.join(dirs2[row_len * 2:row_len * 3])
            row4 = ' '.join(dirs2[row_len * 3:])
            preview_hints[lang][dir1] = '\n'.join((row1, row2, row3, row4))

    return detailed_hints, preview_hints


def load_configs():
    with open("configs.json", encoding="utf8") as file:
        return json.load(file)
