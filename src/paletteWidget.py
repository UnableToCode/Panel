import copy
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.graph import Graph, MyLine, MyPolygon, MyEllipsis, MyCurve
from src.panelWidget import PanelWidget


class PaletteWidget(PanelWidget):
    FREE, LINE, POLYGON, ELLIPSIS, CURVE, TRANSLATE, ROTATE, SCALE, CLIP = range(9)

    def __init__(self):
        super().__init__()

        self.state = self.FREE
        self.selectGraphID = -1
        self.mousePressed = False
        self.algorithm = str()
        self.vertexes = list()
        self.tempGraph = dict()
        self.helpGraph = dict()
        self.tempPanel = QPixmap()

        self.resetDialog = ResetDialog()
        self.lineDialog = LineDialog()
        self.polygonDialog = PolygonDialog()
        self.curveDialog = CurveDialog()
        self.clipDialog = ClipDialog()
        self.selectDialog = SelectDialog()

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
        self.logger.info('init palette widget success')

    def initUI(self):
        self.setWindowTitle('Palette')
        self.setGeometry(400, 200, 800, 600)

        self.resetDialog.okBtn.clicked.connect(self.slotResetOkBtn)
        self.lineDialog.okBtn.clicked.connect(self.slotLineOkBtn)
        self.polygonDialog.okBtn.clicked.connect(self.slotPolygonOkBtn)
        self.curveDialog.okBtn.clicked.connect(self.slotCurveOkBtn)
        self.clipDialog.okBtn.clicked.connect(self.slotClipDialogOkBtn)
        self.selectDialog.graphTable.itemClicked.connect(self.slotClickedGraphList)

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
        self.drawEllipsisBtn.clicked.connect(self.slotEllipsisBtn)
        self.drawCurveBtn.setFixedSize(100, 20)
        self.drawCurveBtn.setText('draw curve')
        self.drawCurveBtn.clicked.connect(self.slotCurveBtn)
        self.translateBtn.setFixedSize(100, 20)
        self.translateBtn.setText('translate')
        self.translateBtn.clicked.connect(self.slotTranslateBtn)
        self.rotateBtn.setFixedSize(100, 20)
        self.rotateBtn.setText('rotate')
        self.rotateBtn.clicked.connect(self.slotRotateBtn)
        self.scaleBtn.setFixedSize(100, 20)
        self.scaleBtn.setText('scale')
        self.scaleBtn.clicked.connect(self.slotScaleBtn)
        self.clipBtn.setFixedSize(100, 20)
        self.clipBtn.setText('clip')
        self.clipBtn.clicked.connect(self.slotClipBtn)

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
            Graph.PANEL_WIDTH, Graph.PANEL_HEIGHT = w, h
            self.panelLabel.setGeometry(140, 20, w, h)
            self.graph.clear()
            self.panel.fill(Qt.white)
            self.panelLabel.setPixmap(self.panel)
            self.setGeometry(0, 0, winWidth, winHeight)
            self.putOnCenter()
            self.logger.info('reset Canvas success, w:{w} h:{h}'.format(w=w, h=h))

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

        elif self.state == self.ELLIPSIS:
            if len(self.vertexes) != 0:
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.tempGraph = self.graph.copy()
                x = (self.vertexes[0] + newX) / 2
                y = (self.vertexes[1] + newY) / 2
                a = abs(newX - self.vertexes[0]) / 2
                b = abs(newY - self.vertexes[1]) / 2
                self.tempGraph['temp'] = MyEllipsis(['temp', x, y, a, b], self.pen.color())
                self.drawTempGraph()

        elif self.state == self.CURVE:
            if len(self.vertexes) != 0:
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.tempGraph = self.graph.copy()
                self.tempGraph['temp'] = MyCurve(['temp', len(self.vertexes) // 2 + 1], self.pen.color(),
                                                 self.algorithm, self.vertexes + [newX, newY])
                self.drawTempGraph()

        elif self.state == self.TRANSLATE and self.mousePressed is True:
            newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
            newX = newPoint.x()
            newY = newPoint.y()
            dx = newX - self.vertexes[0]
            dy = newY - self.vertexes[1]
            self.tempGraph = self.helpGraph.copy()
            self.tempGraph[self.selectGraphID] = copy.deepcopy(self.tempGraph[self.selectGraphID])
            self.tempGraph[self.selectGraphID].translate(dx, dy)
            self.drawTempGraph()

        elif self.state == self.ROTATE and self.mousePressed is True:
            newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
            newX = newPoint.x()
            dx = newX - self.vertexes[0]
            self.tempGraph = self.helpGraph.copy()
            self.tempGraph[self.selectGraphID] = copy.deepcopy(self.tempGraph[self.selectGraphID])
            self.tempGraph[self.selectGraphID].rotate(self.vertexes[0], self.vertexes[1], dx)
            self.drawTempGraph()

        elif self.state == self.SCALE and self.mousePressed is True:
            newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
            newX = newPoint.x()
            dx = newX - self.vertexes[0]
            self.tempGraph = self.helpGraph.copy()
            self.tempGraph[self.selectGraphID] = copy.deepcopy(self.tempGraph[self.selectGraphID])
            self.tempGraph[self.selectGraphID].scale(self.vertexes[0], self.vertexes[1], 1 + dx / 50)
            self.drawTempGraph()

        elif self.state == self.CLIP:
            if len(self.vertexes) != 0:
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.tempGraph = self.graph.copy()
                self.tempGraph['rect'] = MyPolygon(['rect', 4], QColor(Qt.red), 'Bresenham',
                                                   self.vertexes + [self.vertexes[0], newY, newX, newY, newX,
                                                                    self.vertexes[1]])
                self.drawTempGraph()

    def mousePressEvent(self, event):
        if self.state == self.LINE and event.button() == Qt.LeftButton:
            newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
            newX = newPoint.x()
            newY = newPoint.y()
            self.vertexes += [newX, newY]
            self.logger.info('add new point: x:{x} y:{y}'.format(x=newX, y=newY))
            if len(self.vertexes) == 4:
                newID = len(self.graph)
                self.graph[newID] = MyLine([newID] + self.vertexes, self.pen.color(), self.algorithm)
                self.logger.info("draw new line, id:{id}".format(id=newID))
                self.quitDraw()

        elif self.state == self.POLYGON:
            if event.button() == Qt.LeftButton:
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.vertexes += [newX, newY]
                self.logger.info('add new point: x:{x} y:{y}'.format(x=newX, y=newY))
            elif event.button() == Qt.RightButton:
                if len(self.vertexes) > 2:
                    newID = len(self.graph)
                    self.graph[newID] = MyPolygon([newID, len(self.vertexes) // 2], self.pen.color(), self.algorithm,
                                                  self.vertexes)
                    self.logger.info("draw new polygon, id:{id}".format(id=newID))
                self.quitDraw()

        elif self.state == self.ELLIPSIS and event.button() == Qt.LeftButton:
            newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
            newX = newPoint.x()
            newY = newPoint.y()
            self.vertexes += [newX, newY]
            self.logger.info('add new point: x:{x} y:{y}'.format(x=newX, y=newY))
            if len(self.vertexes) == 4:
                newID = len(self.graph)
                x = (self.vertexes[0] + self.vertexes[2]) / 2
                y = (self.vertexes[1] + self.vertexes[3]) / 2
                a = abs(self.vertexes[2] - self.vertexes[0]) / 2
                b = abs(self.vertexes[3] - self.vertexes[1]) / 2
                self.graph[newID] = MyEllipsis([newID, x, y, a, b], self.pen.color())
                self.logger.info("draw new ellipsis, id:{id}".format(id=newID))
                self.quitDraw()

        elif self.state == self.CURVE:
            if event.button() == Qt.LeftButton:
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.vertexes += [newX, newY]
                self.logger.info('add new point: x:{x} y:{y}'.format(x=newX, y=newY))
            elif event.button() == Qt.RightButton:
                if len(self.vertexes) > 2:
                    newID = len(self.graph)
                    self.graph[newID] = MyCurve([newID, len(self.vertexes) // 2], self.pen.color(), self.algorithm,
                                                self.vertexes)
                    self.logger.info("draw new curve, id:{id}".format(id=newID))
                self.quitDraw()

        elif self.state == self.TRANSLATE:
            if event.button() == Qt.LeftButton:
                self.mousePressed = True
                self.panelLabel.setCursor(Qt.ClosedHandCursor)
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.vertexes = [newX, newY]
            elif event.button() == Qt.RightButton:
                self.graph = self.helpGraph
                self.logger.info("translate finished")
                self.quitDraw()

        elif self.state == self.ROTATE:
            if event.button() == Qt.LeftButton:
                self.mousePressed = True
                self.panelLabel.setCursor(Qt.SizeHorCursor)
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.vertexes = [newX, newY]
            elif event.button() == Qt.RightButton:
                self.graph = self.helpGraph
                self.logger.info("rotate finished")
                self.quitDraw()

        elif self.state == self.SCALE:
            if event.button() == Qt.LeftButton:
                self.mousePressed = True
                self.panelLabel.setCursor(Qt.SizeHorCursor)
                newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
                newX = newPoint.x()
                newY = newPoint.y()
                self.vertexes = [newX, newY]
            elif event.button() == Qt.RightButton:
                self.graph = self.helpGraph
                self.logger.info("scale finished")
                self.quitDraw()

        elif self.state == self.CLIP and event.button() == Qt.LeftButton:
            newPoint = self.panelLabel.mapFromParent(QPoint(event.pos().x(), event.pos().y()))
            newX = newPoint.x()
            newY = newPoint.y()
            self.vertexes += [newX, newY]
            self.logger.info('add new point: x:{x} y:{y}'.format(x=newX, y=newY))
            if len(self.vertexes) == 4:
                if self.graph[self.selectGraphID].clip(self.vertexes[0], self.vertexes[1], self.vertexes[2],
                                                       self.vertexes[3], self.algorithm) is False:
                    self.graph.pop(self.selectGraphID)
                self.logger.info('line clip finished')
                self.quitDraw()

    def mouseReleaseEvent(self, event):
        if self.state == self.TRANSLATE and event.button() == Qt.LeftButton:
            self.panelLabel.setCursor(Qt.OpenHandCursor)
            self.mousePressed = False
            self.helpGraph = self.tempGraph

        elif self.state == self.ROTATE and event.button() == Qt.LeftButton:
            self.panelLabel.setCursor(Qt.CrossCursor)
            self.mousePressed = False
            self.helpGraph = self.tempGraph

        elif self.state == self.SCALE and event.button() == Qt.LeftButton:
            self.panelLabel.setCursor(Qt.CrossCursor)
            self.mousePressed = False
            self.helpGraph = self.tempGraph

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.state != self.FREE:
            self.quitDraw()

    def drawTempGraph(self):
        self.panel.fill(Qt.white)
        painter = QPainter(self.panel)
        for graph in self.tempGraph.values():
            graph.draw(painter)
        self.panelLabel.setPixmap(self.panel)

    def quitDraw(self):
        self.setMouseTracking(False)
        self.panelLabel.setCursor(Qt.ArrowCursor)
        self.selectGraphID = -1
        self.vertexes.clear()
        self.drawGraph()
        # self.panelLabel.setPixmap(self.panel)
        self.state = self.FREE
        self.logger.info('quit drawing state')

    def selectListFilter(self, typeFilter):
        if typeFilter is None:
            typeFilter = range(4)

        self.selectGraphID = -1
        self.selectDialog.img.fill(Qt.white)
        self.selectDialog.imgLabel.setPixmap(self.selectDialog.img)
        self.selectDialog.graphTable.clearContents()
        self.selectDialog.graphTable.setRowCount(0)
        row = 0
        for graph in self.graph.values():
            if graph.graphType in typeFilter:
                rowCnt = self.selectDialog.graphTable.rowCount()
                self.selectDialog.graphTable.insertRow(rowCnt)
                item = QTableWidgetItem(str(graph.ID))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.selectDialog.graphTable.setItem(row, 0, item)
                if graph.graphType == graph.LINE:
                    item = QTableWidgetItem('Line')
                elif graph.graphType == graph.POLYGON:
                    item = QTableWidgetItem('Polygon')
                elif graph.graphType == graph.ELLIPSIS:
                    item = QTableWidgetItem('Ellipsis')
                elif graph.graphType == graph.CURVE:
                    item = QTableWidgetItem('Curve')
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.selectDialog.graphTable.setItem(row, 1, item)
                row += 1

    def slotResetBtn(self):
        self.resetDialog.widthInput.setText(str(self.panel.width()))
        self.resetDialog.heightInput.setText(str(self.panel.height()))
        self.resetDialog.exec_()

    def slotColorBtn(self):
        color = QColorDialog.getColor(self.pen.color())
        if color.isValid():
            self.pen.setColor(color)
            self.logger.info(
                'set color success, r:{r} g:{g} b:{b}'.format(r=color.red(), g=color.green(), b=color.blue()))

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
            self.logger.info('save image to {fileName}'.format(fileName=fileName))

    def slotLineBtn(self):
        self.lineDialog.exec_()

    def slotPolygonBtn(self):
        self.polygonDialog.exec_()

    def slotEllipsisBtn(self):
        self.logger.info('start draw ellipsis')
        self.panelLabel.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        self.state = self.ELLIPSIS

        QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                 self.panelLabel.y() + int(self.panelLabel.height() / 2))))

    def slotCurveBtn(self):
        self.curveDialog.exec_()

    def slotTranslateBtn(self):
        self.selectListFilter(None)
        self.selectDialog.setWindowTitle('Translate')
        self.selectDialog.okBtn.clicked.connect(self.slotTranslateOkBtn)
        self.selectDialog.show()

    def slotRotateBtn(self):
        self.selectListFilter(None)
        self.selectDialog.setWindowTitle('Rotate')
        self.selectDialog.okBtn.clicked.connect(self.slotRotateOkBtn)
        self.selectDialog.show()

    def slotScaleBtn(self):
        self.selectListFilter(None)
        self.selectDialog.setWindowTitle('Scale')
        self.selectDialog.okBtn.clicked.connect(self.slotScaleOkBtn)
        self.selectDialog.show()

    def slotClipBtn(self):
        self.clipDialog.exec_()

    def slotLineOkBtn(self):
        # print('self: x:{x} y:{y}'.format(x=self.x(), y=self.y()))
        # print('panelLabel: x:{x} y:{y} w:{w} h:{h}'.format(x=self.panelLabel.x(), y=self.panelLabel.y(),
        #                                                    w=self.panelLabel.width(), h=self.panelLabel.height()))
        self.logger.info('start draw line')
        self.panelLabel.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        self.state = self.LINE

        QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                 self.panelLabel.y() + int(self.panelLabel.height() / 2))))
        # if self.lineDialog.algorithmChoose.checkedId() == 0:
        #     self.algorithm = 'DDA'
        # else:
        #     self.algorithm = 'Bresenham'
        self.algorithm = self.lineDialog.algorithmChoose.checkedButton().text()
        # print(self.algorithm)
        self.lineDialog.close()

    def slotPolygonOkBtn(self):
        self.logger.info('start draw polygon')
        self.panelLabel.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        self.state = self.POLYGON

        QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                 self.panelLabel.y() + int(self.panelLabel.height() / 2))))
        # if self.polygonDialog.algorithmChoose.checkedId() == 0:
        #     self.algorithm = 'DDA'
        # else:
        #     self.algorithm = 'Bresenham'
        self.algorithm = self.polygonDialog.algorithmChoose.checkedButton().text()
        # print(self.algorithm)
        self.polygonDialog.close()

    def slotCurveOkBtn(self):
        self.logger.info('start draw curve')
        self.panelLabel.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        self.state = self.CURVE

        QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                 self.panelLabel.y() + int(self.panelLabel.height() / 2))))
        # if self.curveDialog.algorithmChoose.checkedId() == 0:
        #     self.algorithm = 'Bezier'
        # else:
        #     self.algorithm = 'B-spline'
        self.algorithm = self.curveDialog.algorithmChoose.checkedButton().text()
        # print(self.algorithm)
        self.curveDialog.close()

    def slotClipDialogOkBtn(self):
        # if self.clipDialog.algorithmChoose.checkedId() == 0:
        #     self.algorithm = 'Cohen-Sutherland'
        # else:
        #     self.algorithm = 'Liang-Barsky'
        self.algorithm = self.clipDialog.algorithmChoose.checkedButton().text()
        # print(self.algorithm)
        self.clipDialog.close()
        self.selectListFilter([Graph.LINE])
        self.selectDialog.setWindowTitle('Clip')
        self.selectDialog.okBtn.clicked.connect(self.slotClipOkBtn)
        self.selectDialog.show()

    def slotTranslateOkBtn(self):
        if self.selectGraphID == -1:
            self.logger.error('translate select nothing')
            QMessageBox.critical(None, "selected NULL",
                                 'select a graph to translate.')
        else:
            self.logger.info('start translate graph, ID:{id}'.format(id=self.selectGraphID))
            self.panelLabel.setCursor(Qt.OpenHandCursor)
            self.setMouseTracking(True)
            self.state = self.TRANSLATE
            self.helpGraph = self.graph.copy()
            self.helpGraph[self.selectGraphID] = copy.deepcopy(self.helpGraph[self.selectGraphID])
            QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                     self.panelLabel.y() + int(self.panelLabel.height() / 2))))
            self.selectDialog.close()

    def slotRotateOkBtn(self):
        if self.selectGraphID == -1:
            self.logger.error('rotate select nothing')
            QMessageBox.critical(None, "selected NULL",
                                 'select a graph to rotate.')
        else:
            self.logger.info('start rotate graph, ID:{id}'.format(id=self.selectGraphID))
            self.panelLabel.setCursor(Qt.CrossCursor)
            self.setMouseTracking(True)
            self.state = self.ROTATE
            self.helpGraph = self.graph.copy()
            self.helpGraph[self.selectGraphID] = copy.deepcopy(self.helpGraph[self.selectGraphID])
            QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                     self.panelLabel.y() + int(self.panelLabel.height() / 2))))
            self.selectDialog.close()

    def slotScaleOkBtn(self):
        if self.selectGraphID == -1:
            self.logger.error('scale select nothing')
            QMessageBox.critical(None, "selected NULL",
                                 'select a graph to scale.')
        else:
            self.logger.info('start scale graph, ID:{id}'.format(id=self.selectGraphID))
            self.panelLabel.setCursor(Qt.CrossCursor)
            self.setMouseTracking(True)
            self.state = self.SCALE
            self.helpGraph = self.graph.copy()
            self.helpGraph[self.selectGraphID] = copy.deepcopy(self.helpGraph[self.selectGraphID])
            QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                     self.panelLabel.y() + int(self.panelLabel.height() / 2))))
            self.selectDialog.close()

    def slotClipOkBtn(self):
        if self.selectGraphID == -1:
            self.logger.error('clip select nothing')
            QMessageBox.critical(None, "selected NULL",
                                 'select a line to clip.')
        else:
            self.logger.info('start clip graph, ID:{id}'.format(id=self.selectGraphID))
            self.panelLabel.setCursor(Qt.CrossCursor)
            self.setMouseTracking(True)
            self.state = self.CLIP
            QCursor().setPos(self.mapToGlobal(QPoint(self.panelLabel.x() + int(self.panelLabel.width() / 2),
                                                     self.panelLabel.y() + int(self.panelLabel.height() / 2))))
            self.selectDialog.close()

    def slotResetOkBtn(self):
        w = int(self.resetDialog.widthInput.text())
        h = int(self.resetDialog.heightInput.text())
        if w < 100 or h > 1000:
            self.logger.error('width or height out of range, w:{w} h:{h}'.format(w=w, h=h))
            QMessageBox.critical(None, "Out Of Range",
                                 'width or height out of range, width >= 100, height <= 1000, w:{w} h:{h}'
                                 .format(w=w, h=h))
            return
        self.reset(w, h)
        self.resetDialog.close()

    def slotClickedGraphList(self):
        rowSelected = self.selectDialog.graphTable.selectedItems()
        self.selectGraphID = int(rowSelected[0].text())
        self.tempPanel = QPixmap(self.panel.width(), self.panel.height())
        self.tempPanel.fill(Qt.white)
        painter = QPainter(self.tempPanel)
        self.graph[self.selectGraphID].draw(painter)
        self.selectDialog.img = self.tempPanel.scaled(QSize(200, 150), Qt.KeepAspectRatio | Qt.SmoothTransformation)
        self.selectDialog.imgLabel.setPixmap(self.selectDialog.img)


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
        self.radioBtn1 = QRadioButton(self)
        self.radioBtn2 = QRadioButton(self)
        self.okBtn = QPushButton('ok', self)
        self.cancelBtn = QPushButton('cancel', self)
        self.initUI()

    def initUI(self):
        self.setFixedSize(200, 100)
        self.algorithmChoose.addButton(self.radioBtn1, 0)
        self.algorithmChoose.addButton(self.radioBtn2, 1)
        self.algorithmChoose.setExclusive(True)
        self.radioBtn1.setChecked(True)
        self.cancelBtn.clicked.connect(self.close)

        layoutBox = QGridLayout()
        layoutBox.addWidget(self.radioBtn1, 0, 0)
        layoutBox.addWidget(self.radioBtn2, 0, 1)
        layoutBox.addWidget(self.okBtn, 1, 0)
        layoutBox.addWidget(self.cancelBtn, 1, 1)
        layoutBox.setSpacing(5)

        self.setLayout(layoutBox)


class LineDialog(AlgorithmDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Draw Line')
        self.radioBtn1.setText('DDA')
        self.radioBtn2.setText('Bresenham')


class PolygonDialog(LineDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Draw Polygon')


class CurveDialog(AlgorithmDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Draw Curve')
        self.radioBtn1.setText('Bezier')
        self.radioBtn2.setText('B-spline')


class ClipDialog(AlgorithmDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(250, 100)
        self.setWindowTitle('Clip Line')
        self.radioBtn1.setText('Cohen-Sutherland')
        self.radioBtn2.setText('Liang-Barsky')


class SelectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.graphTable = QTableWidget(self)
        self.imgLabel = QLabel(self)
        self.img = QPixmap(200, 150)
        self.okBtn = QPushButton(self)
        self.cancelBtn = QPushButton(self)
        self.initUI()

    def initUI(self):
        self.setFixedSize(400, 300)
        self.graphTable.setGeometry(30, 30, 120, 200)
        self.imgLabel.setGeometry(180, 60, 200, 150)

        self.okBtn.move(110, 260)
        self.okBtn.setText('ok')
        self.cancelBtn.move(210, 260)
        self.cancelBtn.setText('cancel')
        self.cancelBtn.clicked.connect(self.close)

        self.img.fill(Qt.white)
        self.imgLabel.setPixmap(self.img)

        self.graphTable.setColumnCount(2)
        self.graphTable.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置表格的选取方式是行选取
        self.graphTable.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置选取方式为单个选取
        self.graphTable.setHorizontalHeaderLabels(['ID', 'Type'])  # 设置行表头
        self.graphTable.verticalHeader().setVisible(False)  # 隐藏列表头
        self.graphTable.setFocusPolicy(Qt.ClickFocus)
        self.graphTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应列宽
        self.graphTable.setFont(QFont('宋体', 8))
