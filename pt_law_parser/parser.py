from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

from pt_law_parser.converter import LAOrganizer, LawConverter


def parse_document(file_name):

    rsrcmgr = PDFResourceManager(caching=True)

    fp = file(file_name, 'rb')

    device = LawConverter(rsrcmgr, laparams=LAOrganizer())

    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
    fp.close()

    return device
