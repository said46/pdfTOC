import os
from fitz import Page, Document

os.system('cls')

doc = Document("pdfs/final_results/Fire and Gas Instrument Loop Diagrams with bookmarks.pdf")
toc = doc.get_toc()

for i, bm in enumerate(toc):
    print(f"Processing page {i+1}...")
    bm_title = bm[1]
    bm_page_number = bm[2]-1
    print(f"{bm_title=} {bm_page_number=}")
    new_doc = Document()
    new_doc.insert_pdf(doc, bm_page_number, bm_page_number, annots=True)
    new_doc.save(f"pdfs/final_results/FGS_split/{bm_title}.pdf")
    new_doc.close()

doc.close()