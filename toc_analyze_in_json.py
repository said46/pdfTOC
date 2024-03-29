import os
import fitz
import json

"""
    The script loads the toc from a json-file, where the toc was saved previously, 
    finds missing pages and saves the toc, sorted by page number into toc_sorted_by_page_number.json
"""

os.system('cls')

print("*"*100)

with open("pdfs/toc_saved.json", "r") as fp:
    print("Loading toc_list from a .json file...")
    toc_list = json.load(fp)

toc_list.sort(key=lambda x: x[2])

# print(f"{page}: {toc_list[page - start_page][2]}")
# print(f"{page} is missing")

prev_page_number = toc_list[0][2] - 1
for i, bm in enumerate(toc_list):        
    if bm[2] != prev_page_number + 1:
        print(f"page {bm[2] + 1} is missing")
    prev_page_number = bm[2]

with open("pdfs/toc_sorted_by_page_number.json", "w") as fp:
    print("Saving toc_list into a .json file...")
    json.dump(toc_list, fp)