from pathlib import Path

mapping = {
    "🢂": 'Right',
    "🢅": 'UpRight',
    "🢁": 'Up',
    "🢄": 'UpLeft',
    "🢀": 'Left',
    "🢇": 'DownLeft',
    "🢃": 'Down',
    "🢆": 'DownRight',
}

mapping = {
    "🢂": '→',
    "🢅": '↗',
    "🢁": '↑',
    "🢄": '↖',
    "🢀": '←',
    "🢇": '↙',
    "🢃": '↓',
    "🢆": '↘',
}

def main():
    cur_project = Path(__file__).parent.parent.resolve()
    print(cur_project)
    base_directory = cur_project
    for p in base_directory.iterdir():
        if p.name == 'convert.py' or not (p.is_file() and (p.match('*.py') or p.match('*.csv'))):
            continue

        with open(p, mode='r', encoding='utf8') as file:
            content = file.read()

        for uni_sign, text_repr in mapping.items():
            content = content.replace(uni_sign, text_repr)

        with open(p, mode='w+', encoding='utf8') as file:
            file.write(content)


if __name__ == '__main__':
    main()
