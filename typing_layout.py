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


def load_layout():
    lang_layout = {}
    for lang in langs:
        with open(f"layout_{lang}.json", mode="r", encoding='utf8') as file:
            layout = json.load(file)

        converted = {}
        for dir1 in arrow_directions:
            num1 = arrows_to_btn_num[dir1]
            converted[num1] = {}
            for dir2 in arrow_directions:
                try:
                    letter = layout[dir1][dir2]
                except KeyError:
                    continue
                else:
                    num2 = arrows_to_btn_num[dir2]
                    if letter:
                        converted[num1][num2] = code_map[letter]

        lang_layout[lang] = converted

    return lang_layout


def generate_hints(layout):
    detailed_hints = {}
    preview_hints = {}

    for lang in langs:
        detailed_hints[lang] = {}
        preview_hints[lang] = {}

        for dir1 in num_directions:
            detailed_hints[lang][dir1] = {}
            preview_hints[lang][dir1] = ''

            for dir2 in num_directions:
                try:
                    letter = layout[lang][dir1][dir2]
                except KeyError:
                    letter = ""
                else:
                    letter = reverse_code_map[letter]

                detailed_hints[lang][dir1][dir2] = letter

            dirs2 = detailed_hints[lang][dir1].values()
            dirs2 = [d for d in dirs2 if d]
            preview_hints[lang][dir1] = " ".join(dirs2)

    return detailed_hints, preview_hints


def load_configs():
    with open("configs.json", encoding="utf8") as file:
        return json.load(file)


def convert_layout():
    layout = {}
    for dir1 in arrow_directions:
        layout[dir1] = {}
        for dir2 in arrow_directions:
            layout[dir1][dir2] = ''

    with open("layout.csv", encoding="utf8") as layout_csv:
        content = layout_csv.readlines()

    content = content[2:]
    for line in content:
        line = line.replace(' ', '').replace('\n', '').lower()
        if line and not line.startswith(';'):
            typing_positions, letters = line.split('=>')
            pos1, pos2 = typing_positions.split('&')

            letters = letters.replace('none', '')
            letters = letters.split('|')
            letters = [letter.capitalize() for letter in letters]

            if letters[0]:
                layout[pos1][pos2] = letters[0]

    with open("layout_en.json", mode="w+", encoding='utf8') as file:
        json.dump(layout, file, ensure_ascii=False, indent='  ')

    return layout
