import json


def load_layout():
    arrows_to_btn_num = {
        "🢄": 1, "🢁": 2, "🢅": 3,
        "🢀": 4, "⬤": 5, "🢂": 6,
        "🢇": 7, "🢃": 8, "🢆": 9,
    }

    layout = {}
    with open("layout.csv", encoding="utf8") as layout_csv:
        content = layout_csv.readlines()

    content = content[2:]
    for line in content:
        line = line.replace(' ', '').replace('\n', '').lower()
        if line and not line.startswith(';'):
            typing_positions, letters = line.split('=>')
            typing_positions = typing_positions.split('&')
            typing_positions = (
                arrows_to_btn_num[typing_positions[0]],
                arrows_to_btn_num[typing_positions[1]]
            )

            letters = letters.replace('none', '')
            letters = letters.split('|')
            letters = [letter.capitalize() for letter in letters]

            if typing_positions in layout:
                raise ValueError(f"Repeated: {letters}")

            layout[typing_positions] = {}
            if letters[0]:
                layout[typing_positions]['en'] = letters[0]
            if letters[1]:
                layout[typing_positions]['ru'] = letters[1]

    return layout


def generate_hints(layout):
    langs = ['en', 'ru']
    directions = tuple(range(1, 10))
    lang_direction_hints = {}

    for lang in langs:
        lang_direction_hints[lang] = {}
        for direction1 in directions:
            lang_direction_hints[lang][direction1] = {}

    for direction1 in directions:
        for direction2 in directions:
            pos = (direction1, direction2)
            if pos in layout:
                letters = layout[pos]
            else:
                letters = {}

            for lang in langs:
                letter = letters.get(lang, "")
                lang_direction_hints[lang][direction1][direction2] = letter

    for lang in langs:
        for direction1 in directions:
            dirs2 = lang_direction_hints[lang][direction1].values()
            dirs2 = [d for d in dirs2 if d]
            lang_direction_hints[lang][direction1][0] = " ".join(dirs2)

    return lang_direction_hints


def load_configs():
    with open("configs.json", encoding="utf8") as file:
        return json.load(file)
