import fitz
import re

path = "pdfs/ESD Instrument Loop Diagrams WITH BOOKMARKS.pdf"
pattern = r"(600-\d\d\d-\w-\d\d\d\w*)"

doc = fitz.Document(path)

toc_list = doc.get_toc()

for toc_item in toc_list:
    if not re.match(pattern, toc_item[1]):
        print(f'{toc_item[1]} does not match the pattern, correcting...')

        if len(toc_item[1]) == 12:
            toc_item[1] = toc_item[1] + '1'

        for pos in {4, 5, 6, 10, 11, 12}:
            if toc_item[1][pos] in {'l', 'I', '|', 'T'}:
                toc_item[1] = toc_item[1][:pos] + '1' + toc_item[1][pos + 1:]

        print(f"Corrected title is: {toc_item[1]}")

toc_list.sort(key=lambda x: x[1])
doc.set_toc(toc_list)

with open(f"pdfs/toc.txt", "w") as my_file:
    my_file.write(str([bm[1] for bm in toc_list]))

doc.save(f"pdfs/_sorted.pdf")
doc.close()
