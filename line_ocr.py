import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
try:
    from pytesseract import pytesseract as pyocr
    pyocr.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
except ImportError:
    print('Please install pytesseract first, which depends on the following libs:')
    print('http://www.lfd.uci.edu/~gohlke/pythonlibs/#pil')
    print('http://code.google.com/p/tesseract-ocr/')
    raise SystemExit
import numpy as np
import re
import xlsxwriter
import os, sys, stat, errno
from PIL import Image
# from scipy import ndimage
from skimage import measure, morphology

from PyQt5.QtWidgets import QApplication, QProgressBar, QFileDialog, QLabel
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QThread


class OCR(object):
    def __init__(self):
        self.th_bw = 235
        self.rect = [256, 918, 1653, 1043] # [916, 256, 1035, 1654]
        self.dilate_then_mask = [4, 2, 50, 4]  # imdilate times;xor image 1, 2; threshold of a letter; number of pixel to retain as a letter
        # self.re_pos1 = re.compile('(?<=\()[1-9]\d*.\d*|0\.\d*[1-9]\d*')
        # self.re_pos2 = re.compile('([1-9]\d*.\d*|0\.\d*[1-9]\d*)(?=,\n)')
        # self.re_dist = re.compile('(?<=D)([1-9]\d*.\d*|0\.\d*[1-9]\d*)(?=m)')
        self.re_pos1 = re.compile('\(\s*([1-9]\d*.\d*|0\.\d*[1-9]\d*),')
        self.re_pos2 = re.compile('([1-9]\d*.\d*|0\.\d*[1-9]\d*)\s*,\n')
        self.re_dist = re.compile('D\s*([1-9]\d*.\d*|0\.\d*[1-9]\d*)\s*m')

    def ocr(self, im_path):
        im = Image.open(im_path)  # open colour image
        im = im.crop(self.rect)
        im = im.convert('L')  # convert image to gray
        im = np.array(im)

        # binary image mask
        im_binary = np.where(im > self.th_bw, 255, 0)
        labels = measure.label(im_binary)
        lists = measure.regionprops(labels)
        # print('number of regions is %d' % (len(lists)))
        for l in range(len(lists)):
            # print("------------------------------")
            # print(im_binary.shape)
            # print(lists[l].image.shape)
            # print(lists[l].coords)

            if lists[l].area < self.dilate_then_mask[3]:
                im_binary[lists[l].coords[:, 0], lists[l].coords[:, 1]] = 0
                continue
            im_dilated = np.zeros(im_binary.shape, dtype=bool)
            # print(im_dilated[0].shape)
            im_dilated[lists[l].coords[:, 0], lists[l].coords[:, 1]] = 1
            # dilate to find the black contour of a letter
            im_origin = im_dilated
            im_xor_1 = []
            # print('im_begin %d' % np.sum(np.sum(im_dilated)))
            for i in range(self.dilate_then_mask[0]):
                # im_dilated = ndimage.binary_dilation(im_dilated)
                im_dilated = morphology.binary_dilation(im_dilated)
                if i == self.dilate_then_mask[1]-1:
                    im_xor_1 = im_dilated
            # print('im_xor_1 %d' % np.sum(np.sum(im_xor_1)))
            # print('im_xor_2 %d' % np.sum(np.sum(im_dilated)))
            im_dilated = np.logical_xor(im_dilated, im_xor_1)
            # print(np.sum(sum(im_dilated)))
            if np.mean(im[im_dilated]) > self.dilate_then_mask[2]:
                im_binary[im_origin] = 0

            # if l == 2:
            #     raise

        im_binary = Image.fromarray(np.uint8(im_binary))
        text = pyocr.image_to_string(im_binary, lang='eng')
        return text

    def get_pos_and_dist(self, text):
        pos1 = self.re_pos1.findall(text)
        pos2 = self.re_pos2.findall(text)
        dist = self.re_dist.findall(text)
        if not all([pos1, pos2, dist]):
            return [[], [], []]
        if not re.findall(r'\.', dist[0]):
            dist[0] = str(float(dist[0])/100)
        if not re.findall(r'\.', pos1[0]):
            pos1[0] = str(float(pos1[0])/10000)
        if not re.findall(r'\.', pos2[0]):
            pos2[0] = str(float(pos2[0])/10000)
        return [pos1[0], pos2[0], dist[0]]


def walk_path(top, callback):

    for f in os.listdir(top):

        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[stat.ST_MODE]

        if stat.S_ISDIR(mode):
            walk_path(pathname, callback)
        elif stat.S_ISREG(mode):
            callback(pathname)
        else:
            print('Skipping %s' % pathname)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5 (except OSError, exc: for Python <2.5)
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def parse_argument():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_dir',
        help="Origin image directory.",
        default=''  # os.curdir
    )
    # parser.add_argument(
    #     '--output_dir',
    #     help="Output image directory.",
    #     default=''
    # )
    # parser.add_argument(
    #     '--cartoon',
    #     help="If it is for cartoon",
    #     dest='cartoon',
    #     action='store_true'
    # )
    args = parser.parse_args()
    return args


class WorkThread(QThread):
    nextImageSignal = pyqtSignal(int)
    scanImageDoneSignal = pyqtSignal(int)
    IMAGE_SUFFIX = {'jpg', 'jepg', 'bmp', 'png'}  # supported image suffix (lower case)

    def __int__(self, parent=None):
        super(WorkThread, self).__init__()

    def init(self, input_dir):
        # init working data structure
        self.image_path_name_list = []
        #print("self.image_path_name_list is:")
        #print(self.image_path_name_list)
        self.num_image = 0
        self.input_dir = input_dir
        self.working = True
        self.ocr = OCR()
        self.workbook = xlsxwriter.Workbook(os.path.join(input_dir, 'result.xlsx'))
        self.worksheet = self.workbook.add_worksheet()
        self.worksheet.set_column("A:A", 20)
        self.write_excel()

    def __del__(self):
        self.working = False
        self.workbook.close()
        self.wait()

    def write_excel(self, row=0, path='', position1=0, position2=0, distance=0):
        if row == 0:
            self.worksheet.write(row, 0, '图片文件名')
            self.worksheet.write(row, 1, '纬度')
            self.worksheet.write(row, 2, '经度')
            self.worksheet.write(row, 3, '距离')
        elif path and not all([position1, position2, distance]):
            self.worksheet.write(row, 0, path)
        else:
            self.worksheet.write(row, 0, path)
            self.worksheet.write(row, 1, position1)
            self.worksheet.write(row, 2, position2)
            self.worksheet.write(row, 3, distance)

    def set_path(self, input_dir):
        self.input_dir = input_dir

    def run(self):
        if self.input_dir == '':
            raise('Specify image path before scan.')

        # set path and scan image
        self.scan()
        if len(self.image_path_name_list) < 1:
            print("No image file is found in %s, please select path again." % self.input_dir)
        else:
            print('input dir is: ' + self.input_dir)
            print('Scanned %d image list:' % len(self.image_path_name_list))
        self.scanImageDoneSignal.emit(self.num_image)

        row = 1
        for j in range(self.num_image):
            text = self.ocr.ocr(self.image_path_name_list[j])
            print('image %d: %s' % (j, os.path.basename(self.image_path_name_list[j])))
            print(text)
            if text is None:
                continue
            results = self.ocr.get_pos_and_dist(text)
            # if not all(results):
            #     continue
            self.write_excel(row, os.path.basename(self.image_path_name_list[j]), results[0], results[1], results[2])
            row += 1
            self.nextImageSignal.emit(j)

    def scan(self):
        walk_path(self.input_dir, self.get_image_path)
        self.num_image = len(self.image_path_name_list)

    def get_image_path(self, filename):
        suffix = os.path.splitext(filename)[1][1:].lower()
        if suffix in self.IMAGE_SUFFIX:
            self.image_path_name_list.append(filename)


class ProgressBar(QtWidgets.QWidget):

    def __init__(self, input_dir, parent=None):

        QtWidgets.QWidget.__init__(self)

        self.setGeometry(500, 300, 250, 75)
        self.setWindowTitle('ProgressBar')
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)
        self.pbar.hide()

        self.step = 0

        if '' == input_dir or not os.path.isdir(input_dir):
            input_dir = str(QFileDialog.getExistingDirectory())
        self.input_dir = os.path.abspath(input_dir)
        self.lab = QLabel("Scanning...", self)
        self.lab.move(40, 40)
        self.lab_path = QLabel(input_dir, self)
        self.lab.move(40, 10)

        self.worker = WorkThread()
        self.worker.init(input_dir)
        self.worker.nextImageSignal.connect(self.next_image)
        self.worker.scanImageDoneSignal.connect(self.on_start_ocr)
        self.worker.start()

    def on_start_ocr(self, num):
        # print("Number of images is: %d" %num)
        self.lab.hide()
        self.pbar.show()
        self.num_image = num

    def next_image(self, id):
        # print('next_image %d' %id)
        self.pbar.setValue((id+1)/self.num_image*100)
        if id+1 == self.num_image:
            self.close()


def main():
    args = parse_argument()
    app = QApplication(sys.argv)
    qb = ProgressBar(args.input_dir)
    qb.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
