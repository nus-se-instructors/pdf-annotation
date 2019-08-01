import logging

# Add Page numbers
# https://stackoverflow.com/questions/25164871/how-to-add-page-numbers-to-pdf-file-using-python-and-matplotlib


# Add table of contents
# https://stackoverflow.com/questions/6157456/create-outlines-toc-for-existing-pdf-in-python

# How to add an index page

# https://code.tutsplus.com/tutorials/how-to-work-with-pdf-documents-using-python--cms-25726

# How to muck around with PDFs:
# https://automatetheboringstuff.com/chapter13/

import bs4
import fitz
import os

from pylovepdf.tools.pagenumber import Pagenumber
from collections import defaultdict


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
    toc_headers = []
    toc = [[1, "Textbook", 0]]
    for page_number in range(doc.pageCount):
        page_text = doc.getPageText(page_number)
        section_index = page_text.find(SECTION_DELIMITER)
        if section_index != -1:
            section_title = page_text[section_index:].split("\n")[0]
            logging.info("Section title is %s" % section_title)
            # Adjust for the fact that pages are 0 indexed
            toc.append([LEVEL, section_title, page_number + 1])
            toc_headers.append(section_title)
    logging.info("The items in the table of contents are:" % toc)
    doc.setToC(toc)
    # Append the content page to the front of the document
    doc.save(OUTPUT)
    return toc_headers


def generate_index_entries(doc):
    import spacy

    nlp = spacy.load("en_core_web_sm")
    output_dict = defaultdict(list)
    for page_number in range(doc.pageCount):
        page_text = doc.getPageText(page_number)
        parsed_doc = nlp(page_text)
        # Stem and lemmatize
        proper_word = (
            lambda x: x.pos_ != "PUNCT"
            and x.pos_ != "VERB"
            and x.text.isalpha()
            and x.pos_ != "DET"
            and x.pos != "ADV"
        )
        for word in parsed_doc:
            if word.is_stop == False and proper_word(word):
                output_dict[word.lemma_].append(page_number + 1)
    # Arbitrary filtering conditions
    output_dict = {
        k: v
        for k, v in output_dict.items()
        if (len(k) > 4 and len(v) <= 6 and len(k) <= 10 and "ly" not in k)
    }
    return output_dict


def generate_content_page(headers_and_subheaders, page_height, page_width):
    # Open The document
    # for k,v in headers_and_subheaders.items():
    # Print k
    # Then for item in v indent and then print
    # Return the document
    # Create New page
    doc = fitz.open()
    page = doc.newPage(height=page_height, width=page_width)
    horizontal_start_point = 40
    vertical_start_point = 60
    spacing = 15
    num_lines = 1
    tab = 30
    total_length = 70
    REDUNDANT_WORDS = [
        "Introduction",
        "More",
        "Self-Directed",
        "Aug '19",
        "Guideline:",
        "PersonOverviewController",
    ]
    p = fitz.Point(
        horizontal_start_point + 250, vertical_start_point + num_lines * spacing
    )
    page.insertText(p, "Table of Contents", fontname="helv", fontsize=32)
    for h1_item, h2_items in headers_and_subheaders.items():

        # Insert the h1_item

        p = fitz.Point(
            horizontal_start_point, vertical_start_point + num_lines * spacing
        )
        page.insertText(p, h1_item, fontname="helv", fontsize=24, rotate=0)
        num_lines += 2
        for h2_item in h2_items:
            if any(word in h2_item for word in REDUNDANT_WORDS):
                continue
            p_tab = fitz.Point(
                tab + horizontal_start_point, vertical_start_point + num_lines * spacing
            )
            page.insertText(p_tab, h2_item, fontname="helv", fontsize=16, rotate=0)
            num_lines += 1
        num_lines += 2
        if num_lines >= 45:
            page = doc.newPage(height=page_height, width=page_width)
            horizontal_start_point = 40
            vertical_start_point = 60
            num_lines = 0

    return doc


def get_headers_and_subheaders():
    textbook_website = (
        "https://nus-cs2103-ay1920s1.github.io/website/se-book-adapted/print.html"
    )
    from urllib.request import urlopen

    from collections import defaultdict

    headers_and_subheaders = defaultdict(list)

    html = urlopen(textbook_website)
    bs = bs4.BeautifulSoup(html, "html.parser")
    titles = bs.find_all(["h1", "h2"])
    res = []
    is_new_section = lambda x: x and "SECTION: " in x
    section = ""
    # Find the list of h1 and h2 tags
    # If you encounter a h1 tag then append a h2
    for title in titles:
        for child in title.children:
            if is_new_section(child.string):
                section = child.string.replace("SECTION: ", "")
                continue
            if (
                type(child) is not bs4.element.NavigableString
                and child.string is not None
            ):
                headers_and_subheaders[section].append(child.string)

    return headers_and_subheaders


def generate_index_page(output_dict, page_width, page_height):

    doc = fitz.open()
    page = doc.newPage(height=page_height, width=page_width)
    horizontal_start_point = 40
    vertical_start_point = 45
    index_keys = sorted(output_dict.keys(), key=lambda v: v.upper())
    number_of_entries = len(index_keys)
    row_item_counter = 0
    row_item_counter_height = 8
    items_per_column = 110
    columns_per_page = 5
    items_per_page = items_per_column * columns_per_page
    column_spacing = 125
    column_item_counter = 1
    for item_counter in range(number_of_entries):
        row_item_counter += 1
        p = fitz.Point(
            horizontal_start_point + column_item_counter * column_spacing,
            vertical_start_point + row_item_counter * row_item_counter_height,
        )
        if row_item_counter % items_per_column == 0:
            row_item_counter = 0
            column_item_counter += 1

        if column_item_counter % columns_per_page == 0:
            column_item_counter = 1
            row_item_counter = 0

            page = doc.newPage(width=page_width, height=page_height)
        index_word = index_keys[item_counter]

        text = "%s %s" % (index_word, list(set(output_dict[index_word])))
        rc = page.insertText(
            p,  # bottom-left of 1st char
            text,  # the text (honors '\n')
            fontname="helv",  # the default font
            fontsize=8,  # the default font size
            rotate=0,
        )

    return doc


if __name__ == "__main__":
    doc = fitz.open(TEXTBOOK)

    page_width = int(doc[0].bound().width)
    page_height = int(doc[0].bound().height)

    headers_and_subs = get_headers_and_subheaders()
    content_page = generate_content_page(headers_and_subs, page_height, page_width)
    doc.insertPDF(content_page, start_at=0, links=True)
    doc.save("text3.pdf")
    exit(0)

    """
    try:
        add_toc(doc)
    except Error as e:
        logging.info(e)
        raise Exception("Bookmark addition failed")
    """

    try:
        output_dict = generate_index_entries(doc)
    except Error as e:
        logging.info(e)
        raise Exception("Index addition failed")

    """
    try:
        add_page_numbers(TEXTBOOK)
    except Error as e:
        logging.info(e)
        raise Exception("Page number addition failed")
    """

    index_page = generate_index_page(output_dict, page_width, page_height)
    doc.insertPDF(index_page, start_at=doc.pageCount, links=True)
    doc.save("text2.pdf")
