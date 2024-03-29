import os
from fitz import Page, Document

"""
    The script splits the pdf into separate files (1 page = 1 pdf-file)
    naming the pdf-files as the bookmark name of the corresponding page
"""

os.system('cls')

doc = Document("pdfs/ESD Instrument Loop Diagrams with bookmarks v2.pdf")
toc = doc.get_toc()

for i, bm in enumerate(toc):
    print(f"Processing page {i+1}...")
    bm_title = bm[1]
    bm_page_number = bm[2]-1
    print(f"{bm_title=} {bm_page_number=}")
    new_doc = Document()
    new_doc.insert_pdf(doc, bm_page_number, bm_page_number, annots=True)
    new_doc.save(f"pdfs/ESD_split/{bm_title}.pdf")
    new_doc.close()

doc.close()