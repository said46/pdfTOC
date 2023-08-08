import fitz
import re

path = "pdfs/Fire and Gas Instrument Loop Diagrams WITH BOOKMARKS.pdf"
pattern = r"600-(\d|\w)\d\d-[A-Z]{1,3}-\d\d\d\w*"

doc = fitz.Document(path)

toc_list = doc.get_toc()

with open(f"pdfs/source_toc.txt", "w") as my_file:
    my_file.write(str([bm[1] for bm in toc_list]))

replaced_symbols = ('l', 'I', '|', 'T', 'L', 'i', 'U')

for toc_item in toc_list:
    toc_item[1] = toc_item[1].replace(" ", "")

    if toc_item[1] == "600-030-X-1":
        toc_item[1] = "600-030-X-111"
        continue
    if toc_item[1] == "600-7-090-009":
        toc_item[1] = "600-060-L-009"
        continue
    if toc_item[1] == "600-H-090-009":
        toc_item[1] = "600-060-H-009"
        continue

    title_split = toc_item[1].split("-")

    if title_split[2] in ("NEI", "NF1", "NE1"):
        title_split[2] = "NFI"

    if title_split[2] == "E":
        title_split[2] = "F"

    if title_split[2] in ("N0D",):
        title_split[2] = "NOD"

    if len(title_split[1]) == 2:
        title_split[1] = title_split[1] + '1'

    for pos in {1, 2}:
        if title_split[1][pos] in replaced_symbols:
            title_split[1] = title_split[1][:pos] + '1' + title_split[1][pos + 1:]

    if len(title_split[3]) == 2:
        title_split[3] = title_split[3] + '1'

    for pos in {0, 1, 2}:
        if title_split[3][pos] in replaced_symbols:
            title_split[3] = title_split[3][:pos] + '1' + title_split[3][pos + 1:]

    if len(title_split[2]) == 3:
        if title_split[2][2] == '0':
            title_split[2] = title_split[2][:2] + 'O'

    if len(title_split[1]) == 3:
        if title_split[1][1] == 'O':
            title_split[1] = title_split[1][0] + '0' + title_split[1][2]

    if (title_split[1]) == "NF11":
        title_split[1] = 'A11'

    toc_item[1] = "-".join(title_split)

toc_list.sort(key=lambda x: x[1])
doc.set_toc(toc_list)

print(f"**************************************************************")
print(f"                        Last check:")
print(f"**************************************************************")
for toc_item_number, toc_item in enumerate(toc_list):
    if not re.match(pattern, toc_item[1]):
        print(f"incorrect toc_item {toc_item_number}: {toc_item[1]}, page {toc_item[2]}")

with open(f"pdfs/toc.txt", "w") as my_file:
    my_file.write(str([bm[1] for bm in toc_list]))

doc.save(f"pdfs/_sorted.pdf")
doc.close()
