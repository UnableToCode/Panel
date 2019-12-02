import abc
from math import *

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.special import comb


class Graph:
    LINE, POLYGON, ELLIPSIS, CURVE = range(4)
    PANEL_WIDTH, PANEL_HEIGHT = 0, 0

    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    @abc.abstractmethod
    def draw(self, painter): pass

    @abc.abstractmethod
    def translate(self, dx, dy): pass

    @abc.abstractmethod
    def rotate(self, centerX, centerY, theta): pass

    @abc.abstractmethod
    def scale(self, centerX, centerY, scale): pass


class MyLine(Graph):
    def __init__(self, args, color, algorithm):
        self.graphType = Graph.LINE
        self.ID, x1, y1, x2, y2 = args
        self.vertexes = list()
        self.vertexes.append(Graph.Point(x1, y1))
        self.vertexes.append(Graph.Point(x2, y2))
        self.color = color
        self.algorithm = algorithm

    def draw(self, painter):

        xBegin, xEnd = self.vertexes[0].x, self.vertexes[1].x
        yBegin, yEnd = self.vertexes[0].y, self.vertexes[1].y

        pen = QPen(QColor(self.color), 2, Qt.SolidLine)
        painter.setPen(pen)

        if self.algorithm == 'DDA':
            # 取距离长的方向步进
            k = max(abs(xEnd - xBegin), abs(yEnd - yBegin))
            if k == 0:
                k = 1
            dx = (xEnd - xBegin) / k
            dy = (yEnd - yBegin) / k
            x = xBegin
            y = yBegin
            for i in range(k):
                painter.drawPoint(QPointF(x, y))
                x += dx
                y += dy

        elif self.algorithm == 'Bresenham':
            # 如果斜率大于1，则交换x,y方向，目的是取距离大的方向步进，
            revers = abs(yEnd - yBegin) > abs(xEnd - xBegin)
            if revers is True:
                xBegin, yBegin = yBegin, xBegin
                xEnd, yEnd = yEnd, xEnd
            # 从坐标值小的点像坐标值大的点步进
            if xEnd < xBegin:
                xBegin, xEnd = xEnd, xBegin
                yBegin, yEnd = yEnd, yBegin
            # 处理斜率正负情况下的步进方向
            if yBegin < yEnd:
                step = 1
            else:
                step = -1

            dx = xEnd - xBegin
            dy = abs(yEnd - yBegin)
            p = 2 * dy - dx
            twoDy = 2 * dy
            twoDyMinuDx = 2 * (dy - dx)
            x = xBegin
            y = yBegin
            while x <= xEnd:
                if p <= 0:
                    p += twoDy
                else:
                    y += step
                    p += twoDyMinuDx
                x += 1
                if revers is True:
                    painter.drawPoint(QPointF(y, x))
                else:
                    painter.drawPoint(QPointF(x, y))

    def translate(self, dx, dy):
        for vertex in self.vertexes:
            vertex.x += dx
            vertex.y += dy

    def rotate(self, centerX, centerY, theta):
        theta = radians(theta)
        for vertex in self.vertexes:
            originX, originY = vertex.x, vertex.y
            vertex.x = int((originX - centerX) * cos(theta) - (originY - centerY) * sin(theta)) + centerX
            vertex.y = int((originX - centerX) * sin(theta) + (originY - centerY) * cos(theta)) + centerY

    def scale(self, centerX, centerY, scale):
        for vertex in self.vertexes:
            vertex.x = int(centerX + (vertex.x - centerX) * scale)
            vertex.y = int(centerY + (vertex.y - centerY) * scale)

    def clip(self, x1, y1, x2, y2, algorithm):
        xMin = min(x1, x2)
        xMax = max(x1, x2)
        yMin = min(y1, y2)
        yMax = max(y1, y2)
        if algorithm == 'Cohen-Sutherland':
            lineCode = list()
            while True:
                lineCode.clear()
                for vertex in self.vertexes:
                    code = 0
                    if vertex.x < xMin:
                        code |= 1
                    if vertex.x > xMax:
                        code |= 1 << 1
                    if vertex.y < yMin:
                        code |= 1 << 2
                    if vertex.y > yMax:
                        code |= 1 << 3
                    lineCode.append(code)

                codeAnd = lineCode[0] & lineCode[1]
                codeOr = lineCode[0] | lineCode[1]

                # 整条线段在剪裁框外
                if codeAnd != 0:
                    return False
                # 整条线段在剪裁框内
                elif codeOr == 0:
                    return True
                else:
                    # 有一点在xMin左方
                    if codeOr & 1 != 0:
                        yNew = self.vertexes[0].y + (xMin - self.vertexes[0].x) * (
                                self.vertexes[1].y - self.vertexes[0].y) / (self.vertexes[1].x - self.vertexes[0].x)
                        if self.vertexes[0].x < xMin:
                            self.vertexes[0].x, self.vertexes[0].y = xMin, yNew
                        elif self.vertexes[1].x < xMin:
                            self.vertexes[1].x, self.vertexes[1].y = xMin, yNew
                    # 有一点在xMax右方
                    elif codeOr & 1 << 1 != 0:
                        yNew = self.vertexes[0].y + (xMax - self.vertexes[0].x) * (
                                self.vertexes[1].y - self.vertexes[0].y) / (self.vertexes[1].x - self.vertexes[0].x)
                        if self.vertexes[0].x > xMax:
                            self.vertexes[0].x, self.vertexes[0].y = xMax, yNew
                        elif self.vertexes[1].x > xMax:
                            self.vertexes[1].x, self.vertexes[1].y = xMax, yNew
                    # 有一点在yMin上方
                    elif codeOr & 1 << 2 != 0:
                        xNew = self.vertexes[0].x + (yMin - self.vertexes[0].y) / (
                                self.vertexes[1].y - self.vertexes[0].y) * (self.vertexes[1].x - self.vertexes[0].x)
                        if self.vertexes[0].y < yMin:
                            self.vertexes[0].x, self.vertexes[0].y = xNew, yMin
                        elif self.vertexes[1].y < yMin:
                            self.vertexes[1].x, self.vertexes[1].y = xNew, yMin
                    # 有一点在yMax下方
                    elif codeOr & 1 << 3 != 0:
                        xNew = self.vertexes[0].x + (yMax - self.vertexes[0].y) / (
                                self.vertexes[1].y - self.vertexes[0].y) * (self.vertexes[1].x - self.vertexes[0].x)
                        if self.vertexes[0].y > yMax:
                            self.vertexes[0].x, self.vertexes[0].y = xNew, yMax
                        elif self.vertexes[1].y > yMax:
                            self.vertexes[1].x, self.vertexes[1].y = xNew, yMax

                    # 将计算可能产生的小数坐标转整数
                    self.vertexes = list(
                        map(lambda _vertex: Graph.Point(int(_vertex.x), int(_vertex.y)), self.vertexes))

        elif algorithm == 'Liang-Barsky':
            uMin = 0
            uMax = 1
            p = [0] * 4
            q = [0] * 4

            p[0] = self.vertexes[0].x - self.vertexes[1].x
            p[1] = self.vertexes[1].x - self.vertexes[0].x
            p[2] = self.vertexes[0].y - self.vertexes[1].y
            p[3] = self.vertexes[1].y - self.vertexes[0].y

            q[0] = self.vertexes[0].x - xMin
            q[1] = xMax - self.vertexes[0].x
            q[2] = self.vertexes[0].y - yMin
            q[3] = yMax - self.vertexes[0].y

            for _pi, qi in zip(p, q):
                r = qi / _pi
                if _pi < 0:
                    uMin = max(uMin, r)
                elif _pi > 0:
                    uMax = min(uMax, r)
                elif qi < 0:
                    return False
                if uMin > uMax:
                    return False

            newVertexes = list()
            newVertexes.append(Graph.Point(int(self.vertexes[0].x - uMin * (self.vertexes[0].x - self.vertexes[1].x)),
                                           int(self.vertexes[0].y - uMin * (self.vertexes[0].y - self.vertexes[1].y))))
            newVertexes.append(Graph.Point(int(self.vertexes[0].x - uMax * (self.vertexes[0].x - self.vertexes[1].x)),
                                           int(self.vertexes[0].y - uMax * (self.vertexes[0].y - self.vertexes[1].y))))
            self.vertexes = newVertexes
            return True


class MyPolygon(Graph):
    def __init__(self, args, color, algorithm, vertexes):
        self.graphType = Graph.POLYGON
        self.ID, self.verNum = args
        self.color = color
        self.algorithm = algorithm
        self.lines = list()
        # xPos = vertexes[::2]
        # yPos = vertexes[1::2]
        vertexes += vertexes[:2]
        for i in range(self.verNum):
            # print(vertexes[i:i + 4])
            self.lines.append(MyLine([i] + vertexes[2 * i:2 * i + 4], color, algorithm))

    def draw(self, painter):
        for line in self.lines:
            line.draw(painter)

    def translate(self, dx, dy):
        for line in self.lines:
            line.translate(dx, dy)

    def rotate(self, centerX, centerY, theta):
        for line in self.lines:
            line.rotate(centerX, centerY, theta)

    def scale(self, centerX, centerY, scale):
        for line in self.lines:
            line.scale(centerX, centerY, scale)


class MyEllipsis(Graph):
    def __init__(self, args, color):
        self.graphType = Graph.ELLIPSIS
        self.ID, x, y, self.a, self.b = args
        self.center = Graph.Point(x, y)
        self.color = color
        self.rotateTheta = 0

    def __symmetryPix(self, painter, dx, dy):
        self.__drawPix(painter, self.center.x + dx, self.center.y + dy)
        self.__drawPix(painter, self.center.x + dx, self.center.y - dy)
        self.__drawPix(painter, self.center.x - dx, self.center.y + dy)
        self.__drawPix(painter, self.center.x - dx, self.center.y - dy)

    def __drawPix(self, painter, x, y):
        theta = radians(self.rotateTheta)
        originX, originY = x, y
        x = (originX - self.center.x) * cos(theta) - (originY - self.center.y) * sin(theta) + self.center.x
        y = (originX - self.center.x) * sin(theta) + (originY - self.center.y) * cos(theta) + self.center.y
        painter.drawPoint(QPointF(x, y))

    def draw(self, painter):
        pen = QPen(QColor(self.color), 2, Qt.SolidLine)
        painter.setPen(pen)

        aa, bb = self.a ** 2, self.b ** 2
        dx, dy = 0, self.b
        d = int(bb + aa * (-self.b + 0.25) + 0.5)

        # top half part
        while bb * dx < aa * dy:
            if d < 0:
                d += bb * (2 * dx + 3)
            else:
                d += bb * (2 * dx + 3) + aa * (-2 * dy + 2)
                dy -= 1
            dx += 1
            self.__symmetryPix(painter, dx, dy)

        d = int(bb * (dx + 0.5) ** 2 + aa * (dy - 1) ** 2 - aa * bb + 0.5)

        # half bottom
        while dy > 0:
            if d > 0:
                d += aa * (-2 * dy + 2)
            else:
                d += bb * (2 * dx + 3) + aa * (-2 * dy + 2)
                dx += 1
            dy -= 1
            self.__symmetryPix(painter, dx, dy)

    def translate(self, dx, dy):
        self.center.x += dx
        self.center.y += dy

    def rotate(self, centerX, centerY, theta):
        originX, originY = self.center.x, self.center.y
        self.rotateTheta = (self.rotateTheta + theta) % 360
        theta = radians(theta)
        self.center.x = int((originX - centerX) * cos(theta) - (originY - centerY) * sin(theta)) + centerX
        self.center.y = int((originX - centerX) * sin(theta) + (originY - centerY) * cos(theta)) + centerY

    def scale(self, centerX, centerY, scale):
        self.center.x = centerX + (self.center.x - centerX) * scale
        self.center.y = centerY + (self.center.y - centerY) * scale
        self.a *= scale
        self.b *= scale


class MyCurve(Graph):
    def __init__(self, args, color, algorithm, vertexes):
        self.graphType = Graph.CURVE
        self.ID, self.verNum = args
        self.color = color
        self.algorithm = algorithm
        self.vertexes = list()
        for i in range(self.verNum):
            self.vertexes.append(Graph.Point(vertexes[2 * i], vertexes[2 * i + 1]))

    def draw(self, painter):
        pen = QPen(QColor(self.color), 2, Qt.SolidLine)
        painter.setPen(pen)
        n = self.verNum - 1
        pointNum = (Graph.PANEL_WIDTH + Graph.PANEL_HEIGHT) * 2

        if self.algorithm == 'Bezier':
            for t in np.linspace(0, 1, pointNum):
                x, y = 0, 0
                for i, vertex in zip(range(self.verNum), self.vertexes):
                    x += comb(n, i) * vertex.x * ((1 - t) ** (n - i)) * (t ** i)
                    y += comb(n, i) * vertex.y * ((1 - t) ** (n - i)) * (t ** i)
                painter.drawPoint(QPointF(x, y))

        elif self.algorithm == 'B-spline':
            k = 3
            N = np.linspace(0, 1, n + k + 1)

            def deBoorX(r, u, i):
                if r == 0:
                    return self.vertexes[i].x
                else:
                    if N[i + k - r] - N[i] == 0:
                        a = 0
                    else:
                        a = (u - N[i]) / (N[i + k - r] - N[i])
                    if N[i + k - r] - N[i] == 0:
                        b = 0
                    else:
                        b = (N[i + k - r] - u) / (N[i + k - r] - N[i])
                    return a * deBoorX(r - 1, u, i) + b * deBoorX(r - 1, u, i - 1)

            def deBoorY(r, u, i):
                if r == 0:
                    return self.vertexes[i].y
                else:
                    if N[i + k - r] - N[i] == 0:
                        a = 0
                    else:
                        a = (u - N[i]) / (N[i + k - r] - N[i])
                    if N[i + k - r] - N[i] == 0:
                        b = 0
                    else:
                        b = (N[i + k - r] - u) / (N[i + k - r] - N[i])
                    return a * deBoorY(r - 1, u, i) + b * deBoorY(r - 1, u, i - 1)

            for i in range(k - 1, n + 1):
                for u in np.linspace(N[i], N[i + 1], pointNum // len(N)):
                    x = deBoorX(k - 1, u, i)
                    y = deBoorY(k - 1, u, i)
                    painter.drawPoint(QPointF(x, y))

    def translate(self, dx, dy):
        for vertex in self.vertexes:
            vertex.x += dx
            vertex.y += dy

    def rotate(self, centerX, centerY, theta):
        theta = radians(theta)
        for vertex in self.vertexes:
            originX, originY = vertex.x, vertex.y
            vertex.x = int((originX - centerX) * cos(theta) - (originY - centerY) * sin(theta)) + centerX
            vertex.y = int((originX - centerX) * sin(theta) + (originY - centerY) * cos(theta)) + centerY

    def scale(self, centerX, centerY, scale):
        for vertex in self.vertexes:
            vertex.x = int(centerX + (vertex.x - centerX) * scale)
            vertex.y = int(centerY + (vertex.y - centerY) * scale)
