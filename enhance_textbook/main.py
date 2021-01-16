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
import sys
import ahocorasick
import csv

from collections import defaultdict, OrderedDict
from urllib.request import urlopen

from downloader import Downloader

OUTPUT_FOLDER = "./outputs"
TEXTBOOK = "./inputs/textbook.pdf"
OVERLAY = os.path.join(OUTPUT_FOLDER, "overlay.pdf")
OUTPUT = os.path.join(OUTPUT_FOLDER, "textbook_output.pdf")
DEFAULT_ERROR_MESSAGE = "%s phase failed"
TEXTBOOK_WEBSITE = (
    "https://nus-cs2103-ay2021s1.github.io/website/se-book-adapted/print.html"
)
SECTION_DELIMITER = "SECTION: "


def add_bookmarks(doc, header_to_pagenumber, headers_and_subs, no_content_pages, allow_second_level=True):
    LEVEL_1 = 2
    LEVEL_2 = 3
    # Initial level one heading
    toc = [[1, "Textbook", 0]]
    # Add first-level headers
    for header, subheaders in headers_and_subs.items():
        toc.append([LEVEL_1, SECTION_DELIMITER + header, header_to_pagenumber[header] + no_content_pages])
        if allow_second_level:
            # Add second-level headers
            for subheader in subheaders:
                toc.append([LEVEL_2, subheader, header_to_pagenumber[subheader] + no_content_pages])

    logging.info("The items in the table of contents are:" % toc)
    # Save bookmarks
    doc.setToC(toc)
    doc.save(OUTPUT)


def generate_index_entries(doc):
    index_terms = get_index_terms()
    index_term_pages = defaultdict(list)

    # Use Aho-Corasick algorithm for fast string-searching
    A = ahocorasick.Automaton()
    for index_term in index_terms:
        A.add_word(index_term, index_term)
    A.make_automaton()

    for page_number in range(doc.pageCount):
        page_text = doc.getPageText(page_number)
        for _, term in A.iter(page_text.lower()):
            # Add page number for the term if it does not already exist
            pages = index_term_pages[term]
            if not pages or pages[-1] != page_number + 1:
                pages.append(page_number + 1)

    # Filter out index terms with more than 10 occurrences (likely not index-worthy)
    index_term_pages = {k: v for k, v in index_term_pages.items() if len(v) <= 10}
    return index_term_pages


def get_index_terms():
    """
    Obtains a set of possible index terms.
    The index terms will be scraped from website headings. There are additionally two csv files in the inputs folder,
    include.csv and exclude.csv that can be used to specify what index terms to include or exclude.
    """
    index_terms = set()
    index_terms |= get_index_terms_from_website()
    index_terms |= get_index_terms_from_csv('inputs/include.csv')
    return index_terms.difference(get_index_terms_from_csv('inputs/exclude.csv'))


def get_index_terms_from_website():
    """
    Obtains a set of possible index terms by using headers from the textbook website.
    """
    html = urlopen(TEXTBOOK_WEBSITE)
    bs = bs4.BeautifulSoup(html, "html.parser")
    headers = {header.text.replace(':', '').strip().lower() for header in bs.find_all(["h1", "h2", "h3", "h4", "h5"])}
    # Filter out headers that are longer than 3 words (unlikely to be index-worthy)
    return {header for header in headers if len(header.split(' ')) <= 3}


def get_index_terms_from_csv(filename):
    """
    Obtains a list of possible index terms from a pre-generated csv file. csv file is assumed to be rows of
    comma-separated strings
    Source(s) for index terms:
    https://www.iqbba.org/files/content/iqbba/downloads/Standard_glossary_of_terms_used_in_Software_Engineering_1.0.pdf
    """
    index_terms = set()
    with open(filename) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            index_terms |= set(row)
    return index_terms


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

    # Add Table of Contents heading (centered)
    rect_topleft = fitz.Point(0, vertical_start_point + num_lines * spacing)
    num_lines += 4
    rect_bottomright = fitz.Point(page_width, vertical_start_point + num_lines * spacing)
    rect = fitz.Rect(rect_topleft, rect_bottomright)
    page.insertTextbox(rect, "Table of Contents", fontsize=32, align=fitz.TEXT_ALIGN_CENTER)
    num_lines += 2

    # Create a TextWriter (per page)
    wr = fitz.TextWriter(page.rect)
    for h1_item, h2_items in headers_and_subheaders.items():
        # Insert the h1_item
        p = fitz.Point(
            horizontal_start_point, vertical_start_point + num_lines * spacing
        )
        wr.append(p, h1_item, fontsize=24)
        num_lines += 2
        for h2_item in h2_items:
            # Insert each h2_item
            p_tab = fitz.Point(
                tab + horizontal_start_point, vertical_start_point + num_lines * spacing
            )
            wr.append(p_tab, h2_item, fontsize=16)

            # Insert ... between h2_item and page number
            p_tab_number = fitz.Point(
                tab + horizontal_start_point + 500,
                vertical_start_point + num_lines * spacing,
            )
            add_dot_connector(wr, wr.lastPoint, p_tab_number)

            # Insert page number for h2_item
            wr.append(p_tab_number, str(header_to_pagenumber[h2_item]), fontsize=16)
            num_lines += 1

            # Move to new page if nearing end of page
            if num_lines >= 45:
                wr.writeText(page)
                page = doc.newPage(height=page_height, width=page_width)
                wr = fitz.TextWriter(page.rect)
                num_lines = 0
        num_lines += 2

    wr.writeText(page)
    return doc


def add_dot_connector(wr, start, end):
    """
    Adds ... between a startpoint and endpoint. Uses a workaround to suppress unnecessary pymupdf warnings about text
    overflow. Credits for workaround: https://stackoverflow.com/a/8447352
    """
    sys.stdout = open(os.devnull, "w")

    dot_connector = "." * 200
    rect_topleft = fitz.Point(start.x, start.y - 15)
    rect_bottomright = fitz.Point(end.x, end.y + 10)
    rect = fitz.Rect(rect_topleft, rect_bottomright)
    wr.fillTextbox(rect, dot_connector)

    sys.stdout = sys.__stdout__


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


def generate_index_page(index_term_pages, page_width, page_height):
    doc = fitz.open()
    page = doc.newPage(height=page_height, width=page_width)
    horizontal_start_point = 40
    vertical_start_point = 45
    index_keys = sorted(index_term_pages.keys(), key=lambda v: v.upper())
    number_of_entries = len(index_keys)
    row_item_counter = 0
    row_item_counter_height = 9
    items_per_column = 80
    columns_per_page = 3
    column_spacing = 180
    column_item_counter = 0
    for item_counter in range(number_of_entries):
        row_item_counter += 1
        p = fitz.Point(
            horizontal_start_point + column_item_counter * column_spacing,
            vertical_start_point + row_item_counter * row_item_counter_height,
        )
        # Insert index term along with page number references
        index_term = index_keys[item_counter]
        text = "%s %s" % (index_term, format_as_page_range(index_term_pages[index_term]))
        page.insertText(
            p,  # bottom-left of 1st char
            text,  # the text (honors '\n')
            fontname="helv",  # the default font
            fontsize=8,  # the default font size
            rotate=0,
        )
        # Increment row and column counter accordingly
        if row_item_counter >= items_per_column:
            row_item_counter = 0
            column_item_counter += 1

        if column_item_counter >= columns_per_page:
            column_item_counter = 0
            row_item_counter = 0

            page = doc.newPage(width=page_width, height=page_height)

    return doc


def format_as_page_range(page_numbers):
    """
    Formats a list of page numbers into more readable and condensed page ranges (as a string)
    e.g. [1,3,4,5,6,7,20] -> "1, 3-7, 20"
    """
    if not page_numbers:
        return []
    page_ranges = []
    prev_num = page_numbers[0]
    consecutive_nums = 1
    for page_num in page_numbers[1:]:
        if page_num == prev_num + consecutive_nums:
            consecutive_nums += 1
        else:
            # Reached the end of a consecutive range
            if consecutive_nums > 1:
                page_ranges.append("%d-%d" % (prev_num, prev_num + consecutive_nums - 1))
            else:
                page_ranges.append(str(prev_num))
            prev_num = page_num
            consecutive_nums = 1
    # Add the last consecutive range
    if consecutive_nums > 1:
        page_ranges.append("%d-%d" % (prev_num, prev_num + consecutive_nums - 1))
    else:
        page_ranges.append(str(prev_num))
    return ', '.join(page_ranges)


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

    try:
        index_term_pages = generate_index_entries(doc)
    except Exception as e:
        logging.info(e)
        raise Exception("Index addition failed")
    
    index_page = generate_index_page(index_term_pages, page_width, page_height)

    doc.insertPDF(index_page, start_at=doc.pageCount, links=True)

    doc.save(OUTPUT)
