import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.graph import MyLine, MyPolygon
from src.panelwidget import PanelWidget


class PaletteWidget(PanelWidget):
    FREE, LINE, POLYGON, ELLIPSIS, CURVE, TRANSLATE, ROTATE, SCALE, CLIP = range(9)

    def __init__(self):
        super().__init__()

        self.state = self.FREE
        self.algorithm = str()
        self.vertexes = list()
        self.tempGraph = dict()

        self.resetDialog = ResetDialog()
        self.lineDialog = LineDialog()
        self.polygonDialog = PolygonDialog()

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
        self.polygonDialog.okBtn.clicked.connect(self.slotPolygonOkBtn)

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
        self.drawPolygonBtn.clicked.connect(self.slotPolygonBtn)
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

        btnWidget = QWidget(self)
        btnWidget.setGeometry(10, 20, 120, 320)
        btnWidget.setLayout(btnBox)

        self.panelLabel.setGeometry(140, 20, 200, 200)
        self.panelLabel.setMouseTracking(True)
        # self.panelLabel.setPixmap(self.panel)

    def reset(self, w, h):
        if w < 100 or h > 1000:
            self.logger.error('width or height out if range, width >= 100, height <= 1000, w:{w} h:{h}'
                              .format(w=w, h=h))
        else:
            winWidth = w + 160
            winHeight = h + 40
            if winHeight < 360:
                winHeight = 360
            self.setGeometry(0, 0, winWidth, winHeight)
            self.panel = QPixmap(w, h)
            self.panelLabel.setGeometry(140, 20, w, h)
            self.graph.clear()
            self.panel.fill(Qt.white)
            self.panelLabel.setPixmap(self.panel)
            self.setGeometry(0, 0, winWidth, winHeight)
            self.putOnCenter()

    def mouseMoveEvent(self, event):
        # print('position: x:{x} y:{y}'.format(x=event.pos().x(), y=event.pos().y()))
        newX = max(event.pos().x(), self.panelLabel.x())
        newX = min(newX, self.panelLabel.x() + self.panelLabel.width())
        newY = max(event.pos().y(), self.panelLabel.y())
        newY = min(newY, self.panelLabel.y() + self.panelLabel.height())
        QCursor.setPos(self.mapToGlobal(QPoint(newX, newY)))

        if self.state == self.LINE:
            if len(self.vertexes) != 0:
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.tempGraph = self.graph.copy()
                self.tempGraph['temp'] = MyLine(['temp'] + self.vertexes + [newX, newY], self.pen.color(),
                                                self.algorithm)
                self.drawTempGraph()

        elif self.state == self.POLYGON:
            if len(self.vertexes) != 0:
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.tempGraph = self.graph.copy()
                self.tempGraph['temp'] = MyPolygon(['temp', len(self.vertexes) // 2 + 1], self.pen.color(),
                                                   self.algorithm, self.vertexes + [newX, newY])
                self.drawTempGraph()

    def mousePressEvent(self, event):
        if self.state == self.LINE and event.button() == Qt.LeftButton:
            newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
            newX = newPoint.x()
            newY = newPoint.y()
            self.vertexes += [newX, newY]
            if len(self.vertexes) == 4:
                newID = len(self.graph)
                self.graph[newID] = MyLine([newID] + self.vertexes, self.pen.color(), self.algorithm)
                self.quitDraw()

        elif self.state == self.POLYGON:
            if event.button() == Qt.LeftButton:
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.vertexes += [newX, newY]
            elif event.button() == Qt.RightButton:
                if len(self.vertexes) > 2:
                    newID = len(self.graph)
                    self.graph[newID] = MyPolygon([newID, len(self.vertexes) // 2], self.pen.color(), self.algorithm,
                                                  self.vertexes)
                self.quitDraw()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.state != self.FREE:
            self.quitDraw()

    def drawTempGraph(self):
        self.panel.fill(Qt.white)
        painter = QPainter(self.panel)
        for gragh in self.tempGraph.values():
            gragh.draw(painter)
        self.panelLabel.setPixmap(self.panel)

    def quitDraw(self):
        self.setMouseTracking(False)
        self.panelLabel.setCursor(Qt.ArrowCursor)
        self.vertexes.clear()
        self.panelLabel.setPixmap(self.panel)
        self.state = self.FREE
        self.drawGragh()

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

    def slotPolygonBtn(self):
        self.polygonDialog.exec_()

    def slotEllipsisBtn(self):
        self.panelLabel.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        self.state = self.ELLIPSIS

        QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                 self.panelLabel.y() + int(self.panelLabel.height() / 2))))

    def slotLineOkBtn(self):
        # print('self: x:{x} y:{y}'.format(x=self.x(), y=self.y()))
        # print('panelLabel: x:{x} y:{y} w:{w} h:{h}'.format(x=self.panelLabel.x(), y=self.panelLabel.y(),
        #                                                    w=self.panelLabel.width(), h=self.panelLabel.height()))
        self.panelLabel.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        self.state = self.LINE

        QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                 self.panelLabel.y() + int(self.panelLabel.height() / 2))))
        if self.lineDialog.algorithmChoose.checkedId() == 0:
            self.algorithm = 'DDA'
        else:
            self.algorithm = 'Bresenham'
        # QCursor.setPos(self.x() + self.panelLabel.x() + self.panelLabel.width() / 2,
        #                self.y() + self.panelLabel.y() + self.panelLabel.height() / 2)
        # print('cusor pos: x:{x} y:{y}'.format(x=QCursor.pos().x(), y=QCursor.pos().y()))
        self.lineDialog.close()

    def slotPolygonOkBtn(self):
        self.panelLabel.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        self.state = self.POLYGON

        QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                 self.panelLabel.y() + int(self.panelLabel.height() / 2))))
        if self.lineDialog.algorithmChoose.checkedId() == 0:
            self.algorithm = 'DDA'
        else:
            self.algorithm = 'Bresenham'
        self.polygonDialog.close()

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


class AlgorithmDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.algorithmChoose = QButtonGroup(self)
        self.RadioBtn1 = QRadioButton(self)
        self.RadioBtn2 = QRadioButton(self)
        self.okBtn = QPushButton('ok', self)
        self.cancelBtn = QPushButton('cancel', self)
        self.initUI()

    def initUI(self):
        self.setFixedSize(200, 150)
        self.algorithmChoose.addButton(self.RadioBtn1, 0)
        self.algorithmChoose.addButton(self.RadioBtn2, 1)
        self.RadioBtn1.setChecked(True)
        self.cancelBtn.clicked.connect(self.close)

        layoutBox = QGridLayout()
        layoutBox.addWidget(self.RadioBtn1, 0, 0)
        layoutBox.addWidget(self.RadioBtn2, 0, 1)
        layoutBox.addWidget(self.okBtn, 1, 0)
        layoutBox.addWidget(self.cancelBtn, 1, 1)
        layoutBox.setSpacing(5)

        self.setLayout(layoutBox)


class LineDialog(AlgorithmDialog):
    def __init__(self):
        super().__init__()
        self.RadioBtn1.setText('DDA')
        self.RadioBtn2.setText('Bresenham')


class PolygonDialog(LineDialog):
    def __init__(self):
        super().__init__()
