from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


def drawFunc():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    # glOrtho(0.0, 100, 0.0, 100, -1.0, 1.0)
    glViewport(0, 0, 400, 400)
    gluOrtho2D(0, 100, 0, 100)

    # 设置点大小
    glPointSize(2)
    # 只绘制端点
    glBegin(GL_POINTS)
    # 第一个点
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(25, 25, 0)
    # 第二个点
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(75, 25, 0)
    # 第三个点
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(75, 75, 0)
    # 第四个点
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(50, 50, 0)
    glEnd()

    glFlush()


if __name__ == '__main__':
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
    glutInitWindowSize(400, 400)
    glutCreateWindow(b"First")
    glutDisplayFunc(drawFunc)
    glutMainLoop()
