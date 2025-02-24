try:
    import requests
    from PIL import Image
    from io import BytesIO
except Exception as e:
    print(e)
    
import concurrent.futures  
import os
import cv2
from pytesseract import *
pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

# ------------------------------ Importacioes para la interfaz ------------------------------ #
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QGraphicsDropShadowEffect, QApplication, QMainWindow
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QImage, QImageReader, QClipboard
from PyQt5.QtCore import Qt, QSize, QMimeData, QUrl, QEvent, QEventLoop
# ------------------------------ End Importacioes para la interfaz ------------------------------ #

# ----- Clase list item ----- #
from ui_list_item import ListItem
# ----- End Clase list item ----- #

# ------------------------------ Extractor ------------------------------ #   
def extract(elem_actual):   
    if elem_actual['link']:
        try:
            content_type = elem_actual['file'].headers.get('content-type')
            file_extension = ''

            if content_type:
                if 'jpeg' in content_type:
                    file_extension = '.jpg'
                elif 'png' in content_type:
                    file_extension = '.png'

            filename = f"temp_image_{elem_actual['object'].id}{file_extension}"

            with open(filename, 'wb') as f:
                f.write(elem_actual['file'].content)

            try:
                # image = Image.open(filename)
                gray_image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
                _, th = cv2.threshold(gray_image, 138, 255, cv2.THRESH_BINARY)
                text = pytesseract.image_to_string(th)
            finally:
                # image.close()
                os.remove(filename)
            
        except elem_actual['file'].exceptions.RequestException as e:
            elem_actual['link'] = 'Error'
            print(f"Error en la solicitud HTTP: {e}")
            text = None 
            
    elif elem_actual['paste']:
        try:
            # image = Image.open(elem_actual['file'])
            # text = pytesseract.image_to_string(image)
            gray_image = cv2.imread(elem_actual['file'], cv2.IMREAD_GRAYSCALE)
            _, th = cv2.threshold(gray_image, 138, 255, cv2.THRESH_BINARY)
            text = pytesseract.image_to_string(th)
            
        finally:
            # image.close()
            os.remove(elem_actual['file'])
    else:
        # image = Image.open(elem_actual['file'])
        # text = pytesseract.image_to_string(image)
        gray_image = cv2.imread(elem_actual['file'], cv2.IMREAD_GRAYSCALE)
        _, th = cv2.threshold(gray_image, 138, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(th)
        
    return text, elem_actual
# ------------------------------ End Extractor ------------------------------ #   

### ---/-/---/-/---/-/---/-/---/-/--- Interfaz principal ---/-/---/-/---/-/---/-/---/-/--- ###
class Ui_MainWindow(object):
    def __init__(self):
        self.item_id = 0       
        self.image_previews = []
        self.elementos_list = []
        self.is_proc = False
            
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 700)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(900, 700))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(900, 700))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(900, 700))
        self.frame.setBaseSize(QtCore.QSize(5, 0))
        self.frame.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(146, 184, 181, 201), stop:1 rgba(255, 255, 255, 179))")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.frame_sup = QtWidgets.QFrame(self.frame)
        self.frame_sup.setEnabled(True)
        self.frame_sup.setGeometry(QtCore.QRect(10, 10, 881, 60))
        self.frame_sup.setMinimumSize(QtCore.QSize(881, 60))
        self.frame_sup.setMaximumSize(QtCore.QSize(16777215, 60))
        self.frame_sup.setStyleSheet("background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255, 255, 255, 203), stop:1 rgba(228, 245, 243, 163));\n"
"border-radius: 25px;\n"
"")
        self.frame_sup.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_sup.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_sup.setObjectName("frame_sup")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_sup)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(293, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.frame_sup)
        font = QtGui.QFont()
        font.setFamily("HoloLens MDL2 Assets")
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setStyleSheet("background-color: rgba(255, 255, 255, 0)")
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(199, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btn_reolad = QtWidgets.QPushButton(self.frame_sup)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_reolad.sizePolicy().hasHeightForWidth())
        self.btn_reolad.setSizePolicy(sizePolicy)
        self.btn_reolad.setMinimumSize(QtCore.QSize(20, 20))
        self.btn_reolad.setMaximumSize(QtCore.QSize(20, 20))
        self.btn_reolad.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.btn_reolad.setStyleSheet("")
        self.btn_reolad.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "reload.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_reolad.setIcon(icon)
        self.btn_reolad.setIconSize(QtCore.QSize(20, 20))
        self.btn_reolad.setObjectName("btn_reolad")
        self.horizontalLayout.addWidget(self.btn_reolad)
        spacerItem2 = QtWidgets.QSpacerItem(27, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.frame_inf = QtWidgets.QFrame(self.frame)
        self.frame_inf.setGeometry(QtCore.QRect(10, 610, 881, 78))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_inf.sizePolicy().hasHeightForWidth())
        self.frame_inf.setSizePolicy(sizePolicy)
        self.frame_inf.setMinimumSize(QtCore.QSize(881, 78))
        self.frame_inf.setMaximumSize(QtCore.QSize(16777215, 78))
        self.frame_inf.setStyleSheet("background-color:rgba(243, 255, 255, 237);\n"
"border-radius: 20px 20px 5px 5px;")
        self.frame_inf.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_inf.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_inf.setObjectName("frame_inf")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_inf)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem3 = QtWidgets.QSpacerItem(347, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem3)
        self.btn_proc = QtWidgets.QPushButton(self.frame_inf)
        font = QtGui.QFont()
        font.setFamily("HoloLens MDL2 Assets")
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        self.btn_proc.setFont(font)
        self.btn_proc.setStyleSheet("QPushButton{\n"
"color: white;\n"
"padding: 5px 10px ;\n"
"border-radius: 15px;\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0.528, x2:1, y2:0.517, stop:0 rgba(95, 170, 177, 255), stop:1 rgba(59, 117, 127, 255));\n"
"border: 4px outset rgba(80,171,255,0.71);\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0.528, x2:1, y2:0.517, stop:0 rgba(67, 142,150, 255), stop:1 rgba(53, 97, 105, 255));\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: qlineargradient(spread:pad, x1:1, y1:0.608, x2:0, y2:0.375, stop:0 rgba(59, 117, 127, 255), stop:1 rgba(26, 44, 50, 255))\n"
"}")
        self.btn_proc.setObjectName("btn_proc")
        self.horizontalLayout_5.addWidget(self.btn_proc)
        spacerItem4 = QtWidgets.QSpacerItem(346, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem4)
        self.frame_mid = QtWidgets.QFrame(self.frame)
        self.frame_mid.setGeometry(QtCore.QRect(10, 84, 881, 521))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_mid.sizePolicy().hasHeightForWidth())
        self.frame_mid.setSizePolicy(sizePolicy)
        self.frame_mid.setMinimumSize(QtCore.QSize(841, 521))
        self.frame_mid.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"\n"
"border: 2px solid rgb(191, 224, 226);\n"
"\n"
"border-radius: 15px;\n"
"")
        self.frame_mid.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_mid.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_mid.setObjectName("frame_mid")
        
        # Crear un QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5) 
        shadow.setOffset(0, 0) 
        shadow.setColor(QtGui.QColor(26, 44, 50, 191)) 
        self.frame_mid.setGraphicsEffect(shadow)
        
        # Evento drop
        self.frame_mid.setAcceptDrops(True) 
        self.frame_mid.dragEnterEvent = self.dragEnterEvent
        self.frame_mid.dropEvent = self.dropEvent
        
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_mid)
        self.verticalLayout_2.setContentsMargins(0, -1, 0, -1)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_elemnts = QtWidgets.QFrame(self.frame_mid)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(14)
        sizePolicy.setVerticalStretch(14)
        sizePolicy.setHeightForWidth(self.frame_elemnts.sizePolicy().hasHeightForWidth())
        self.frame_elemnts.setSizePolicy(sizePolicy)
        self.frame_elemnts.setMinimumSize(QtCore.QSize(859, 275))
        self.frame_elemnts.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.frame_elemnts.setStyleSheet("border-top: unset;\n"
"border-left: unset;\n"
"border-right: unset;\n"
"border-bottom: 5px solid rgba(242, 249, 249, 0.7);\n"
"")
        self.frame_elemnts.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_elemnts.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_elemnts.setObjectName("frame_elemnts")
        self.list_items = QtWidgets.QListWidget(self.frame_elemnts)
        self.list_items.setGeometry(QtCore.QRect(10, 0, 860, 280))
        self.list_items.setMinimumSize(QtCore.QSize(860, 280))
        self.list_items.setStyleSheet("border: unset;\n"
"border-radius: unset;")
        self.list_items.setObjectName("list_items")
        self.verticalLayout_2.addWidget(self.frame_elemnts)
        self.frame_pad_info = QtWidgets.QFrame(self.frame_mid)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_pad_info.sizePolicy().hasHeightForWidth())
        self.frame_pad_info.setSizePolicy(sizePolicy)
        self.frame_pad_info.setMinimumSize(QtCore.QSize(859, 206))
        self.frame_pad_info.setMaximumSize(QtCore.QSize(16777215, 206))
        self.frame_pad_info.setSizeIncrement(QtCore.QSize(0, 0))
        self.frame_pad_info.setStyleSheet("border: unset;")
        self.frame_pad_info.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_pad_info.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_pad_info.setObjectName("frame_pad_info")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_pad_info)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_pad_img = QtWidgets.QFrame(self.frame_pad_info)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_pad_img.sizePolicy().hasHeightForWidth())
        self.frame_pad_img.setSizePolicy(sizePolicy)
        self.frame_pad_img.setMinimumSize(QtCore.QSize(859, 89))
        self.frame_pad_img.setMaximumSize(QtCore.QSize(16777215, 89))
        self.frame_pad_img.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_pad_img.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_pad_img.setObjectName("frame_pad_img")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_pad_img)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem5 = QtWidgets.QSpacerItem(374, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem5)
        self.label_img = QtWidgets.QLabel(self.frame_pad_img)
        self.label_img.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_img.sizePolicy().hasHeightForWidth())
        self.label_img.setSizePolicy(sizePolicy)
        self.label_img.setMinimumSize(QtCore.QSize(123, 102))
        self.label_img.setMaximumSize(QtCore.QSize(123, 102))
        self.label_img.setSizeIncrement(QtCore.QSize(0, 0))
        self.label_img.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("HoloLens MDL2 Assets")
        font.setPointSize(8)
        self.label_img.setFont(font)
        self.label_img.setStyleSheet("border: unset;")
        self.label_img.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_img.setText("")
        self.label_img.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "tool-box-image.svg")))
        self.label_img.setScaledContents(True)
        self.label_img.setAlignment(QtCore.Qt.AlignCenter)
        self.label_img.setObjectName("label_img")
        self.horizontalLayout_4.addWidget(self.label_img)
        spacerItem6 = QtWidgets.QSpacerItem(374, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem6)
        self.verticalLayout.addWidget(self.frame_pad_img)
        self.frame_inf_2 = QtWidgets.QFrame(self.frame_pad_info)
        self.frame_inf_2.setMinimumSize(QtCore.QSize(859, 38))
        self.frame_inf_2.setMaximumSize(QtCore.QSize(16777215, 38))
        self.frame_inf_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_inf_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_inf_2.setObjectName("frame_inf_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_inf_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem7 = QtWidgets.QSpacerItem(256, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem7)
        self.label_info = QtWidgets.QLabel(self.frame_inf_2)
        font = QtGui.QFont()
        font.setFamily("HoloLens MDL2 Assets")
        font.setPointSize(14)
        self.label_info.setFont(font)
        self.label_info.setStyleSheet("border: unset;")
        self.label_info.setObjectName("label_info")
        self.horizontalLayout_2.addWidget(self.label_info)
        spacerItem8 = QtWidgets.QSpacerItem(256, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem8)
        self.verticalLayout.addWidget(self.frame_inf_2)
        self.frame_pad_cargar = QtWidgets.QFrame(self.frame_pad_info)
        self.frame_pad_cargar.setMinimumSize(QtCore.QSize(859, 52))
        self.frame_pad_cargar.setMaximumSize(QtCore.QSize(16777215, 52))
        self.frame_pad_cargar.setStyleSheet("")
        self.frame_pad_cargar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_pad_cargar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_pad_cargar.setObjectName("frame_pad_cargar")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_pad_cargar)
        self.horizontalLayout_3.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem9 = QtWidgets.QSpacerItem(386, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem9)
        self.btn_cargar = QtWidgets.QPushButton(self.frame_pad_cargar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_cargar.sizePolicy().hasHeightForWidth())
        self.btn_cargar.setSizePolicy(sizePolicy)
        self.btn_cargar.setMinimumSize(QtCore.QSize(100, 40))
        self.btn_cargar.setMaximumSize(QtCore.QSize(100, 50))
        font = QtGui.QFont()
        font.setFamily("HoloLens MDL2 Assets")
        font.setPointSize(12)
        font.setBold(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.btn_cargar.setFont(font)
        self.btn_cargar.setStyleSheet("QPushButton{\n"
"margin: 0;\n"
"padding: 0;\n"
"color: rgb(53, 97, 105);\n"
"border-radius: 15px;\n"
"border: 4px outset rgba(80,171,255,0.4);\n"
"\n"
"}\n"
"QPushButton:hover {\n"
"background-color: rgb(242, 249, 249);\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: rgb(221, 239, 240);\n"
"}\n"
"\n"
"     ")
        self.btn_cargar.setObjectName("btn_cargar")
        self.horizontalLayout_3.addWidget(self.btn_cargar)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem10)
        self.verticalLayout.addWidget(self.frame_pad_cargar)
        self.verticalLayout_2.addWidget(self.frame_pad_info)
        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        self.setup_key_shortcuts()
        MainWindow.keyPressEvent = self.load_image_from_clipboard
        
    # ----------------------------- Botones ----------------------------- #   
    def setup_key_shortcuts(self):  
        self.btn_reolad.pressed.connect(lambda: self.apply_shadow_effect())
        self.btn_reolad.released.connect(lambda: self.remove_shadow_effect())
        self.btn_reolad.clicked.connect(lambda: self.recargar())
        
        self.btn_cargar.clicked.connect(lambda: self.load_image_from_file_dialog())
        self.btn_proc.clicked.connect(lambda: self.procesar_imagen())
    # ----------------------------- End Botones ----------------------------- #
    
    # ----------------------------- Limpiar ----------------------------- #
    def recargar(self):
        self.list_items.clear()
        self.item_id = 0    
        for elem_actual in self.elementos_list:
                del elem_actual
        self.elementos_list = []
        self.is_proc = False
    # ----------------------------- End Limpiar ----------------------------- #  
     
    # ----------------------------- Procesar ----------------------------- #   
    def procesar_imagen(self):
        self.is_proc = True
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for elem_actual in self.elementos_list:
                future = executor.submit(extract, elem_actual)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                text, elem_actual = future.result()
                self.show_text(text,elem_actual)          
    # ----------------------------- End Procesar ----------------------------- #   
    
    # ----------------------------- Mostrar texto ----------------------------- #    
    def show_text(self, text, elem_actual):
        if text:
            elem_actual['object'].info_text.setText(text)
            elem_actual['object'].info_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
            elem_actual['object'].btn_copy.setEnabled(True)
        elif elem_actual['link'] == 'Error': 
            elem_actual['object'].info_text.setText("No se pudo acceder a la imagen en la URL especificada. Asegúrate de que la URL sea válida y que tengas una conexión a Internet activa.")
        else:
            elem_actual['object'].info_text.setText("No hay texto que extraer.")
    # ----------------------------- End Mostrar texto ----------------------------- #    
            
    # ----------------------------- Sombra de reload y copy ----------------------------- #   
    def apply_shadow_effect(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5) 
        shadow.setOffset(0, 0)
        shadow.setColor(QtGui.QColor(26, 44, 50, 191))
        self.btn_reolad.setGraphicsEffect(shadow)
    
    def remove_shadow_effect(self):
        self.btn_reolad.setGraphicsEffect(None)
    # ----------------------------- End Sombra de reload y copy ----------------------------- #   
           
    # ----------------------------- Cargar elemento en interfaz ----------------------------- #   
    def load_in_list(self, file_name=None, is_url=False, is_paste=False):
        self.item_id += 1
            
        elemento = ListItem(item_id=self.item_id)
        elemento.verticalLayout.setContentsMargins(2, 2, 2, 2)

        if is_url:
            try:
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(file_name.content)
                elemento.nomb_img.setText(os.path.basename(file_name.url))
            except Exception as e:
                print(e)    
        else:
            if is_paste:
                custom_filename = f"image_{self.item_id}.png"
                temp_img = Image.fromqpixmap(file_name)
                temp_img.save(custom_filename)
                file_name = custom_filename
                
            elemento.nomb_img.setText(os.path.basename(file_name))
            pixmap = QtGui.QPixmap(file_name)
            
        if pixmap is not None:
            pixmap = pixmap.scaled(250, 90, Qt.KeepAspectRatio)
            elemento.info_img.setPixmap(pixmap)
    
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(elemento.sizeHint())
        self.list_items.addItem(item)
        self.list_items.setItemWidget(item, elemento)
        self.elementos_list.append(
            {
                'file': file_name,
                'object': elemento,
                'link': is_url,
                'paste': is_paste
            }   
        )
    # ----------------------------- End Cargar elemento en interfaz ----------------------------- #   
    
    # ----------------------------- Tipo de elemento ----------------------------- #   
    def load_image(self, file_name=None, is_url=False, is_paste=False):
        if self.is_proc:
            self.recargar()
            return self.load_image(file_name, is_url, is_paste)
        else: 
            if is_url:
                self.load_in_list(file_name, is_url=True)
            elif is_paste:
                self.load_in_list(file_name, is_paste=True)
            else:
                self.load_in_list(file_name)
    # ----------------------------- End Tipo de elemento ----------------------------- #   
    
    #### --/--/--/--/--/--/--/--/--/-- Tipos de eventos de carga --/--/--/--/--/--/--/--/--/-- ####   
    # ----------------------------- Portapapeles ----------------------------- #   
    def load_image_from_clipboard(self,event):
        if event.key() == Qt.Key_V and event.modifiers() & Qt.ControlModifier:
            clipboard = QApplication.clipboard()
            if clipboard and clipboard.mimeData().hasImage():
               image = clipboard.image()
               self.load_image(image, is_paste=True)
    # ----------------------------- End Portapapeles ----------------------------- #   

    # ----------------------------- Explorador de archivos ----------------------------- #   
    def load_image_from_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Cargar imagen", "", "Images (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_name:
            return self.load_image(file_name)
    # ----------------------------- End Explorador de archivos ----------------------------- # 
      
    # ----------------------------- Drag and drop ----------------------------- #   
    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls() and mime_data.urls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls() and mime_data.urls():
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    return self.load_image(file_path)
                response = self.is_image_url(url.toString())
                if response:
                    return self.load_image(response, is_url=True)
    # ----------------------------- End Drag and drop ----------------------------- # 
    #### --/--/--/--/--/--/--/--/--/-- End Tipos de eventos de carga --/--/--/--/--/--/--/--/--/-- ####  
     
    # ----------------------------- Verificar url img ----------------------------- # 
    def is_image_url(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type')
                if content_type and content_type.startswith('image'):
                    img = Image.open(BytesIO(response.content))
                    return response
        except Exception as e:
            print(e)
            error_element = ListItem(0)
            error_element.verticalLayout.setContentsMargins(2, 2, 2, 2)
            error_element.nomb_img.setText("Error")
            error_element.info_text.setText("No se pudo acceder a la imagen en la URL especificada. Asegúrate de que la URL sea válida y que tengas una conexión a Internet activa.")
            pixmap = QtGui.QPixmap("../resources/question.svg")
            pixmap = pixmap.scaled(250, 90, Qt.KeepAspectRatio)
            error_element.info_img.setPixmap(pixmap)
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(error_element.sizeHint())
            self.list_items.addItem(item)
            self.list_items.setItemWidget(item, error_element)        
        return None
    # ----------------------------- End Verificar url img ----------------------------- # 
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Extractor de texto"))
        self.label.setText(_translate("MainWindow", "Coloque la imagen para extraer el texto"))
        self.btn_proc.setText(_translate("MainWindow", "Procesar imagen"))
        self.label_info.setText(_translate("MainWindow", "Arrastrar y soltar, cargar o pegar la imagen"))
        self.btn_cargar.setText(_translate("MainWindow", "Cargar"))
### ---/-/---/-/---/-/---/-/---/-/--- EndInterfaz principal ---/-/---/-/---/-/---/-/---/-/--- ###

if __name__ == "__main__":      
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())