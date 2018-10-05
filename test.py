import sys
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
try:
    from pytesseract import pytesseract as pyocr
except ImportError:
    print('Please install pytesseract first, which depends on the following libs:')
    print ('http://www.lfd.uci.edu/~gohlke/pythonlibs/#pil')
    print ('http://code.google.com/p/tesseract-ocr/')
    raise SystemExit
from PIL import Image
import numpy as np
import re
#from scipy.misc import imsave
#from PIL import ImageFilter

im_path = 'test2.jpg'
im = Image.open(im_path) # open colour image
im = im.convert('L') # convert image to gray
im = np.array(im)
im = np.where(im > 235, 255, 0)
im = Image.fromarray(np.uint8(im))

#im = im.filter(ImageFilter.SMOOTH);
#imsave('result.png', im)
##im.save('result.png')

text = pyocr.image_to_string(im, lang='eng')
print(text)

re_pos1 = re.compile('(?<=\()[1-9]\d*.\d*|0\.\d*[1-9]\d*')
re_pos2 = re.compile('([1-9]\d*.\d*|0\.\d*[1-9]\d*)(?=,\n)')
re_dist = re.compile('(?<=D\s)([1-9]\d*.\d*|0\.\d*[1-9]\d*)(?=m)')
pos1 = re_pos1.findall(text)[0]
pos2 = re_pos2.findall(text)[0]
dist = re_dist.findall(text)[0]


print(pos1)
print(pos2)
print(dist)

import xlsxwriter
workbook=xlsxwriter.Workbook('test.xlsx')
worksheet=workbook.add_worksheet()
worksheet.set_column("A:A",20)

def writeExcel(row=0, path='图片文件名', position1='纬度', position2='经度', distance='距离'):
    worksheet.write(row, 0, path)
    worksheet.write(row, 1, position1)
    worksheet.write(row, 2, position2)
    worksheet.write(row, 3, distance)


row = 1
writeExcel(row=row, path='test2.jpg', position1=pos1,position2=pos2, distance=dist)

workbook.close()