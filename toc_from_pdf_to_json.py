import os
import fitz
import json


os.system('cls')

path = "pdfs/PCS Instrument Loop Diagrams with bookmarks.pdf"
print(f'Opening {path}...')
doc = fitz.Document(path)

print(f"Getting toc_list")
toc_list = doc.get_toc()

with open("pdfs/toc_saved.json", "w") as fp:
    print("Saving toc_list into a .json file...")
    json.dump(toc_list, fp)

print(f"Closing the pdf....")
doc.close()

# print(toc_list[0])