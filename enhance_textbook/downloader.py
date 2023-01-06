from base64 import b64decode
from selenium import webdriver


class Downloader:
    """
    A class that uses Chrome's PDF engine to save a website as PDF format with added page numbers
    """
    def __init__(self, url):
        self.url = url

    def download_to(self, filename):
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('headless')  # removed because this causes some images to be missing
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.url)
        input('\n\n################ is the page loaded fully?\n\n')
        print_settings = {'printBackground': True, 'displayHeaderFooter': True,
                          'headerTemplate': '<div class="page-header" style="width:100%; text-align:right; '
                                            'font-size:12px;"></div>',
                          'footerTemplate': '<div class="page-footer" style="width:100%; text-align:right; '
                                            'font-size:12px;"><span class="pageNumber" '
                                            'style="padding-right:10px"></span></div>'}

        res = driver.execute_cdp_cmd('Page.printToPDF', print_settings)

        pdf_bytes = b64decode(res['data'], validate=True)
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
