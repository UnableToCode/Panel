import abc
from math import *

from OpenGL.GL import *


class Graph:
    LINE, POLYGON, ELLIPSIS, CURVE = range(4)

    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    @abc.abstractmethod
    def draw(self): pass

    @abc.abstractmethod
    def translate(self, dx, dy): pass

    @abc.abstractmethod
    def rotate(self, centerX, centerY, theta): pass

    @abc.abstractmethod
    def scale(self, centerX, centerY, scale): pass


class Line(Graph):
    def __init__(self, args, color, algorithm):
        self.graghType = Graph.LINE
        self.ID, x1, y1, x2, y2 = args
        self.vertexes = list()
        self.vertexes.append(Graph.Point(x1, y1))
        self.vertexes.append(Graph.Point(x2, y2))
        self.color = color
        self.algorithm = algorithm

    def draw(self):
        r, g, b = self.color
        glColor3f(r, g, b)
        xBegin, xEnd = self.vertexes[0].x, self.vertexes[1].x
        yBegin, yEnd = self.vertexes[0].y, self.vertexes[1].y
        if self.algorithm == "DDA":
            k = max(abs(xEnd - xBegin), abs(yEnd - yBegin))
            dx = (xEnd - xBegin) / k
            dy = (yEnd - yBegin) / k
            x = xBegin
            y = yBegin
            for i in range(k):
                glVertex2f(x, y)
                x += dx
                y += dy
        elif self.algorithm == "Bresenham":
            revers = abs(yEnd - yBegin) > abs(xEnd - xBegin)
            if revers is True:
                xBegin, yBegin = yBegin, xBegin
                xEnd, yEnd = yEnd, xEnd
            if xEnd < xBegin:
                xBegin, xEnd = xEnd, xBegin
                yBegin, yEnd = yEnd, yBegin
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
                    glVertex2f(y, x)
                else:
                    glVertex2f(x, y)

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


class Polygon(Graph):
    def __init__(self, args, color, algorithm, vertexes):
        self.graghType = Graph.POLYGON
        self.id, self.verNum = args
        self.color = color
        self.algorithm = algorithm
        self.lines = list()
        # xPos = vertexes[::2]
        # yPos = vertexes[1::2]
        vertexes += vertexes[:2]
        for i in range((len(vertexes) - 2) // 2):
            # print(vertexes[i:i + 4])
            self.lines.append(Line([i] + vertexes[2 * i:2 * i + 4], color, algorithm))

    def draw(self):
        for line in self.lines:
            line.draw()

    def translate(self, dx, dy):
        for line in self.lines:
            line.translate(dx, dy)

    def rotate(self, centerX, centerY, theta):
        for line in self.lines:
            line.rotate(centerX, centerY, theta)

    def scale(self, centerX, centerY, scale):
        for line in self.lines:
            line.scale(centerX, centerY, scale)


class Ellipsis(Graph):
    def __init__(self, args, color):
        self.id, x, y, self.a, self.b = args
        self.center = Graph.Point(x, y)
        self.color = color
        self.rotateTheta = 0

    def __symmetryPix(self, dx, dy):
        self.__drawPix(self.center.x + dx, self.center.y + dy)
        self.__drawPix(self.center.x + dx, self.center.y - dy)
        self.__drawPix(self.center.x - dx, self.center.y + dy)
        self.__drawPix(self.center.x - dx, self.center.y - dy)

    def __drawPix(self, x, y):
        theta = radians(self.rotateTheta)
        originX, originY = x, y
        x = (originX - self.center.x) * cos(theta) - (originY - self.center.y) * sin(theta) + self.center.x
        y = (originX - self.center.x) * sin(theta) + (originY - self.center.y) * cos(theta) + self.center.y
        glVertex2f(x, y)

    def draw(self):
        r, g, b = self.color
        glColor3f(r, g, b)
        aa, bb = self.a ** 2, self.b ** 2
        dx, dy = 0, self.b
        d = int(bb + aa * (-self.b + 0.25) + 0.5)

        # top half part
        while bb * dx < aa * dy:
            if d < 0:
                d += bb * (2 * dx + 3)
                dx += 1
            else:
                d += bb * (2 * dx + 3) + aa * (-2 * dy + 2)
                dx += 1
                dy -= 1
            self.__symmetryPix(dx, dy)

        d = int(bb * (dx + 0.5) ** 2 + aa * (dy - 1) ** 2 - aa * bb + 0.5)

        # half bottom 
        while dy > 0:
            if d > 0:
                d += aa * (-2 * dy + 2)
                dy -= 1
            else:
                d += bb * (2 * dx + 3) + aa * (-2 * dy + 2)
                dx += 1
                dy -= 1
            self.__symmetryPix(dx, dy)

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
