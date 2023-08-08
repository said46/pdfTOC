import re

pattern = r"(600-(\d|\w)\d\d-\w{1,3}-\d\d\d\w*)"

titles = ('600-A2L-NSO-104', '600-A01-NEI-L10')

for title in titles:
    print(f"original title: {title}")
    title_split = title.split("-")
    for pos in {1, 2}:
        if title_split[1][pos] in {'l', 'I', '|', 'T', 'L'}:
            title_split[1] = title_split[1][:pos] + '1' + title_split[1][pos + 1:]
    for pos in {0, 1, 2}:
        if title_split[3][pos] in {'l', 'I', '|', 'T', 'L'}:
            title_split[3] = title_split[3][:pos] + '1' + title_split[3][pos + 1:]
    title = "-".join(title_split)
    print(f"modified title: {title}")


