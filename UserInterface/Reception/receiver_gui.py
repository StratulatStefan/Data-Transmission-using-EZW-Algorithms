# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'receiver.ui'
##
## Created by: Qt User Interface Compiler version 5.15.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.ApplicationModal)
        MainWindow.resize(1579, 1004)
        MainWindow.setLayoutDirection(Qt.LeftToRight)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.title = QLabel(self.centralwidget)
        self.title.setObjectName(u"title")
        self.title.setGeometry(QRect(410, 20, 732, 33))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setLayoutDirection(Qt.LeftToRight)
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(30, 80, 701, 851))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        font1.setWeight(75)
        self.groupBox_2.setFont(font1)
        self.con = QGroupBox(self.groupBox_2)
        self.con.setObjectName(u"con")
        self.con.setGeometry(QRect(30, 40, 621, 241))
        self.check_connections = QPushButton(self.con)
        self.check_connections.setObjectName(u"check_connections")
        self.check_connections.setGeometry(QRect(190, 200, 231, 31))
        self.check_connections.setFont(font1)
        self.select_image_label_14 = QLabel(self.con)
        self.select_image_label_14.setObjectName(u"select_image_label_14")
        self.select_image_label_14.setGeometry(QRect(220, 30, 211, 41))
        font2 = QFont()
        font2.setPointSize(11)
        font2.setBold(True)
        font2.setWeight(75)
        self.select_image_label_14.setFont(font2)
        self.select_image_label_14.setLayoutDirection(Qt.LeftToRight)
        self.connection_status = QTextEdit(self.con)
        self.connection_status.setObjectName(u"connection_status")
        self.connection_status.setGeometry(QRect(20, 80, 571, 61))
        self.image_name = QTextEdit(self.groupBox_2)
        self.image_name.setObjectName(u"image_name")
        self.image_name.setGeometry(QRect(260, 330, 301, 31))
        self.select_image_label_15 = QLabel(self.groupBox_2)
        self.select_image_label_15.setObjectName(u"select_image_label_15")
        self.select_image_label_15.setGeometry(QRect(40, 320, 211, 41))
        self.select_image_label_15.setFont(font2)
        self.select_image_label_15.setLayoutDirection(Qt.LeftToRight)
        self.image_dimensions = QTextEdit(self.groupBox_2)
        self.image_dimensions.setObjectName(u"image_dimensions")
        self.image_dimensions.setGeometry(QRect(260, 390, 301, 31))
        self.select_image_label_16 = QLabel(self.groupBox_2)
        self.select_image_label_16.setObjectName(u"select_image_label_16")
        self.select_image_label_16.setGeometry(QRect(40, 380, 211, 41))
        self.select_image_label_16.setFont(font2)
        self.select_image_label_16.setLayoutDirection(Qt.LeftToRight)
        self.image_decomposition_levels = QTextEdit(self.groupBox_2)
        self.image_decomposition_levels.setObjectName(u"image_decomposition_levels")
        self.image_decomposition_levels.setGeometry(QRect(260, 510, 301, 31))
        self.select_image_label_17 = QLabel(self.groupBox_2)
        self.select_image_label_17.setObjectName(u"select_image_label_17")
        self.select_image_label_17.setGeometry(QRect(40, 500, 211, 41))
        self.select_image_label_17.setFont(font2)
        self.select_image_label_17.setLayoutDirection(Qt.LeftToRight)
        self.image_expected_iterations = QTextEdit(self.groupBox_2)
        self.image_expected_iterations.setObjectName(u"image_expected_iterations")
        self.image_expected_iterations.setGeometry(QRect(260, 690, 301, 31))
        self.select_image_label_18 = QLabel(self.groupBox_2)
        self.select_image_label_18.setObjectName(u"select_image_label_18")
        self.select_image_label_18.setGeometry(QRect(40, 680, 211, 41))
        self.select_image_label_18.setFont(font2)
        self.select_image_label_18.setLayoutDirection(Qt.LeftToRight)
        self.significance_map_conventions = QTextEdit(self.groupBox_2)
        self.significance_map_conventions.setObjectName(u"significance_map_conventions")
        self.significance_map_conventions.setGeometry(QRect(40, 770, 551, 31))
        self.select_image_label_19 = QLabel(self.groupBox_2)
        self.select_image_label_19.setObjectName(u"select_image_label_19")
        self.select_image_label_19.setGeometry(QRect(40, 730, 361, 41))
        self.select_image_label_19.setFont(font2)
        self.select_image_label_19.setLayoutDirection(Qt.LeftToRight)
        self.image_size = QTextEdit(self.groupBox_2)
        self.image_size.setObjectName(u"image_size")
        self.image_size.setGeometry(QRect(260, 450, 301, 31))
        self.select_image_label_20 = QLabel(self.groupBox_2)
        self.select_image_label_20.setObjectName(u"select_image_label_20")
        self.select_image_label_20.setGeometry(QRect(40, 440, 211, 41))
        self.select_image_label_20.setFont(font2)
        self.select_image_label_20.setLayoutDirection(Qt.LeftToRight)
        self.wavelet_algorithm = QTextEdit(self.groupBox_2)
        self.wavelet_algorithm.setObjectName(u"wavelet_algorithm")
        self.wavelet_algorithm.setGeometry(QRect(370, 570, 301, 31))
        self.select_image_label_28 = QLabel(self.groupBox_2)
        self.select_image_label_28.setObjectName(u"select_image_label_28")
        self.select_image_label_28.setGeometry(QRect(40, 570, 321, 41))
        self.select_image_label_28.setFont(font2)
        self.select_image_label_28.setLayoutDirection(Qt.LeftToRight)
        self.select_image_label_29 = QLabel(self.groupBox_2)
        self.select_image_label_29.setObjectName(u"select_image_label_29")
        self.select_image_label_29.setGeometry(QRect(40, 630, 151, 41))
        self.select_image_label_29.setFont(font2)
        self.select_image_label_29.setLayoutDirection(Qt.LeftToRight)
        self.wavelet_type = QTextEdit(self.groupBox_2)
        self.wavelet_type.setObjectName(u"wavelet_type")
        self.wavelet_type.setGeometry(QRect(250, 630, 301, 31))
        self.grbox = QGroupBox(self.centralwidget)
        self.grbox.setObjectName(u"grbox")
        self.grbox.setGeometry(QRect(780, 80, 701, 871))
        self.grbox.setFont(font1)
        self.select_image_label_21 = QLabel(self.grbox)
        self.select_image_label_21.setObjectName(u"select_image_label_21")
        self.select_image_label_21.setGeometry(QRect(160, 40, 211, 41))
        self.select_image_label_21.setFont(font2)
        self.select_image_label_21.setLayoutDirection(Qt.LeftToRight)
        self.current_iteration = QTextEdit(self.grbox)
        self.current_iteration.setObjectName(u"current_iteration")
        self.current_iteration.setGeometry(QRect(340, 50, 151, 31))
        self.groupBox = QGroupBox(self.grbox)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(40, 90, 611, 361))
        self.wavelet_label = QLabel(self.groupBox)
        self.wavelet_label.setObjectName(u"wavelet_label")
        self.wavelet_label.setGeometry(QRect(30, 30, 461, 301))
        self.groupBox_4 = QGroupBox(self.grbox)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(40, 470, 611, 371))
        self.image_label = QLabel(self.groupBox_4)
        self.image_label.setObjectName(u"image_label")
        self.image_label.setGeometry(QRect(30, 30, 561, 351))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1579, 26))
        self.menu_help = QMenu(self.menubar)
        self.menu_help.setObjectName(u"menu_help")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_help.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.title.setText(QCoreApplication.translate("MainWindow", u"Data Transmission using EZW Algorithm - Receiver", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Decoding and Receiving", None))
        self.con.setTitle(QCoreApplication.translate("MainWindow", u"Connection", None))
        self.check_connections.setText(QCoreApplication.translate("MainWindow", u"Check for connections", None))
        self.select_image_label_14.setText(QCoreApplication.translate("MainWindow", u"Connection Status", None))
        self.select_image_label_15.setText(QCoreApplication.translate("MainWindow", u"Image name", None))
        self.select_image_label_16.setText(QCoreApplication.translate("MainWindow", u"Image dimensions", None))
        self.select_image_label_17.setText(QCoreApplication.translate("MainWindow", u"Decomposition levels", None))
        self.select_image_label_18.setText(QCoreApplication.translate("MainWindow", u"Expected Iterations", None))
        self.select_image_label_19.setText(QCoreApplication.translate("MainWindow", u"Significance Map Encoding Conventions", None))
        self.select_image_label_20.setText(QCoreApplication.translate("MainWindow", u"Image size", None))
        self.select_image_label_28.setText(QCoreApplication.translate("MainWindow", u"Wavelet Decomposition Algorithm", None))
        self.select_image_label_29.setText(QCoreApplication.translate("MainWindow", u"Wavelet Type", None))
        self.grbox.setTitle(QCoreApplication.translate("MainWindow", u"Recomposition", None))
        self.select_image_label_21.setText(QCoreApplication.translate("MainWindow", u"Current Iteration", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Wavelet Recomposition", None))
        self.wavelet_label.setText("")
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Image Recomposition", None))
        self.image_label.setText("")
        self.menu_help.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

