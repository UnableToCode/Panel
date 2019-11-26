import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.fileWidget import FileWidget
from src.paletteWidget import PaletteWidget


class MainWindow(QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()

        self.newPanelBtn = QPushButton(self)
        self.fileReadBtn = QPushButton(self)
        self.quitBtn = QPushButton(self)
        self.hideBtn = QPushButton(self)

        self.paletteWidget = PaletteWidget()

        self.initUI()

    def initUI(self):
        # set main windows geometry and style
        self.setFixedSize(320, 180)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.resize(320, 180)
        self.putOnCenter()

        self.quitBtn.setGeometry(self.width() - 20, 0, 20, 20)
        self.quitBtn.setStyleSheet("background-color:transparent; border-width:0;")
        quitIcon = QIcon("../res/exit.png")
        self.quitBtn.setIcon(quitIcon)
        self.quitBtn.setIconSize(QSize(20, 20))
        self.quitBtn.setText("")
        self.quitBtn.clicked.connect(self.slotOnQuitClick)

        self.hideBtn.setGeometry(self.width() - 50, 0, 20, 20)
        self.hideBtn.setStyleSheet("background-color:transparent; border-width:0;")
        hideIcon = QIcon("../res/hide.png")
        self.hideBtn.setIcon(hideIcon)
        self.hideBtn.setIconSize(QSize(20, 20))
        self.hideBtn.setText("")
        self.hideBtn.clicked.connect(self.showMinimized)

        # set btn geometry
        self.newPanelBtn.resize(150, 50)
        self.newPanelBtn.move((self.width() - self.newPanelBtn.width()) / 2,
                              (self.height() / 2 - self.newPanelBtn.height()) / 2)
        self.newPanelBtn.setText("New Panel")
        self.newPanelBtn.clicked.connect(self.slotNewPanelBtn)

        self.fileReadBtn.resize(150, 50)
        self.fileReadBtn.move((self.width() - self.fileReadBtn.width()) / 2,
                              (self.height() / 2 - self.fileReadBtn.height()) / 2 + self.height() / 2)
        self.fileReadBtn.setText("File input")
        self.fileReadBtn.clicked.connect(self.slotFileInputBtn)

    # 重写三个方法使我们的Example窗口支持拖动,上面参数window就是拖动对象
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_drag:
            self.move(QMouseEvent.globalPos() - self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def putOnCenter(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def slotNewPanelBtn(self):
        self.paletteWidget.reset(400, 400)
        self.paletteWidget.pen.setColor(Qt.black)
        self.paletteWidget.show()

    def slotFileInputBtn(self):
        fileWidget = FileWidget(self)
        fileWidget.exec_()

    def slotOnQuitClick(self):
        reply = QMessageBox.question(self,
                                     'Exit',
                                     "Quit？",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            os._exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
