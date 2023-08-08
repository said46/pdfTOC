import os
from paddleocr import PaddleOCR
import fitz
from PIL import Image, ImageDraw
import numpy as np
# import cv2
# such import resolves "Cannot find reference 'xxx' in '__init__.py | __init__.py'" issue
from cv2 import cv2


os.system('cls')

path = "pdfs/Fire and Gas Instrument Loop Diagrams.pdf"

print(f'Opening {path}...')
doc = fitz.Document(path)

DPI = 200
PDF_ZOOM_FACTOR = 72 / DPI
crop_image: bool = True
preprocess_image = True
kernel_size = (2, 2)  # (2, 2)
save_preprocessed_image = True
save_original_image = False
save_result_to_txt = False
visible_red_text = False

first_page: int = 450  # 1
last_page: int = 460   # 1419

# crop coordinates for DPI=150
crop_x0: int = 1860
crop_y0: int = 1500
crop_x1: int = 2225
crop_y1: int = 1550

crop_x0 = int(crop_x0 * DPI / 150)
crop_y0 = int(crop_y0 * DPI / 150)
crop_x1 = int(crop_x1 * DPI / 150)
crop_y1 = int(crop_y1 * DPI / 150)

print(f'Creating a new pdf document...')
new_doc: fitz.Document = fitz.Document()
toc_list = []


for enumerated_page_number, page_number in enumerate(range(first_page-1, last_page)):
    print(f'Loading page number {page_number + 1}...')
    page = doc.load_page(page_number)

    print(f'Getting pix with dpi {DPI}...')
    pix = page.get_pixmap(dpi=DPI)

    page_pillow_image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    if crop_image:
        print(f'Cropping the page image...')
        page_pillow_image = page_pillow_image.crop((crop_x0, crop_y0, crop_x1, crop_y1))

    page_opencv_orig_image = np.asarray(page_pillow_image)
    if save_original_image:
        print(f'Saving original page image...')
        cv2.imwrite(f'pdfs/img_original_{DPI}.png', page_opencv_orig_image)

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
            cv2.imwrite(f'pdfs/img_pre-processed_{DPI}_{page_number}.png', page_opencv_image)
    else:
        page_opencv_image = page_opencv_orig_image

    print(f'OCRing page {page_number + 1}...')
    ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    result = ocr.ocr(page_opencv_image, cls=True)

    # as there is only one page, the result contains only one element
    ocr_result_data = result[0]

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
    cv2.imwrite(f'pdfs/img_ocred_{DPI}.png', page_opencv_ocred_image)

    print(f'Inserting a new page from the original document...')
    new_doc.insert_pdf(doc, page_number, page_number, annots=True)
    new_page = new_doc[enumerated_page_number]

    if txts:
        if len(txts[0]) > 3:
            if txts[0][:4] == '600-':
                toc_list.append([1, txts[0], enumerated_page_number+1])  # [lvl, title, page, dest (optional)]

    if visible_red_text:
        tw: fitz.TextWriter = fitz.TextWriter(new_page.rect, opacity=1, color=(1, 0, 0))
    else:
        tw: fitz.TextWriter = fitz.TextWriter(new_page.rect, opacity=0, color=(1, 1, 1))

    if crop_image:
        boxes = boxes_cropped
    for rect, text in zip(boxes, txts):
        pdf_text_rect_bl = [c * PDF_ZOOM_FACTOR for c in rect[3]]
        tw.append(pdf_text_rect_bl, text, fontsize=16)

    tw.write_text(new_page)

toc_list.sort(key=lambda x: x[1])
new_doc.set_toc(toc_list)

try:
    new_doc.save(f"pdfs/test_{DPI}.pdf")
except RuntimeError as e:
    print("cannot save file: Permission denied")
new_doc.close()

doc.close()
