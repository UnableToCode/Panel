import os

from PyQt5.QtWidgets import *

from src.panelWidget import FilePanelWidget, logging


class FileWidget(QDialog):
    class LogHandle(logging.Handler):
        def __init__(self, outLabel):
            super().__init__()
            self.outLabel = outLabel
            fmt = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                    '%a, %d %b %Y %H:%M:%S')
            self.setFormatter(fmt)

        def emit(self, record):
            if type(self.outLabel) is QPlainTextEdit:
                msg = self.format(record)
                self.outLabel.appendPlainText(msg)

    def __init__(self, parent):
        # noinspection PyArgumentList
        super().__init__()
        self.parent = parent
        self.cwd = os.getcwd()
        self.chooseFileBtn = QPushButton(self)
        self.filePathInput = QLineEdit(self)
        self.logText = QPlainTextEdit(self)
        self.finishBtn = QPushButton(self)
        self.checkBtn = QPushButton(self)
        self.returnBtn = QPushButton(self)
        self.logHandle = self.LogHandle(self.logText)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('file input')
        self.setFixedSize(400, 300)
        self.putOnCenter()

        self.chooseFileBtn.resize(80, 20)
        self.chooseFileBtn.move(20, 20)
        self.chooseFileBtn.setText('Choose File')
        self.chooseFileBtn.clicked.connect(self.slotChooseFileBtn)

        self.filePathInput.resize(270, 20)
        self.filePathInput.move(110, 20)
        # TEST
        # filePath = 'H:/PycharmProjects/CG_exp/input.txt'
        # self.filePathInput.setText(filePath)

        self.logText.resize(360, 200)
        self.logText.move(20, 50)
        self.logText.setReadOnly(True)

        self.finishBtn.resize(80, 20)
        self.finishBtn.move(60, 260)
        self.finishBtn.setText('Finish')
        self.finishBtn.setEnabled(False)
        self.finishBtn.clicked.connect(self.close)

        self.checkBtn.resize(80, 20)
        self.checkBtn.move(160, 260)
        self.checkBtn.setText('OK')
        self.checkBtn.clicked.connect(self.slotCheckBtn)

        self.returnBtn.resize(80, 20)
        self.returnBtn.move(260, 260)
        self.returnBtn.setText('Cancel')
        self.returnBtn.clicked.connect(self.close)

        self.show()

    def putOnCenter(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def slotChooseFileBtn(self):
        # fileDialog = QFileDialog()
        # fileDialog.setFileMode(QFileDialog.AnyFile)
        # fileDialog.setFilter("Text Files (*.txt)")
        # fileDialog.setDirectory(self.cwd)
        # fileDialog.exec_()
        filePath, _ = QFileDialog.getOpenFileName(parent=self,
                                                  caption="选取文件",
                                                  directory=self.cwd,  # 起始路径
                                                  filter="Text Files (*.txt)")  # 设置文件扩展名过滤,用双分号间隔
        # print(filePath)
        self.filePathInput.setText(filePath)

    def slotCheckBtn(self):
        filePath = self.filePathInput.text()
        if filePath == '':
            QMessageBox.critical(None, "None Files chosen Error", "Please choose input file!")
            return
        if os.path.exists(filePath) is False:
            QMessageBox.critical(None, "Files Not Exist Error", "Please input right file path!")
            return
        if filePath[-4:] != '.txt':
            QMessageBox.critical(None, "Files Type Error", "Please choose Text Files (*.txt)!")
            return
        self.checkBtn.setEnabled(False)
        self.chooseFileBtn.setEnabled(False)
        self.filePathInput.setEnabled(False)
        self.returnBtn.setEnabled(False)
        self.logText.appendPlainText("choose file:" + filePath)
        self.logText.appendPlainText("run panel")

        self.filePanel = FilePanelWidget(self, filePath)
        self.filePanel.run()
