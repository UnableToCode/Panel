import datetime
import queue
import threading
import time

import cv2
import numpy as np
from OpenGL.GLU import *
from OpenGL.GLUT import *

from src.graph import *
from src.interpreter import *

STDIN = 0
FILEIN = 1
STDOUT = 0
FILEOUT = 1
IMAGE_FILE = '../pic/'
LOG_FILE = '../log.log'

order_mod = FILEIN
out_mode = FILEOUT

if out_mode == FILEOUT:
    fileClear = open(LOG_FILE, 'w')
    fileClear.close()


def Log(*msg):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if out_mode == STDOUT:
        print()
        print(now, ': ', *msg)
    elif out_mode == FILEOUT:
        with open(LOG_FILE, 'a+') as write_log:
            logMsg = str(now) + ': '
            for i in msg:
                logMsg += str(i)
            logMsg += '\n'
            write_log.write(logMsg)


class Panel:
    class Brush:
        def __init__(self, r=0, g=0, b=0):
            self.color = [r, g, b]

        def setColor(self, rgb):
            self.color = rgb

    def __init__(self, w, h):
        if w < 100 or h > 1000:
            raise OutOfRange('width or height out if range, width >= 100, height <= 1000, w:{w} h:{h}'.format(w=w, h=h))
        else:
            if order_mod == FILEIN:
                self.f = open('../input.txt')
            self.orders = queue.Queue()
            self.width, self.height = w, h
            self.graph = dict()
            self.brush = self.Brush()
            self.orderInterpreter = Interpreter()
            self.numberPattern = re.compile(r'\d+')  # for split number string
            inputThreading = threading.Thread(target=self.inputThread)
            inputThreading.setDaemon(True)
            glutInit()
            glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
            glutInitWindowSize(w, h)
            glutCreateWindow(b"Panel")
            glutDisplayFunc(self.display)
            # glutIdleFunc(self.display)
            glutCloseFunc(self.quitFunc)
            # glutReshapeFunc(self.reshape)
            inputThreading.start()
            glutMainLoop()

    def reset(self, w, h):
        if w < 100 or h > 1000:
            raise OutOfRange('width or height out if range, width >= 100, height <= 1000, w:{w} h:{h}'.format(w=w, h=h))
        else:
            self.width, self.height = w, h
            self.graph.clear()
            # glClearColor(1.0, 1.0, 1.0, 1.0)
            # glClear(GL_COLOR_BUFFER_BIT)

    def reshape(self, w, h):
        self.width = w
        self.height = h
        glViewport(0, 0, w, h)
        gluOrtho2D(0, w, 0, h)

    def display(self):
        if self.orders.empty() is False:
            order = self.orders.get()
            retItem = self.orderInterpreter.interpretOrder(order)
            if retItem is None:
                Log('Error order:{order}'.format(order=order))
            elif retItem.orderType is Interpreter.RESET:
                # w, h = [int(i) for i in retItem.args]
                w, h = map(int, retItem.args)
                self.reset(w, h)
                Log('reshape w:{w} h:{h}'.format(w=w, h=h))
            elif retItem.orderType is Interpreter.COLOR:
                # r, g, b = [int(i) for i in retItem.args]
                rgb = list(map(int, retItem.args))
                self.brush.setColor(rgb)
                Log('set Color r:{r} g:{g} b:{b}'.format(r=rgb[0], g=rgb[1], b=rgb[2]))
            elif retItem.orderType is Interpreter.SAVE:
                glReadBuffer(GL_FRONT)
                data = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
                arr = np.zeros((self.width * self.height * 3), dtype=np.uint8)
                # RGB(OpenGL) to BGR(OpenCV)
                for i in range(0, len(data), 3):
                    arr[i] = data[i + 2]
                    arr[i + 1] = data[i + 1]
                    arr[i + 2] = data[i]
                arr = np.reshape(arr, (self.height, self.width, 3))
                cv2.flip(arr, 0, arr)
                # cv2.imshow('test', arr)
                # cv2.waitKey(1)
                cv2.imwrite(IMAGE_FILE + retItem.args[0] + '.bmp', arr)
                Log('Save success as {filename}.bmp'.format(filename=retItem.args[0]))
            elif retItem.orderType is Interpreter.LINE:
                Id = retItem.args[0]
                if Id in self.graph:
                    Log('Error: draw line failed, ID:{ID} exist'.format(ID=Id))
                else:
                    algorithm = retItem.args.pop()
                    if algorithm != 'DDA' and algorithm != 'Bresenham':
                        Log(
                            "Error: draw line failed, unknown algorithm: {algorithm}, excepted 'DDA' or 'Bresenham'".
                                format(algorithm=algorithm))
                    else:
                        self.graph[Id] = Line(list(map(int, retItem.args)), self.brush.color, algorithm)
                        Log('draw line success id:{ID}'.format(ID=Id))
            elif retItem.orderType is Interpreter.POLYGON:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id in self.graph:
                    Log('Error: draw polygon failed, ID:{ID} exist'.format(ID=Id))
                else:
                    vertexesStr = retItem.args.pop()
                    algorithm = retItem.args.pop()
                    vertexes = list(map(int, self.numberPattern.findall(vertexesStr)))
                    if algorithm != 'DDA' and algorithm != 'Bresenham':
                        Log(
                            "Error: draw line failed, unknown algorithm: {algorithm}, excepted 'DDA' or 'Bresenham'".
                                format(algorithm=algorithm))
                    elif len(vertexes) != 2 * int(retItem.args[1]):
                        Log(
                            'Error: number of vertexes position args is wrong,expected {expectedNum} got {actualNum}'.
                                format(expectedNum=len(vertexes), actualNum=2 * int(retItem.args[1])))
                    else:
                        self.graph[Id] = Polygon(list(map(int, retItem.args)), self.brush.color, algorithm, vertexes)
                        Log('draw Polygon success id:{ID}'.format(ID=Id))
            elif retItem.orderType is Interpreter.ELLIPSIS:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id in self.graph:
                    Log('Error: draw ellipsis failed, ID:{ID} exist'.format(ID=Id))
                else:
                    self.graph[Id] = Ellipsis(list(map(int, retItem.args)), self.brush.color)
                    Log('draw Ellipsis success id:{ID}'.format(ID=Id))

            elif retItem.orderType is Interpreter.CURVE:
                Log('draw Curve success id:')
                Log(str(retItem.args))
                pass
            elif retItem.orderType is Interpreter.TRANSLATE:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id not in self.graph:
                    Log("Error: translate failed,ID:{ID} don't exist".format(ID=Id))
                else:
                    dx, dy = map(int, retItem.args[1:3])
                    self.graph[Id].translate(dx, dy)
                    Log('Translate success id:{ID}'.format(ID=Id))
            elif retItem.orderType is Interpreter.ROTATE:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id not in self.graph:
                    Log("Error: translate failed,ID:{ID} don't exist".format(ID=Id))
                else:
                    centerX, centerY, theta = map(int, retItem.args[1:4])
                    self.graph[Id].rotate(centerX, centerY, theta)
                    Log('Rotate success id:{ID}'.format(ID=Id))
            elif retItem.orderType is Interpreter.SCALE:
                # Log(str(retItem.args))
                Id = retItem.args[0]
                if Id not in self.graph:
                    Log("Error: translate failed,ID:{ID} don't exist".format(ID=Id))
                else:
                    centerX, centerY = map(int, retItem.args[1:3])
                    scale = float(retItem.args[3])
                    self.graph[Id].scale(centerX, centerY, scale)
                    Log('Scale success id:{ID}'.format(ID=Id))
            elif retItem.orderType is Interpreter.CLIP:
                Log('clip success id:')
                Log(str(retItem.args))
                pass

        glPushMatrix()
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glViewport(0, 0, self.width, self.height)
        gluOrtho2D(0, self.width, self.height, 0)

        glPointSize(1.5)
        glBegin(GL_POINTS)

        for i in self.graph.values():
            i.draw()

        glEnd()
        glPopMatrix()
        glFlush()

    def inputThread(self):
        reading = True
        while reading:
            if order_mod == STDIN:
                order = input('input order:')
                if order != '':
                    self.orders.put(order)
            elif order_mod == FILEIN:
                ordersList = self.f.readlines()
                for order in ordersList:
                    self.orders.put(order)
                reading = False
            time.sleep(1)

    def quitFunc(self):
        if order_mod == FILEIN:
            self.f.close()


class OutOfRange(RuntimeError):
    def __init__(self, args):
        self.args = args


if __name__ == '__main__':
    panel = Panel(100, 100)
