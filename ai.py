from PIL import Image
import cv2
from keras.models import load_model
import os
import numpy as np
import shutil
import stat
import etc
from PyQt5 import QtCore, QtWidgets, QtGui
from functools import partial

globalfile = ''

HEX_LIST=['0x00','0x17','0x20','0x2F','0x6D','0x92','0xA4','0xD4','0xE8','0x2B',
          '0x35','0xB0','0xB8','0xC2','0xD8','0x01','0x02','0x03','0xC0','0xFE',
          '0xFF','0x73','0x75','0x61','0x6E','0x6F','0x70','0x24','0x2A','0x48',
          '0x49','0x4A','0x52','0x54','0x55','0x8E','0x95','0xA5','0xA9','0xAA',
          '0x05','0x08','0x10','0x15','0x18','0x1D','0x23','0x25','0x2D','0x4B',
          '0xA0','0xA8','0xAD','0xB5','0xC4','0xC8','0xD0','0xD2','0xDB','0xE2',
          '0xE7','0xEB','0xEF','0x7F','0x80','0x91','0xBF','0x04','0xFC','0xFD',
          '0xBC','0xDC','0xE1','0xF8','0x14','0x1B','0x34','0x40','0x5B','0x5C',
          '0x5E','0x5F','0x7C','0x7E','0x8B','0xAB','0xAE','0xAF','0xB6','0xB7'] 

def check(byte):
    if len(byte) != 0:
        return ord(byte)
    else:
        return 0
# 모델 입력 층에 들어가기전 사전 작업
def Dataization(data):
    image_w = 30
    image_h = 90
    nparr = cv2.cvtColor(data,cv2.COLOR_GRAY2BGR)
    nparr = cv2.resize(nparr, None, fx=image_w / nparr.shape[1], fy=image_h / nparr.shape[0])
    return (nparr / 256)

def del_rw(action, name, exc):
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)

# gray scale로 변환
def createGreyScaleImageSpecificWith(dataSet):
    image = Image.new('L', (30, 90))
    image.putdata(dataSet)
    return np.array(image)


#메시지 알람 함수
def alertDialog(text=""):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setText(text);
    msgBox.exec()

#hexView를 보여주는 함수
def hexView(count):
    layout = QtWidgets.QVBoxLayout()
    scroll = QtWidgets.QScrollArea()
    toplabel = QtWidgets.QLabel()
    toplabeltext = 'offset(h)'.ljust(13)
    for x in range(16):
        toplabeltext += '{0:02X} '.format(x)
    toplabeltext += '  Decoded Text'.ljust(8)
    label = QtWidgets.QLabel()
    dialog = QtWidgets.QDialog()
    dialog.resize(850, 600)
    with open(globalfile, "rb") as f:
        f.seek(count*4096)
        filebyte = f.read(4096)
    toplabel.setFont(QtGui.QFont('Courier', 10))
    toplabel.setText(toplabeltext)
    label.setFont(QtGui.QFont('Courier', 10))
    label.setText(etc.hexViwer(filebyte,count))
    scroll.setWidget(label)
    layout.addWidget(toplabel)
    layout.addWidget(scroll)
    dialog.setWindowTitle("hexViewer")
    dialog.setLayout(layout)
    dialog.exec()

#지정한 위치의 데이터를 다운로드하는 함수
def downloadData(count=0, file_type=""):
    with open(globalfile, "rb") as f:
        f.seek(count*4096)
        filebyte = f.read(4096)
        path = os.path.join(os.environ["HOMEPATH"], "Desktop")
        with open(path+"/0x{0:02X} - 0x{1:02X} {2}".format(count*4096, (count+1)*4096 , file_type),"wb") as savefile:
            savefile.write(filebyte)
    alertDialog("0x{0:02X} - 0x{1:02X} download complete!".format(count * 4096, (count + 1) * 4096))


# scan시 실행하는 함수
def maintest(filename, unallocated, png_frag_list, moduletree, Qcore):
    global globalfile
    globalfile = filename
    topH264 = QtWidgets.QTreeWidgetItem()
    topH264.setText(0, "h264")
    topH264.setText(1, "-")
    topJpg = QtWidgets.QTreeWidgetItem()
    topJpg.setText(0, "jpg")
    topJpg.setText(1, "-")
    topPng = QtWidgets.QTreeWidgetItem()
    topPng.setText(0, "png")
    topPng.setText(1, "-")
    topWav = QtWidgets.QTreeWidgetItem()
    topWav.setText(0, "wav")
    topWav.setText(1, "-")
    topExe = QtWidgets.QTreeWidgetItem()
    topExe.setText(0, "exe")
    topExe.setText(1, "-")
    topHwp = QtWidgets.QTreeWidgetItem()
    topHwp.setText(0, "hwp")
    topHwp.setText(1, "-")
    
    moduletree.addTopLevelItem(topH264)
    moduletree.addTopLevelItem(topJpg)
    moduletree.addTopLevelItem(topPng)
    moduletree.addTopLevelItem(topWav)
    moduletree.addTopLevelItem(topExe)
    moduletree.addTopLevelItem(topHwp)


    png_predit_list = []
    path = os.path.dirname(os.path.abspath(__file__))
    path += '/model.h5'
    model = load_model(path)
    cate = ["exe", "h264", "jpg", "png", "wav", "hwp"]

    jpg_count = 0
    png_count = 0
    wav_count = 0
    h264_count = 0
    hwp_count = 0
    exe_count = 0
    
    count = 0
    # file split
    with open(globalfile, "rb") as f:
        for x in unallocated:
            start = x[0]
            end = x[1]
            f.seek(start * 4096)
            for y in range(end - start):
                Qcore.processEvents()
                test = []
                gray = []
                check_offset = f.tell() // 4096
                if (check_offset) in png_frag_list:
                    png_frag_list.remove(check_offset)
                    continue
                file_byte = f.read(4096)
                if not file_byte or len(file_byte) < 4096:
                    break
                #데이터 변화해줘야 하는 부분
                lst = [0 for _ in range(256)]
                for x in file_byte:
                    lst[x] += 1

                if lst[0] == 4096:
                    continue

                for x in HEX_LIST:
                    input_value = lst[int(x,16)]
                    if input_value >= 255:
                        input_value = 255
                    for yy in range(30):
                        gray.append(ord(input_value.to_bytes(1, byteorder='big')))
                
                test.append(Dataization(createGreyScaleImageSpecificWith(gray)))
                test = np.array(test)
                predict = model.predict_classes(test)
                predict2 = model.predict(test)

                for i in range(len(test)):                 
                    #확장자가 확인이 되면 UI에 추가를 위한 로직
                    if predict[i] == 0:
                        exe_item = QtWidgets.QTreeWidgetItem(topExe)
                        exe_push_button = QtWidgets.QPushButton("exe")
                        exe_push_button.clicked.connect(partial(downloadData, check_offset, "exe"))
                        moduletree.setItemWidget(exe_item, 0, exe_push_button)
                        exe_item.setText(1, "0x{0:02X} - 0x{1:02X}".format(check_offset * 4096, (check_offset + 1) * 4096))
                        exe_item.setText(2, "{0}%".format(round(predict2[0][0] * 100, 2)))
                        exe_hex_button = QtWidgets.QPushButton(
                            'hex : 0x{0:02X} 0x{1:02X} 0x{2:02X} 0x{3:02X} ...'.format(file_byte[0], file_byte[1], file_byte[2], file_byte[3]))
                        exe_hex_button.clicked.connect(partial(hexView, check_offset))
                        moduletree.setItemWidget(exe_item, 3, exe_hex_button)
                        exe_count += 1
                        topExe.setText(1, str(exe_count))
                        topExe.addChild(exe_item)
                    elif predict[i] == 1:
                        h264_item = QtWidgets.QTreeWidgetItem(topH264)
                        h264_push_button = QtWidgets.QPushButton("h264")
                        h264_push_button.clicked.connect(partial(downloadData, check_offset, "h264"))
                        moduletree.setItemWidget(h264_item, 0, h264_push_button)
                        h264_item.setText(1, "0x{0:02X} - 0x{1:02X}".format(check_offset * 4096, (check_offset + 1) * 4096))
                        h264_item.setText(2, "{0}%".format(round(predict2[0][1] * 100, 2)))
                        h264_hex_button = QtWidgets.QPushButton(
                            'hex : 0x{0:02X} 0x{1:02X} 0x{2:02X} 0x{3:02X} ...'.format(file_byte[0], file_byte[1], file_byte[2], file_byte[3]))
                        h264_hex_button.clicked.connect(partial(hexView, check_offset))
                        moduletree.setItemWidget(h264_item, 3, h264_hex_button)
                        h264_count += 1
                        topH264.setText(1, str(h264_count))
                        topH264.addChild(h264_item)
                    elif predict[i] == 2:
                        jpg_item = QtWidgets.QTreeWidgetItem(topJpg)
                        jpg_push_button = QtWidgets.QPushButton("jpg")
                        jpg_push_button.clicked.connect(partial(downloadData, check_offset, "jpg"))
                        moduletree.setItemWidget(jpg_item, 0, jpg_push_button)
                        jpg_item.setText(1, "0x{0:02X} - 0x{1:02X}".format(check_offset * 4096, (check_offset + 1) * 4096))
                        jpg_item.setText(2,"{0}%".format(round(predict2[0][2]*100,2)))
                        jpg_hex_button = QtWidgets.QPushButton(
                            'hex : 0x{0:02X} 0x{1:02X} 0x{2:02X} 0x{3:02X} ...'.format(file_byte[0], file_byte[1], file_byte[2], file_byte[3]))
                        jpg_hex_button.clicked.connect(partial(hexView, check_offset))
                        moduletree.setItemWidget(jpg_item, 3, jpg_hex_button)
                        jpg_count+=1
                        topJpg.setText(1, str(jpg_count))
                        topJpg.addChild(jpg_item)
                    elif predict[i] == 3:
                        png_item = QtWidgets.QTreeWidgetItem(topPng)
                        png_push_button = QtWidgets.QPushButton("png")
                        png_push_button.clicked.connect(partial(downloadData, check_offset, "png"))
                        moduletree.setItemWidget(png_item, 0, png_push_button)
                        png_item.setText(1, "0x{0:02X} - 0x{1:02X}".format(check_offset * 4096, (check_offset + 1) * 4096))
                        png_item.setText(2, "{0}%".format(round(predict2[0][3] * 100, 2)))
                        png_hex_button = QtWidgets.QPushButton(
                            'hex : 0x{0:02X} 0x{1:02X} 0x{2:02X} 0x{3:02X} ...'.format(file_byte[0], file_byte[1], file_byte[2], file_byte[3]))
                        png_hex_button.clicked.connect(partial(hexView, check_offset))
                        moduletree.setItemWidget(png_item, 3, png_hex_button)
                        png_count += 1
                        topPng.setText(1, str(png_count))
                        topPng.addChild(png_item)
                        png_predit_list.append(f.tell()-4096)
                    elif predict[i] == 3:
                        wav_item = QtWidgets.QTreeWidgetItem(topWav)
                        wav_push_button = QtWidgets.QPushButton("wav")
                        wav_push_button.clicked.connect(partial(downloadData, check_offset, "wav"))
                        moduletree.setItemWidget(wav_item, 0, wav_push_button)
                        wav_item.setText(1, "0x{0:02X} - 0x{1:02X}".format(check_offset * 4096, (check_offset + 1) * 4096))
                        wav_item.setText(2, "{0}%".format(round(predict2[0][4] * 100, 2)))
                        wav_hex_button = QtWidgets.QPushButton(
                            'hex : 0x{0:02X} 0x{1:02X} 0x{2:02X} 0x{3:02X} ...'.format(file_byte[0], file_byte[1], file_byte[2], file_byte[3]))
                        wav_hex_button.clicked.connect(partial(hexView, check_offset))
                        moduletree.setItemWidget(wav_item, 3, wav_hex_button)
                        wav_count += 1
                        topWav.setText(1, str(wav_count))
                        topWav.addChild(wav_item)
                    elif predict[i] == 4:
                        hwp_item = QtWidgets.QTreeWidgetItem(topHwp)
                        hwp_push_button = QtWidgets.QPushButton("hwp")
                        hwp_push_button.clicked.connect(partial(downloadData, check_offset, "hwp"))
                        moduletree.setItemWidget(hwp_item, 0, hwp_push_button)
                        hwp_item.setText(1, "0x{0:02X} - 0x{1:02X}".format(check_offset * 4096, (check_offset + 1) * 4096))
                        hwp_item.setText(2, "{0}%".format(round(predict2[0][5] * 100, 2)))
                        hwp_hex_button = QtWidgets.QPushButton(
                            'hex : 0x{0:02X} 0x{1:02X} 0x{2:02X} 0x{3:02X} ...'.format(file_byte[0], file_byte[1], file_byte[2], file_byte[3]))
                        hwp_hex_button.clicked.connect(partial(hexView, check_offset))
                        moduletree.setItemWidget(hwp_item, 3, hwp_hex_button)
                        hwp_count += 1
                        topHwp.setText(1, str(hwp_count))
                        topHwp.addChild(hwp_item)
                        
                    count += 1

    return png_predit_list

