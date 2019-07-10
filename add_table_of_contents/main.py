import logging
from matplotlib.backends.backend_pdf import PdfPages
import PyPDF2
from tika import parser


# Add Page numbers
# https://stackoverflow.com/questions/25164871/how-to-add-page-numbers-to-pdf-file-using-python-and-matplotlib


# Add table of contents
# https://stackoverflow.com/questions/6157456/create-outlines-toc-for-existing-pdf-in-python

# How to add an index page

# https://code.tutsplus.com/tutorials/how-to-work-with-pdf-documents-using-python--cms-25726

# How to muck around with PDFs:
# https://automatetheboringstuff.com/chapter13/


from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileReader, PdfFileMerger
from pdfrw import PdfReader, PdfWriter, PageMerge


TEXTBOOK = "./inputs/textbook.pdf"
OVERLAY = "./outputs/overlay.pdf"
OUTPUT = "./outputs/textbook_output.pdf"


def create_overlay(num_pages):
    """
    Create a multi-page document
    """
    c = canvas.Canvas(OVERLAY)

    for i in range(num_pages):
        page_num = c.getPageNumber()
        text = "%s" % page_num
        c.drawString(800, 40, text)
        c.showPage()
    c.save()


def watermarker(textbook, overlay, output):
    base_pdf = PdfReader(textbook)
    watermark_pdf = PdfReader(overlay)

    for page in range(len(base_pdf.pages)):
        mark = watermark_pdf.pages[page]
        merger = PageMerge(base_pdf.pages[page])
        merger.add(mark).render()

    writer = PdfWriter()
    writer.write(output, base_pdf)


def extract_text(TEXTBOOK):
    text = textract.process(TEXTBOOK)
    print(text)


# ----------------------------------------------------------------------


if __name__ == "__main__":
    pdf = PdfFileReader(open(TEXTBOOK, "rb"))
    num_pages = pdf.getNumPages()
    create_overlay(num_pages)
    watermarker(TEXTBOOK, OVERLAY, OUTPUT)
    raw = parser.from_file(TEXTBOOK)
    with open("pdftotext.txt", "w") as output:
        output.write(raw["content"])
