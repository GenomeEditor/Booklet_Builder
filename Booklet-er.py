import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial import ConvexHull
from PIL import Image
from pathlib import Path
import argparse
import os
import subprocess
import re
from PyPDF3 import PdfFileWriter as pWrite, PdfFileReader
from PyPDF3.pdf import PageObject

def two_merge(page1,page2):
    total_width = page1.mediaBox.upperRight[0] + page2.mediaBox.upperRight[0]
    total_height = max([page1.mediaBox.upperRight[1], page2.mediaBox.upperRight[1]])
    new_page = PageObject.createBlankPage(None, total_width, total_height)
    new_page.mergePage(page1)
    new_page.mergeTranslatedPage(page2, page1.mediaBox.upperRight[0], 0)
    return new_page
    
def pdf_split(file,sec_size,out):
    pdf_in = PdfFileReader(open(file, "rb"), strict=False)
    num_pages = pdf_in.getNumPages()
    okay = pWrite()
    if num_pages%sec_size != 0:
        num_pages = num_pages + (sec_size - (num_pages%sec_size))
    page = pdf_in.getPage(0)
    total_width = page.mediaBox.upperRight[0]
    total_height = page.mediaBox.upperRight[1]
    i = 1
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
            new_page = two_merge(page1,page2)
            okay.addPage(new_page)
            i+=1
        i=1
        j+=1
    pdf_out = open(out, 'wb')
    okay.write(pdf_out)

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
    parser.add_argument('data', type=str, nargs='*', default='./*.pdf',
						help='PDF File.')
    parse_args = parser.parse_args()
    datapaths = list(map(Path, parse_args.data))
    print(datapaths)
    if parse_args.sec_size[0]%4 != 0:
        parse_args.sec_size[0] = 16
        print("Bad section size; defaulting to 16")
    pdf_split(parse_args.data[0],parse_args.sec_size[0], parse_args.outputfile[:])
    