# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import os
import ntfs
import checkPng
import ai
import assemblePng

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 620)
        MainWindow.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        icon = QtGui.QIcon()
        path = os.path.dirname(os.path.abspath(__file__))
        icon_path = path + '/bob.bmp'
        icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.tabwidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabwidget.setGeometry(0,0,800,600)
        #################################################################################################################
        #poc 부분
        self.pngtabwidget = QtWidgets.QWidget()
        self.tabwidget.addTab(self.pngtabwidget,"pngtab")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.pngtabwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 771, 531))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.mainLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.openButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.openButton.setObjectName("Open Disk")
        self.openButton.setFixedSize(QtCore.QSize(150,50))
        self.horizontalLayout.addWidget(self.openButton)
        self.open_scan = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.arrowimage_path = path + "/arrow.png"
        self.arrowimage = QtGui.QPixmap(self.arrowimage_path)
        self.open_scan.setPixmap(self.arrowimage.scaled(40,40))
        self.open_scan.setFixedHeight(40)
        self.open_scan.setFixedWidth(40)
        self.horizontalLayout.addWidget(self.open_scan)
        self.scanButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.scanButton.setObjectName("Scan Image")
        self.scanButton.setFixedSize(QtCore.QSize(150,50))
        self.horizontalLayout.addWidget(self.scanButton)
        self.scan_recovery = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.scan_recovery.setPixmap(self.arrowimage.scaled(40,40))
        self.scan_recovery.setFixedHeight(40)
        self.scan_recovery.setFixedWidth(40)
        self.horizontalLayout.addWidget(self.scan_recovery)
        self.RecoveryButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.RecoveryButton.setObjectName("Recovery Image")
        self.RecoveryButton.setFixedSize(QtCore.QSize(150,50))
        self.horizontalLayout.addWidget(self.RecoveryButton)
        self.mainLayout.addLayout(self.horizontalLayout)

        self.disklabel = QtWidgets.QLabel()
        self.disklabel.setText("Disk : ")
        self.font = QtGui.QFont()
        self.font.setPointSize(15)
        self.disklabel.setFont(self.font)
        self.mainLayout.addWidget(self.disklabel)

        self.treeWidget = QtWidgets.QTreeWidget(self.verticalLayoutWidget)
        self.treeWidget.setObjectName("treeWidget")
        self.mainLayout.addWidget(self.treeWidget)

        self.graphicsView = QtWidgets.QGraphicsView(self.verticalLayoutWidget)
        self.graphicsView.setObjectName("graphicsView")
        self.mainLayout.addWidget(self.graphicsView)
                
        self.DownloadButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.DownloadButton.setObjectName("DownloadButton")
        self.DownloadButton.setFixedSize(QtCore.QSize(150,50))
        self.mainLayout.addWidget(self.DownloadButton, alignment=QtCore.Qt.AlignCenter)


        #################################################################################################################
        #모듈 부분
        self.modulewidget = QtWidgets.QWidget()
        self.tabwidget.addTab(self.modulewidget,"moduletab")
        self.modulehorizontalLayout = QtWidgets.QVBoxLayout(self.modulewidget)

        #모듈 tree
        self.moduletree = QtWidgets.QTreeWidget()
        self.moduletree.setObjectName("treeWidget")
        self.modulehorizontalLayout.addWidget(self.moduletree)
        
       #gif 부분
        self.testLabel = QtWidgets.QLabel(self.centralwidget)
        self.testLabel.setGeometry(QtCore.QRect((MainWindow.width() / 2) - 110 ,(MainWindow.height() / 2) - 100, 150, 150))
        self.testLabel.setObjectName("label")
        movie_path = path + "/down_loading.gif"
        self.movie = QtGui.QMovie(movie_path)
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.testLabel.setMovie(self.movie)
        self.testLabel.hide()
        self.Qcore = QtWidgets.QApplication.instance()

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "확정이 >_<"))
        self.openButton.setText(_translate("MainWindow", "Open Disk"))
        self.openButton.clicked.connect(partial(self.OnOpenDocument,"open",MainWindow))
        self.scanButton.setText(_translate("MainWindow", "Scan Image"))
        self.scanButton.clicked.connect(self.scan)
        self.scanButton.setDisabled(True)
        self.RecoveryButton.setText(_translate("MainWindow", "Recover Fragment"))
        self.RecoveryButton.setDisabled(True)
        self.treeWidget.headerItem().setText(0,'')
        self.treeWidget.setColumnWidth(0,70)
        self.treeWidget.headerItem().setText(1, "Scaned Image")
        self.treeWidget.setColumnWidth(1,300)
        self.treeWidget.headerItem().setText(2, "size")
        self.treeWidget.headerItem().setText(3, "state")
        self.treeWidget.headerItem().setText(4, "view")

        self.DownloadButton.setText(_translate("MainWindow", "Download"))
        self.DownloadButton.clicked.connect(self.downloadData)

        self.moduletree.headerItem().setText(0, _translate("MainWindow", "type"))
        self.moduletree.headerItem().setText(1, _translate("MainWindow", "offset"))
        self.moduletree.setColumnWidth(1,200)
        self.moduletree.headerItem().setText(2, _translate("MainWindow", "acc"))
        self.moduletree.headerItem().setText(3, _translate("MainWindow", "hex view"))
       

    # 파일 여는 함수
    def OnOpenDocument(self, text="open",MainWindow=None):
        # 다른 파일을 열었을 때 scan 버튼 활성화
        qfd = QtWidgets.QFileDialog()
        path = os.getenv('HOME')
        file_filter = "all(*)"
        if text == "open":
            self.filename = (qfd.getOpenFileName(None, "title", path, file_filter))[0]
            if self.filename == '':
                self.disklabel.setText("Disk : ")
                self.scanButton.setDisabled(True)
                return
            self.disklabel.setText("Disk : {0}".format(self.filename))
            self.scanButton.setEnabled(True)
            self.treeWidget.clear()  
        elif text == "save":
             self.downloadEdit.setText(QFileDialog.getExistingDirectory(qfd, "title", path, QFileDialog.ShowDirsOnly))

    def scan(self):
        self.testLabel.show()
        self.movie.start()

        self.treeWidget.clear()
        unallocated = ntfs.unallocatedList(self.filename, self.Qcore)
        if unallocated == -1:
            self.alertDialog("Plz insert ntfs file")
            self.movie.stop()
            self.testLabel.hide()
            return
        ihdr_list, idat_list, png_frag_list, perfect_png_list, fragment_png_list = checkPng.classifyPng(self.filename, unallocated, self.Qcore)

        for x in perfect_png_list:
           perfect_png_item = QtWidgets.QTreeWidgetItem(self.treeWidget)
          # perfect_png_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
           perfect_png_item.setCheckState(0,QtCore.Qt.Unchecked)
           perfect_png_item.setText(1,'perfect_png')
           perfect_png_item.setText(2,'{0} byte'.format(len(x)))
           perfect_png_item.setText(3,'pass')
           perfect_png_button = QtWidgets.QPushButton("view")
           perfect_png_button.setFixedSize(80,30)
           perfect_png_button.clicked.connect(partial(self.viewhandler, x))
           self.treeWidget.setItemWidget(perfect_png_item, 4, perfect_png_button)
           perfect_png_item.setData(4, QtCore.Qt.UserRole, QtCore.QVariant(x))
           self.treeWidget.addTopLevelItem(perfect_png_item)

        for x in fragment_png_list:
           fragment_png_item = QtWidgets.QTreeWidgetItem(self.treeWidget)
          # fragment_png_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
           fragment_png_item.setCheckState(0,QtCore.Qt.Unchecked)
           fragment_png_item.setText(1, 'fragment_png')
           fragment_png_item.setText(2, 'Unknown')
           fragment_png_item.setText(3, 'ready')
           fragment_png_button = QtWidgets.QPushButton("view")
           fragment_png_button .setFixedSize(80,30)
           fragment_png_button.setDisabled(True)
           fragment_png_item.setData(4, QtCore.Qt.UserRole, QtCore.QVariant(x))
           fragment_png_button.clicked.connect(partial(self.viewhandler, x))
           self.treeWidget.setItemWidget(fragment_png_item, 4, fragment_png_button)
           self.treeWidget.addTopLevelItem(fragment_png_item)


        self.RecoveryButton.setEnabled(True)
        self.RecoveryButton.clicked.connect(partial(self.recovery, unallocated, ihdr_list, idat_list, png_frag_list, perfect_png_list))
        self.movie.stop()
        self.testLabel.hide()
        self.alertDialog("scan completed")


    def viewhandler(self, data):
        scene = QtWidgets.QGraphicsScene()
        pixmap= QtGui.QPixmap()
        self.graphicsView.setScene(scene)
        pixmap.loadFromData(data)
        self.graphicsView.fitInView(scene.addPixmap(pixmap), QtCore.Qt.KeepAspectRatio)
    
    def recovery(self, unallocated, ihdr_list, idat_list, png_frag_list, perfect_png_list):
        self.testLabel.show()
        self.movie.start()

        pnglist = ai.maintest(self.filename, unallocated, png_frag_list, self.moduletree, self.Qcore)
        recovery_list = assemblePng.assemble_png(self.filename, ihdr_list, idat_list, pnglist, self.Qcore)
        self.treeWidget.clear()
        for x in perfect_png_list:
            perfect_png_item = QtWidgets.QTreeWidgetItem(self.treeWidget)
            #perfect_png_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            perfect_png_item.setCheckState(0,QtCore.Qt.Unchecked)
            perfect_png_item.setText(1,'perfect_png')
            perfect_png_item.setText(2,'{0} byte'.format(len(x)))
            perfect_png_item.setText(3,'pass')
            perfect_png_button = QtWidgets.QPushButton("view")
            perfect_png_button.clicked.connect(partial(self.viewhandler,x))
            perfect_png_button.setFixedSize(80,30)
            self.treeWidget.setItemWidget(perfect_png_item, 4, perfect_png_button)
            perfect_png_item.setData(4, QtCore.Qt.UserRole, QtCore.QVariant(x))
            self.treeWidget.addTopLevelItem(perfect_png_item)

        for x in recovery_list:
           recovery_png_item = QtWidgets.QTreeWidgetItem(self.treeWidget)
           #recovery_png_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
           recovery_png_item.setCheckState(0,QtCore.Qt.Unchecked)
           recovery_png_item.setText(1,'fragment_png')
           recovery_png_item.setText(2,'{0} byte'.format(len(x)))
           recovery_png_item.setText(3, 'done')
           recovery_png_button = QtWidgets.QPushButton("view")
           recovery_png_button.setFixedSize(80,30)
           recovery_png_button.clicked.connect(partial(self.viewhandler, x))
           self.treeWidget.setItemWidget(recovery_png_item, 4, recovery_png_button)
           recovery_png_item.setData(4, QtCore.Qt.UserRole, QtCore.QVariant(x))
           self.treeWidget.addTopLevelItem(recovery_png_item)
        
        self.movie.stop()
        self.testLabel.hide()
        self.alertDialog("recovery completed")


    #지정한 위치의 데이터를 다운로드하는 함수
    def downloadData(self):
        self.testLabel.show()
        for x in range(self.treeWidget.topLevelItemCount()):
            if self.treeWidget.topLevelItem(x).checkState(0) == 2:
                path = os.path.join(os.environ["HOMEPATH"], "Desktop")
                path += '/'+ self.treeWidget.topLevelItem(x).text(1) + str(x) +'.png'
                with open(path, 'wb') as f:
                    f.write(self.treeWidget.topLevelItem(x).data(4, QtCore.Qt.UserRole))
        self.testLabel.hide()
        self.alertDialog("download complete!")

   #메시지 알람 함수
    def alertDialog(self, text=""):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(text);
        msgBox.exec()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())