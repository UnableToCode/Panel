import datetime
import queue

from OpenGL.GLUT import *
from PyQt5.QtWidgets import *

from src.graph import *
from src.interpreter import *

# STDIN = 0
# FILEIN = 1
# STDOUT = 0
# FILEOUT = 1
IMAGE_FILE_PATH = '../pic/'


# LOG_FILE = '../logs/' + datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + '_log.self.logger.error'
#
# order_mod = FILEIN
# out_mode = FILEOUT


# def Log(*msg):
#     now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     if out_mode == STDOUT:
#         print()
#         print(now, ': ', *msg)
#     elif out_mode == FILEOUT:
#         with open(LOG_FILE, 'a') as write_log:
#             logMsg = str(now) + ': '
#             for i in msg:
#                 logMsg += str(i)
#             logMsg += '\n'
#             write_log.write(logMsg)

class PanelWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.panel = QPixmap(self.width(), self.height())
        self.panelLabel = QLabel(self)
        self.pen = QPen(Qt.black, 1.5, Qt.SolidLine)
        self.graph = dict()
        self.logger = logging.getLogger('Panel')
        self.logger.setLevel(logging.INFO)
        fmt = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                '%a, %d %b %Y %H:%M:%S')
        logFileName = '../logs/' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'
        fileHandle = logging.FileHandler(logFileName)
        fileHandle.setFormatter(fmt)
        self.logger.addHandler(fileHandle)
        # self.initUI()

        # TEST
        # painter = QPainter(self.panel)
        # painter.setPen(self.pen)
        # painter.drawLine(0, 0, self.width, self.height)
        # self.panelLabel.setPixmap(self.panel)

    def initUI(self):
        self.setGeometry(200, 200, 200, 200)
        self.putOnCenter()
        self.panelLabel.setGeometry(0, 0, self.width(), self.height())
        self.panel.fill(Qt.white)
        self.panelLabel.setPixmap(self.panel)
        self.show()

    def putOnCenter(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def reset(self, w, h):
        pass

    def fileModRun(self):
        self.__orderRun()
        self.__drawGragh()

    def drawGragh(self):
        self.panel.fill(Qt.white)
        painter = QPainter(self.panel)
        for gragh in self.graph.values():
            gragh.draw(painter)
        self.panelLabel.setPixmap(self.panel)

    # def paintGL(self):
    #     glPushMatrix()
    #     # glClearColor(1.0, 1.0, 1.0, 1.0)
    #     glClear(GL_COLOR_BUFFER_BIT)
    #     glViewport(0, 0, self.width, self.height)
    #     gluOrtho2D(0, self.width, self.height, 0)
    #
    #     glPointSize(1.5)
    #     glBegin(GL_POINTS)

    # for i in self.graph.values():
    #     i.draw()
    #
    # glEnd()
    # glPopMatrix()
    # glFlush()


class FilePanelWidget(PanelWidget):
    def __init__(self, parentWidget, filePath):
        super().__init__()
        self.fileIn = open(filePath)
        self.orders = queue.Queue()
        self.runningFlag = False
        self.parentWidget = parentWidget
        self.logger.addHandler(parentWidget.logHandle)
        self.orderInterpreter = Interpreter()
        self.numberPattern = re.compile(r'\d+')  # for split number string

        self.logger.info("Panel init success.")

        self.initUI()

    def reset(self, w, h):
        if w < 100 or h > 1000:
            self.logger.error('width or height out if range, width >= 100, height <= 1000, w:{w} h:{h}'
                              .format(w=w, h=h))
        else:
            self.setGeometry(0, 0, w, h)
            self.putOnCenter()
            self.panel = QPixmap(w, h)
            self.panel.fill(Qt.white)
            self.graph.clear()
            self.panelLabel.setGeometry(0, 0, w, h)
            self.panelLabel.setPixmap(self.panel)

            # glClearColor(1.0, 1.0, 1.0, 1.0)
            # glClear(GL_COLOR_BUFFER_BIT)

    def __getOrders(self):
        ordersList = self.fileIn.read().splitlines()
        for order in ordersList:
            self.orders.put(order)
        self.runningFlag = True

    def run(self):
        self.__getOrders()
        while self.runningFlag:
            self.__orderRun()
            super().drawGragh()

    def __orderRun(self):
        if self.orders.empty() is False:
            order = self.orders.get()
            retItem = self.orderInterpreter.interpretOrder(order)
            if retItem is None:
                self.logger.error('Error order:{order}'.format(order=order))
            elif retItem.orderType is Interpreter.RESET:
                # w, h = [int(i) for i in retItem.args]
                w, h = map(int, retItem.args)
                self.reset(w, h)
                self.logger.info('reshape w:{w} h:{h}'.format(w=w, h=h))
            elif retItem.orderType is Interpreter.COLOR:
                r, g, b = [int(i) for i in retItem.args]
                # rgb = list(map(int, retItem.args))
                self.pen.setColor(QColor(r, g, b))
                self.logger.info('set Color r:{r} g:{g} b:{b}'.format(r=r, g=g, b=b))
            elif retItem.orderType is Interpreter.SAVE:
                saveFile = QFile(IMAGE_FILE_PATH + retItem.args[0] + '.bmp')
                saveFile.open(QIODevice.WriteOnly)
                self.panel.save(saveFile, 'BMP')
                saveFile.close()
                self.logger.info('Save success as {filename}.bmp'.format(filename=retItem.args[0]))
            elif retItem.orderType is Interpreter.LINE:
                Id = retItem.args[0]
                if Id in self.graph:
                    self.logger.error('Error: draw line failed, ID:{ID} exist'.format(ID=Id))
                else:
                    algorithm = retItem.args.pop()
                    if algorithm != 'DDA' and algorithm != 'Bresenham':
                        self.logger.error("Error: draw line failed, unknown algorithm: {algorithm},"
                                          " expected 'DDA' or 'Bresenham'".
                                          format(algorithm=algorithm))
                    else:
                        self.graph[Id] = MyLine(list(map(int, retItem.args)), self.pen.color(), algorithm)
                        self.logger.info('draw line success id:{ID}'.format(ID=Id))
            elif retItem.orderType is Interpreter.POLYGON:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id in self.graph:
                    self.logger.error('Error: draw polygon failed, ID:{ID} exist'.format(ID=Id))
                else:
                    vertexesStr = retItem.args.pop()
                    algorithm = retItem.args.pop()
                    vertexes = list(map(int, self.numberPattern.findall(vertexesStr)))
                    if algorithm != 'DDA' and algorithm != 'Bresenham':
                        self.logger.error("Error: draw polygon failed, unknown algorithm: {algorithm},"
                                          " expected 'DDA' or 'Bresenham'".
                                          format(algorithm=algorithm))
                    elif len(vertexes) != 2 * int(retItem.args[1]):
                        self.logger.error('Error: number of vertexes position args is wrong,'
                                          ' expected {expectedNum} got {actualNum}'.
                                          format(expectedNum=2 * int(retItem.args[1]), actualNum=len(vertexes)))
                    else:
                        self.graph[Id] = MyPolygon(list(map(int, retItem.args)), self.pen.color(), algorithm, vertexes)
                        self.logger.info('draw Polygon success id:{ID}'.format(ID=Id))
            elif retItem.orderType is Interpreter.ELLIPSIS:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id in self.graph:
                    self.logger.error('Error: draw ellipsis failed, ID:{ID} exist'.format(ID=Id))
                else:
                    self.graph[Id] = MyEllipsis(list(map(int, retItem.args)), self.pen.color())
                    self.logger.info('draw Ellipsis success id:{ID}'.format(ID=Id))

            elif retItem.orderType is Interpreter.CURVE:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id in self.graph:
                    self.logger.error('Error: draw curve failed, ID:{ID} exist'.format(ID=Id))
                else:
                    vertexesStr = retItem.args.pop()
                    algorithm = retItem.args.pop()
                    verNum = int(retItem.args[1])
                    vertexes = list(map(int, self.numberPattern.findall(vertexesStr)))
                    if algorithm != 'Bezier' and algorithm != 'B-spline':
                        self.logger.error("Error: draw curve failed, unknown algorithm: {algorithm},"
                                          " expected 'Bezier' or 'B-spline'".
                                          format(algorithm=algorithm))
                    elif verNum < 2:
                        self.logger.error("Error: draw curve failed, at least 3 points, got {verNum}"
                                          .format(verNum=verNum))
                    elif len(vertexes) != 2 * int(retItem.args[1]):
                        self.logger.error('Error: number of vertexes position args is wrong,'
                                          'expected {expectedNum} got {actualNum}'.
                                          format(expectedNum=2 * int(retItem.args[1]), actualNum=len(vertexes)))
                    else:
                        self.graph[Id] = Curve(list(map(int, retItem.args)), self.pen.color(), algorithm, vertexes)
                        self.logger.info('draw Curve success id:{ID}'.format(ID=Id))

            elif retItem.orderType is Interpreter.TRANSLATE:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id not in self.graph:
                    self.logger.error("Error: translate failed,ID:{ID} don't exist".format(ID=Id))
                else:
                    dx, dy = map(int, retItem.args[1:3])
                    self.graph[Id].translate(dx, dy)
                    self.logger.info('Translate success id:{ID}'.format(ID=Id))
            elif retItem.orderType is Interpreter.ROTATE:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id not in self.graph:
                    self.logger.error("Error: rotate failed,ID:{ID} don't exist".format(ID=Id))
                else:
                    centerX, centerY, theta = map(int, retItem.args[1:4])
                    self.graph[Id].rotate(centerX, centerY, theta)
                    self.logger.info('Rotate success id:{ID}'.format(ID=Id))
            elif retItem.orderType is Interpreter.SCALE:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id not in self.graph:
                    self.logger.error("Error: scale failed,ID:{ID} don't exist".format(ID=Id))
                else:
                    centerX, centerY = map(int, retItem.args[1:3])
                    scale = float(retItem.args[3])
                    self.graph[Id].scale(centerX, centerY, scale)
                    self.logger.info('Scale success id:{ID}'.format(ID=Id))
            elif retItem.orderType is Interpreter.CLIP:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id not in self.graph:
                    self.logger.error("Error: clip failed,ID:{ID} don't exist".format(ID=Id))
                elif self.graph[Id].graphType is not Graph.LINE:
                    self.logger.error("Error: clip graph (ID:{ID}) type is wrong, expected Line but got {className}".
                                      format(ID=Id, className=self.graph[Id].__class__.__name__))
                else:
                    algorithm = retItem.args.pop()
                    if algorithm != 'Cohen-Sutherland' and algorithm != 'Liang-Barsky':
                        self.logger.error("Error: clip line failed, unknown algorithm: {algorithm}, "
                                          "expected 'Cohen-Sutherland' or 'Liang-Barsky'".
                                          format(algorithm=algorithm))
                    else:
                        x1, y1, x2, y2 = list(map(int, retItem.args[1:5]))
                        if self.graph[Id].clip(x1, y1, x2, y2, algorithm) is False:
                            self.graph.pop(Id)
                        self.logger.info("Clip success, id:{ID}".format(ID=Id))

        else:
            self.logger.info("finished.")
            reply = QMessageBox.information(None,
                                            "finished",
                                            "file run done!",
                                            QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.runningFlag = False
                self.parentWidget.finishBtn.setEnabled(True)
                self.deleteLater()
                self.close()
