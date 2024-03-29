import os
import fitz
import json


os.system('cls')

path = "pdfs/ESD toc test.pdf"
print(f'Opening {path}...')
doc = fitz.Document(path)

with open("pdfs/toc test.json", "r") as fp:
    print("Loading toc_list from a .json file...")
    toc_list = json.load(fp)

toc_list.sort(key=lambda x: x[1])
try:
    doc.set_toc(toc_list)
except Exception as e:
    print(f"Exception while adding the TOC: {str(e)}")

try:
    print(f'Saving the pdf document with updated toc...')
    doc.save(f"pdfs/updated_toc.pdf")
except RuntimeError as e:
    print("cannot save file: Permission denied")
print(f'Closing the pdf document...')
doc.close()

# print(toc_list[0])