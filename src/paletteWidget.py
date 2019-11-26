import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.panelwidget import PanelWidget


class PaletteWidget(PanelWidget):
    FREE, LINE, POLYGON, ELLIPSIS, CURVE, TRANSLATE, ROTATE, SCALE, CLIP = range(9)

    def __init__(self):
        super().__init__()

        self.state = self.FREE

        self.resetDialog = ResetDialog()
        self.lineDialog = LineDialog()

        self.resetBtn = QPushButton(self)
        self.setColorBtn = QPushButton(self)
        self.saveBtn = QPushButton(self)
        self.drawLineBtn = QPushButton(self)
        self.drawPolygonBtn = QPushButton(self)
        self.drawEllipsisBtn = QPushButton(self)
        self.drawCurveBtn = QPushButton(self)
        self.translateBtn = QPushButton(self)
        self.rotateBtn = QPushButton(self)
        self.scaleBtn = QPushButton(self)
        self.clipBtn = QPushButton(self)

        self.initUI()

    def initUI(self):
        self.setGeometry(400, 200, 800, 600)

        self.resetDialog.okBtn.clicked.connect(self.slotResetOkBtn)
        self.lineDialog.okBtn.clicked.connect(self.slotLineOkBtn)

        self.resetBtn.setFixedSize(100, 20)
        self.resetBtn.setText('reset')
        self.resetBtn.clicked.connect(self.slotResetBtn)
        self.setColorBtn.setFixedSize(100, 20)
        self.setColorBtn.setText('set color')
        self.setColorBtn.clicked.connect(self.slotColorBtn)
        self.saveBtn.setFixedSize(100, 20)
        self.saveBtn.setText('save')
        self.saveBtn.clicked.connect(self.slotSaveBtn)
        self.drawLineBtn.setFixedSize(100, 20)
        self.drawLineBtn.setText('draw line')
        self.drawLineBtn.clicked.connect(self.slotLineBtn)
        self.drawPolygonBtn.setFixedSize(100, 20)
        self.drawPolygonBtn.setText('draw polygon')
        self.drawEllipsisBtn.setFixedSize(100, 20)
        self.drawEllipsisBtn.setText('draw ellipsis')
        self.drawCurveBtn.setFixedSize(100, 20)
        self.drawCurveBtn.setText('draw curve')
        self.translateBtn.setFixedSize(100, 20)
        self.translateBtn.setText('translate')
        self.rotateBtn.setFixedSize(100, 20)
        self.rotateBtn.setText('rotate')
        self.scaleBtn.setFixedSize(100, 20)
        self.scaleBtn.setText('scale')
        self.clipBtn.setFixedSize(100, 20)
        self.clipBtn.setText('clip')

        btnBox = QVBoxLayout(self)
        boxLayout = QHBoxLayout(self)

        btnBox.addWidget(self.resetBtn)
        btnBox.addWidget(self.setColorBtn)
        btnBox.addWidget(self.saveBtn)
        btnBox.addWidget(self.drawLineBtn)
        btnBox.addWidget(self.drawPolygonBtn)
        btnBox.addWidget(self.drawEllipsisBtn)
        btnBox.addWidget(self.drawCurveBtn)
        btnBox.addWidget(self.translateBtn)
        btnBox.addWidget(self.rotateBtn)
        btnBox.addWidget(self.scaleBtn)
        btnBox.addWidget(self.clipBtn)
        btnBox.setSpacing(10)

        btnWidget = QWidget()
        btnWidget.setLayout(btnBox)

        boxLayout.addWidget(btnWidget)
        boxLayout.addWidget(self.panelLabel)
        boxLayout.setSpacing(10)

        self.setLayout(boxLayout)
        # self.panelLabel.setPixmap(self.panel)

    def reset(self, w, h):
        if w < 100 or h > 1000:
            self.logger.error('width or height out if range, width >= 100, height <= 1000, w:{w} h:{h}'
                              .format(w=w, h=h))
        else:
            self.setGeometry(0, 0, w + 130, h + 40)
            self.putOnCenter()
            self.panel = QPixmap(w, h)
            self.panelLabel.resize(w, h)
            # self.panelLabel.setGeometry(0, 0, w, h)
            # self.setLayout(self.boxLayout)
            self.graph.clear()
            self.panel.fill(Qt.white)
            self.panelLabel.setPixmap(self.panel)

    def mouseMoveEvent(self, event):
        pass

    def keyPressEvent(self, event):


    def slotResetBtn(self):
        self.resetDialog.widthInput.setText(str(self.panel.width()))
        self.resetDialog.heightInput.setText(str(self.panel.height()))
        self.resetDialog.exec_()

    def slotColorBtn(self):
        color = QColorDialog.getColor(self.pen.color())
        if color.isValid():
            self.pen.setColor(color)

    def slotSaveBtn(self):
        fileName, _ = QFileDialog.getSaveFileName(self,
                                                  caption='save image',
                                                  directory=os.getcwd(),
                                                  filter='BMP Files(*.bmp);;PNG Files(*.png);;JPEG Files(*.jpeg)')
        if fileName != '':
            saveFile = QFile(fileName)
            saveFile.open(QIODevice.WriteOnly)
            suffix = fileName.split('.')[1]
            self.panel.save(saveFile, suffix.upper())
            saveFile.close()

    def slotLineBtn(self):
        self.lineDialog.exec_()

    def slotLineOkBtn(self):
        self.panelLabel.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        self.state = self.LINE
        QCursor.setPos(self.x() + self.panelLabel.x() + self.panelLabel.width() / 2,
                       self.y() + self.panelLabel.y() + self.panelLabel.height() / 2)
        self.lineDialog.close()

    def slotResetOkBtn(self):
        w = int(self.resetDialog.widthInput.text())
        h = int(self.resetDialog.heightInput.text())
        if w < 100 or h > 1000:
            QMessageBox.critical(None, "Out Of Range",
                                 'width or height out if range, width >= 100, height <= 1000, w:{w} h:{h}'
                                 .format(w=w, h=h))
            return
        self.reset(w, h)
        self.resetDialog.close()


class ResetDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.widthText = QLabel()
        self.widthInput = QLineEdit()
        self.heightText = QLabel()
        self.heightInput = QLineEdit()
        self.okBtn = QPushButton()
        self.cancelBtn = QPushButton()
        self.initUI()

    def initUI(self):
        self.setFixedSize(200, 150)
        self.widthText.setText('width:')
        self.heightText.setText('height:')
        self.okBtn.setText('ok')
        self.cancelBtn.setText('cancel')
        self.cancelBtn.clicked.connect(self.close)
        widthValidator = QIntValidator(100, 2000, self)
        self.widthInput.setValidator(widthValidator)
        heightValidator = QIntValidator(0, 1000, self)
        self.heightInput.setValidator(heightValidator)
        inputBox = QGridLayout()
        inputBox.addWidget(self.widthText, 0, 0)
        inputBox.addWidget(self.widthInput, 0, 1)
        inputBox.addWidget(self.heightText, 1, 0)
        inputBox.addWidget(self.heightInput, 1, 1)
        inputBox.setSpacing(5)

        inputWidget = QWidget()
        inputWidget.setLayout(inputBox)

        layoutBox = QGridLayout()
        layoutBox.addWidget(inputWidget, 0, 0, 1, 2)
        layoutBox.addWidget(self.okBtn, 1, 0)
        layoutBox.addWidget(self.cancelBtn, 1, 1)
        layoutBox.setRowStretch(0, 2)
        layoutBox.setRowStretch(1, 1)
        self.setLayout(layoutBox)


class LineDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.algorithmChoose = QButtonGroup(self)
        self.ddaRadioBtn = QRadioButton('DDA', self)
        self.bresenhamRadioBtn = QRadioButton('Bresenham', self)
        self.okBtn = QPushButton('ok', self)
        self.cancelBtn = QPushButton('cancel', self)
        self.initUI()

    def initUI(self):
        self.setFixedSize(200, 150)
        self.algorithmChoose.addButton(self.ddaRadioBtn, 0)
        self.algorithmChoose.addButton(self.bresenhamRadioBtn, 1)
        self.ddaRadioBtn.setChecked(True)
        self.cancelBtn.clicked.connect(self.close)

        layoutBox = QGridLayout()
        layoutBox.addWidget(self.ddaRadioBtn, 0, 0)
        layoutBox.addWidget(self.bresenhamRadioBtn, 0, 1)
        layoutBox.addWidget(self.okBtn, 1, 0)
        layoutBox.addWidget(self.cancelBtn, 1, 1)
        layoutBox.setSpacing(5)

        self.setLayout(layoutBox)
