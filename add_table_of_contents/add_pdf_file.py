import logging
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('output.pdf')
for n, fig in enumerate(figs):
    fig.text(4.25/8.5, 0.5/11., str(n+1), ha='center', fontsize=8)
    pp.savefig(fig)
pp.close()


# Add Page numbers
# https://stackoverflow.com/questions/25164871/how-to-add-page-numbers-to-pdf-file-using-python-and-matplotlib


# Add table of contents
# https://stackoverflow.com/questions/6157456/create-outlines-toc-for-existing-pdf-in-python

# How to add an index page

# https://code.tutsplus.com/tutorials/how-to-work-with-pdf-documents-using-python--cms-25726

# How to muck around with PDFs:
# https://automatetheboringstuff.com/chapter13/

if __name__ == "__main__":
    logging.info("This is an index page")
