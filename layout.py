def load_layout():
    layout = {}
    with open("layout.csv", encoding="utf8") as layout_csv:
        content = layout_csv.readlines()

    content = content[2:]
    for line in content:
        line = line.replace(' ', '').replace('\n', '').lower()
        if line and not line.startswith(';'):
            stick_positions, letters = line.split('=>')
            stick_positions = tuple(stick_positions.split('&'))

            letters = letters.replace('none', '')
            letters = letters.split('|')
            letters = [letter.capitalize() for letter in letters]

            if stick_positions in layout:
                raise ValueError(f"Repeated: {letters}")

            layout[stick_positions] = {}
            if letters[0]:
                layout[stick_positions]['en'] = letters[0]
            if letters[1]:
                layout[stick_positions]['ru'] = letters[1]

    return layout


def generate_hints(layout):
    langs = ['en', 'ru']
    directions = ["🢂", "🢅", "🢁", "🢄", "🢀", "🢇", "🢃", "🢆"]
    arrow_map = get_arrow_convert_map()
    lang_direction_hints = {}

    for lang in langs:
        lang_direction_hints[lang] = {}
        for direction1 in directions:
            lang_direction_hints[lang][direction1] = []

    for direction1 in directions:
        for direction2 in directions:
            pos = (direction1, direction2)
            if pos in layout:
                letters = layout[pos]
                for lang, letter in letters.items():
                    lang_direction_hints[lang][direction1].append(f"({arrow_map[direction2]}: '{letter}')")

    for lang in langs:
        for direction1 in directions:
            hints = ', '.join(lang_direction_hints[lang][direction1])
            lang_direction_hints[lang][direction1] = hints

    return lang_direction_hints


def get_arrow_convert_map():
    return {
        "🢂": 'R',
        "🢅": 'UR',
        "🢁": 'U',
        "🢄": 'UL',
        "🢀": 'L',
        "🢇": 'DL',
        "🢃": 'D',
        "🢆": 'DR',
        "⬤": 'Neutral',
        "❌": 'Unmapped',
    }
