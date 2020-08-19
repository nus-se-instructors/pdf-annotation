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
import logging

from collections import defaultdict, OrderedDict
from urllib.request import urlopen

from downloader import Downloader

OUTPUT_FOLDER = "./outputs"
TEXTBOOK = "./inputs/textbook.pdf"
OVERLAY = os.path.join(OUTPUT_FOLDER, "overlay.pdf")
OUTPUT = os.path.join(OUTPUT_FOLDER, "textbook_output.pdf")
DEFAULT_ERROR_MESSAGE = "%s phase failed"
TEXTBOOK_WEBSITE = (
    "https://nus-cs2103-ay1920s1.github.io/website/se-book-adapted/print.html"
)
SECTION_DELIMITER = "SECTION: "


def add_bookmarks(doc, header_to_pagenumber, headers_and_subs, no_content_pages):
    LEVEL = 2
    # Initial level one heading
    toc = [[1, "Textbook", 0]]
    # Add Section Headers
    for header in headers_and_subs.keys():
        toc.append([LEVEL, SECTION_DELIMITER + header, header_to_pagenumber[header] + no_content_pages])
    logging.info("The items in the table of contents are:" % toc)
    # Save bookmarks
    doc.setToC(toc)
    doc.save(OUTPUT)


def generate_index_entries(doc):
    import spacy

    nlp = spacy.load("en_core_web_sm")
    output_dict = defaultdict(list)
    for page_number in range(doc.pageCount):
        page_text = doc.getPageText(page_number)
        parsed_doc = nlp(page_text)
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


def generate_content_page(
    header_to_pagenumber, headers_and_subheaders, page_height, page_width
):
    doc = fitz.open()
    page = doc.newPage(height=page_height, width=page_width)
    horizontal_start_point = 40
    vertical_start_point = 60
    spacing = 15
    num_lines = 1
    tab = 30
    p = fitz.Point(
        horizontal_start_point + 250, vertical_start_point + num_lines * spacing
    )
    page.insertText(p, "Table of Contents", fontname="helv", fontsize=32)
    num_lines += 4
    for h1_item, h2_items in headers_and_subheaders.items():

        # Insert the h1_item

        p = fitz.Point(
            horizontal_start_point, vertical_start_point + num_lines * spacing
        )
        page.insertText(p, h1_item, fontname="helv", fontsize=24, rotate=0)
        num_lines += 2
        for h2_item in h2_items:
            p_tab = fitz.Point(
                tab + horizontal_start_point, vertical_start_point + num_lines * spacing
            )
            page.insertText(p_tab, h2_item, fontname="helv", fontsize=16, rotate=0)
            p_tab_number = fitz.Point(
                tab + horizontal_start_point + 500,
                vertical_start_point + num_lines * spacing,
            )
            page.insertText(
                p_tab_number,
                str(header_to_pagenumber[h2_item]),
                fontname="helv",
                fontsize=16,
                rotate=0,
            )

            # TODO: If the mapping exists then move horizontally by 500 and then print that page number
            num_lines += 1
        num_lines += 2
        if num_lines >= 45:
            page = doc.newPage(height=page_height, width=page_width)
            horizontal_start_point = 40
            vertical_start_point = 60
            num_lines = 0

    return doc


def get_headers_and_subheaders(tags=["h1"]):
    """
    Generates an ordered dictionary of L1 headers mapped to L2 headers
    """
    headers_and_subheaders = OrderedDict()

    html = urlopen(TEXTBOOK_WEBSITE)
    bs = bs4.BeautifulSoup(html, "html.parser")
    titles = bs.find_all(tags)
    section = ""
    # Find the list of h1 and h2 tags
    # If you encounter a h1 tag then append a h2
    for title in titles:
        for child in title.children:
            if is_new_section(child.string):
                section = child.string.replace(SECTION_DELIMITER, "")
                continue
            if (
                type(child) is not bs4.element.NavigableString
                and child.string is not None
            ):
                # Prevent addition of "" headers
                if not section:
                    continue
                if headers_and_subheaders.get(section):
                    headers_and_subheaders[section].append(child.string)
                else:
                    headers_and_subheaders[section] = [child.string]
    return headers_and_subheaders


def is_new_section(header):
    return header and SECTION_DELIMITER in header


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
        page.insertText(
            p,  # bottom-left of 1st char
            text,  # the text (honors '\n')
            fontname="helv",  # the default font
            fontsize=8,  # the default font size
            rotate=0,
        )

    return doc


def get_page_number(doc):
    """
    Returns a dictionary mapping of header to page number
    """
    headers_and_subheaders = get_headers_and_subheaders(tags=["h1"])
    header_to_pagenumber = {}

    page_num = 1
    for L1_header, L2_headers in headers_and_subheaders.items():
        # First locate the L1 header
        page_num = locate(SECTION_DELIMITER + L1_header, doc, page_num)
        header_to_pagenumber[L1_header] = page_num

        # Then locate each L2 header
        for L2_header in L2_headers:
            # Add newline character to prevent matching inline occurrences of the header
            page_num = locate(L2_header + "\n", doc, page_num)
            header_to_pagenumber[L2_header] = page_num

    return header_to_pagenumber


def locate(keyword, doc, page_num):
    """
    Searches for the given keyword in the doc starting from a specified page number
    """
    while keyword not in doc.getPageText(page_num - 1) and page_num < doc.pageCount:
        page_num += 1
    return page_num


if __name__ == "__main__":
    downloader = Downloader(TEXTBOOK_WEBSITE)
    try:
        downloader.download_to(TEXTBOOK)
    except Exception as e:
        logging.info(e)
        print("Download failed, using existing copy of textbook")

    doc = fitz.open(TEXTBOOK)

    page_width = int(doc[0].bound().width)
    page_height = int(doc[0].bound().height)

    header_to_pagenumber = get_page_number(doc)
    headers_and_subs = get_headers_and_subheaders()
    content_page = generate_content_page(
        header_to_pagenumber, headers_and_subs, page_height, page_width
    )
    doc.insertPDF(content_page, start_at=0, links=True)

    try:
        add_bookmarks(doc, header_to_pagenumber, headers_and_subs, content_page.pageCount)
    except Exception as e:
        logging.info(e)
        raise Exception("Bookmark addition failed")

    """
    try:
        output_dict = generate_index_entries(doc)
    except Exception as e:
        logging.info(e)
        raise Exception("Index addition failed")
    
    index_page = generate_index_page(output_dict, page_width, page_height)

    doc.insertPDF(index_page, start_at=doc.pageCount, links=True)
    """

    doc.save(OUTPUT)
