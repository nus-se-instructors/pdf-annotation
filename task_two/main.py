import logging

# Add Page numbers
# https://stackoverflow.com/questions/25164871/how-to-add-page-numbers-to-pdf-file-using-python-and-matplotlib


# Add table of contents
# https://stackoverflow.com/questions/6157456/create-outlines-toc-for-existing-pdf-in-python

# How to add an index page

# https://code.tutsplus.com/tutorials/how-to-work-with-pdf-documents-using-python--cms-25726

# How to muck around with PDFs:
# https://automatetheboringstuff.com/chapter13/

import fitz
import os
from pylovepdf.tools.pagenumber import Pagenumber


OUTPUT_FOLDER = "./outputs"
TEXTBOOK = "./inputs/textbook.pdf"
OVERLAY = os.path.join(OUTPUT_FOLDER, "overlay.pdf")
OUTPUT = os.path.join(OUTPUT_FOLDER, "textbook_output.pdf")
DEFAULT_ERROR_MESSAGE = "%s phase failed"
PUBLIC_KEY = "project_public_36e2b8c0ce3c0d29905ab7acecbd1174_EwMDq1a590e7848c9bb7f57fd2429741123c9"


def add_page_numbers(filename):

    t = Pagenumber(PUBLIC_KEY, verify_ssl=True)
    t.add_file(filename)
    t.debug = False
    t.set_output_folder(OUTPUT_FOLDER)
    t.execute()
    t.download()
    return True


def add_toc(doc):
    SECTION_DELIMITER = "SECTION: "
    LEVEL = 2
    # Initial level one heading
    toc = [[1, "Textbook", 0]]
    for page_number in range(doc.pageCount):
        page_text = doc.getPageText(page_number)
        section_index = page_text.find(SECTION_DELIMITER)
        if section_index != -1:
            section_title = page_text[section_index:].split("\n")[0]
            logging.info("Section title is %s" % section_title)
            # Adjust for the fact that pages are 0 indexed
            toc.append([LEVEL, section_title, page_number + 1])
    logging.info("The items in the table of contents are:" % toc)
    doc.setToC(toc)
    doc.save(OUTPUT)
    return True


def add_index(doc):

    raise NotImplementedError("Index addition not implemented")


if __name__ == "__main__":
    doc = fitz.open(TEXTBOOK)
    add_page_numbers(TEXTBOOK)

    try:
        add_page_numbers(INPUT)
    except Error as e:
        logging.info(e)
        raise Exception("Page number addition failed")

    try:
        add_toc(doc)
    except Error as e:
        logging.info(e)
        raise Exception("Bookmark addition failed")
    """
    try:
        add_index(doc)
    except Error as e:
        logging.info(e)
        raise Exception("Index addition failed")
    """
