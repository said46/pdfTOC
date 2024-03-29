import os
from paddleocr import PaddleOCR
import fitz
from PIL import Image, ImageDraw
import numpy as np
import cv2
# such import resolves "Cannot find reference 'xxx' in '__init__.py | __init__.py'" issue
# from cv2 import cv2
import json


os.system('cls')

path = "pdfs/ESD Instrument Loop Diagrams.pdf"

print(f'Opening {path}...')
doc = fitz.Document(path)

DPI = 150
PDF_ZOOM_FACTOR = 72 / DPI
crop_image: bool = True
preprocess_image = True
kernel_size = (2, 2)  # (2, 2)
save_preprocessed_image = False
save_original_image = True
save_ocred_image = True
save_result_to_txt = True
visible_red_text = False
text_fontsize = 16  # 16 by default

# ESD: 
# pages 1-754
# pages 215-218 have different crop, 
# pages not to OCR or add to TOC: 1-20, 750-754 (last pages are in different format)

first_page: int = 1
last_page: int = 754
drop_pages_list = tuple(range(1, 20)) + tuple(range(750, 755))

# crop coordinates for DPI=150: 1860, 1500, 2225, 1550
crop_x0: int = 1860
crop_y0: int = 1490
crop_x1: int = 2225
crop_y1: int = 1540

crop_x0 = int(crop_x0 * DPI / 150)
crop_y0 = int(crop_y0 * DPI / 150)
crop_x1 = int(crop_x1 * DPI / 150)
crop_y1 = int(crop_y1 * DPI / 150)

print(f'Creating a new pdf document...')
new_doc: fitz.Document = fitz.Document()
toc_list = []

new_page_number = 0
for page_number in range(first_page-1, last_page):
    print(f'Loading page number {page_number + 1}...')
    page = doc.load_page(page_number)

    txts = None    

    # если страница не в списке страниц, которые не надо распознавать
    
    if page_number + 1 not in drop_pages_list:
        add_to_toc: bool = True

        print(f'Getting pix with dpi {DPI}...')
        pix = page.get_pixmap(dpi=DPI)

        page_pillow_image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        if crop_image:
            print(f'Cropping the page image...')
            page_pillow_image = page_pillow_image.crop((crop_x0, crop_y0, crop_x1, crop_y1))

        page_opencv_orig_image = np.asarray(page_pillow_image)
        if save_original_image:
            print(f'Saving original page image...')
            cv2.imwrite(f'pdfs/img/img_original_{DPI}_page_{page_number+1}.png', page_opencv_orig_image)

        if preprocess_image:
            # converting to grayscale
            page_opencv_image = cv2.cvtColor(page_opencv_orig_image, cv2.COLOR_BGR2GRAY)

            # threshold the image using Otsu's thresholding method
            page_opencv_image = cv2.threshold(page_opencv_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            # dilating the image
            kernel = np.ones(kernel_size, np.uint8)
            page_opencv_image = cv2.dilate(page_opencv_image, kernel, iterations=1)

            if save_preprocessed_image:
                print(f'Saving pre-processed page image...')
                cv2.imwrite(f'pdfs/img/img_pre-processed_{DPI}_{page_number}.png', page_opencv_image)
        else:
            page_opencv_image = page_opencv_orig_image

        print(f'OCRing page {page_number + 1}...')
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        result = ocr.ocr(page_opencv_image, cls=True)

        # as there is only one page, the result contains only one element
        ocr_result_data = result[0]

        if ocr_result_data:
            boxes = [line[0] for line in ocr_result_data]
            boxes_cropped = [[[i[0]+crop_x0, i[1]+crop_y0] for i in line[0]] for line in ocr_result_data]

            txts = [line[1][0] for line in ocr_result_data]
            scores = [line[1][1] for line in ocr_result_data]

            draw = ImageDraw.Draw(page_pillow_image)
            for box in boxes:
                try:
                    draw.rectangle((tuple(box[0]), tuple(box[2])), width=1, outline='red')
                except Exception as e:
                    print(f'drawing {box[0]}:{box[2]} failed, {str(e)}')

            if save_result_to_txt:
                with open(f"pdfs/ocr_result_{DPI}.txt", "w") as my_file:
                    print(f'Saving the result into the text file...')
                    my_file.write(str(txts))
                    # my_file.write(str(result[0]))

        print(f'Saving the processed page image...')
        page_opencv_ocred_image = np.asarray(page_pillow_image)
        if save_ocred_image:
            cv2.imwrite(f'pdfs/img/img_ocred_{DPI}_{page_number}.png', page_opencv_ocred_image)
    else:
        add_to_toc: bool = False

    print(f'Inserting a new page from the original document...')
    new_doc.insert_pdf(doc, page_number, page_number, annots=True)
    new_page = new_doc[new_page_number]
    new_page_number += 1

    if txts:
        if len(txts[0]) > 3:
            toc_list.append([1, txts[0], new_page_number])  # [lvl, title, page, dest (optional)]

        # font color and opacity
        if visible_red_text:
            tw: fitz.TextWriter = fitz.TextWriter(new_page.rect, opacity=1, color=(1, 0, 0))
        else:
            tw: fitz.TextWriter = fitz.TextWriter(new_page.rect, opacity=0, color=(1, 1, 1))

        if crop_image:
            boxes = boxes_cropped
        # add each text and box to the TextWriter
        for rect, text in zip(boxes, txts):
            pdf_text_rect_bl = [c * PDF_ZOOM_FACTOR for c in rect[3]]
            tw.append(pdf_text_rect_bl, text, fontsize=text_fontsize)

        # draw all the texts
        tw.write_text(new_page)
    elif add_to_toc:
        toc_list.append([1, "_ERROR", new_page_number])  # [lvl, title, page, dest (optional)]

toc_list.sort(key=lambda x: x[1])
with open("pdfs/toc.json", "w") as fp:
    print("Saving toc_list into a .json file...")
    json.dump(toc_list, fp)

try:
    new_doc.set_toc(toc_list)
except Exception as e:
    print(f"Exception while adding the TOC: {str(e)}")

try:
    print(f'Saving the new document...')
    new_doc.save(f"pdfs/test_{DPI}.pdf")
except RuntimeError as e:
    print("cannot save file: Permission denied")
print(f'Closing the new document...')
new_doc.close()

print(f'Closing the original document...')
doc.close()
print("End of script")

