import argparse
import os
from PyPDF3 import PdfFileWriter as pWrite, PdfFileReader
from PyPDF3.pdf import PageObject
from decimal import Decimal


def two_merge(page1,page2,spine_spc):
    total_width = page1.mediaBox.upperRight[0] + page2.mediaBox.upperRight[0]
    total_width += (Decimal(spine_spc)*total_width)/100
    total_height = max([page1.mediaBox.upperRight[1], page2.mediaBox.upperRight[1]])
    second_width = float(total_width)-float(page1.mediaBox.upperRight[0])
    new_page = PageObject.createBlankPage(None, total_width, total_height)
    new_page.mergePage(page1)
    new_page.mergeTranslatedPage(page2, second_width, 0)
    return new_page
    
    
def temp_pdf(pdf, width, height):
    num_pages = pdf.getNumPages()
    okay = pWrite()
    new_page = PageObject.createBlankPage(None, width, height)
    okay.addPage(new_page)
    i=0
    while i < num_pages:
        page=pdf.getPage(i)
        okay.addPage(page)
        i+=1
    pdf_out = open("temp.pdf", 'wb')
    okay.write(pdf_out)
    pdf_out.close()
    
    
def pdf_split(file,sec_size,out, page_shift,spine_spc):
    pdf_open = PdfFileReader(open(file, "rb"), strict=False)
    num_pages = pdf_open.getNumPages()
    okay = pWrite()
    if num_pages%sec_size != 0:
        num_pages = num_pages + (sec_size - (num_pages%sec_size))
    page = pdf_open.getPage(0)
    total_width = page.mediaBox.upperRight[0]
    total_height = page.mediaBox.upperRight[1]
    i = 1
    if page_shift:
        num_pages+=1
        temp_pdf(pdf_open,total_width, total_height)
        close_for_erase = open("temp.pdf", "rb")
        pdf_in = PdfFileReader(close_for_erase, strict=False)
        erase = True
    else:
        pdf_in = pdf_open
        erase = False
    j = 1
    while j <= (num_pages/sec_size):
        while i <= sec_size/2:
            if i%2 != 0:
                try:
                    page1 = pdf_in.getPage(((j*sec_size)-(i-1))-1)
                except:
                    page1 = PageObject.createBlankPage(None, total_width, total_height)
                try:
                    page2 = pdf_in.getPage((i+((j-1)*sec_size))-1)
                except:
                    page2 = PageObject.createBlankPage(None, total_width, total_height)
            else:
                try:
                    page2 = pdf_in.getPage(((j*sec_size)-(i-1))-1)
                except:
                    page2 = PageObject.createBlankPage(None, total_width, total_height)
                try:
                    page1 = pdf_in.getPage((i+((j-1)*sec_size))-1)
                except:
                    page1 = PageObject.createBlankPage(None, total_width, total_height)
            new_page = two_merge(page1,page2,spine_spc)
            okay.addPage(new_page)
            i+=1
        i=1
        j+=1
    pdf_out = open(out, 'wb')
    okay.write(pdf_out)
    if erase:
        close_for_erase.close()
        os.remove("temp.pdf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make Booklet.')
    parser.add_argument('-s', '--secsz', dest='sec_size',
                                nargs = 1,
                                default = [16],
                                type = int,
                                required = False,
                                help = 'Section size.  Must divisible by 4.')
    parser.add_argument('-o','--output',dest='outputfile',
                                nargs = 1,
                                default = 'New_PDF.pdf',
                                type = str,
                                required = False,
                                help = 'Filename/path for new PDF file.')
    parser.add_argument('-b', '--blnkpg', dest='page_shift',
                                action = 'store_const',
                                const = True, default = False,
                                help = 'Add a blank page at the start.')
    parser.add_argument('-d', '--div', dest='spine_spc',
                                nargs = 1,
                                default = [0.],
                                type = float,
                                required = False,
                                help = 'Add space in the spine (percentage of width).')
    parser.add_argument('data', type=str, nargs='*', default='./*.pdf',
                                help='PDF File.')
    parse_args = parser.parse_args()
    if parse_args.sec_size[0]%4 != 0:
        parse_args.sec_size[0] = 16
        print("Bad section size; defaulting to 16")
    try:
        pdf_split(parse_args.data[0],parse_args.sec_size[0], parse_args.outputfile[:],parse_args.page_shift,parse_args.spine_spc[0])
        print("Completed successfully!")
    except:
        print("Something went wrong.")
        
    