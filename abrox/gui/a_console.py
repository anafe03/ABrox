from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class AConsoleWindow(QTextEdit):
    BGCOLOR = QColor(211, 211, 211, 25)

    def __init__(self, parent=None, font=None):
        super(AConsoleWindow, self).__init__(parent)

        self.setReadOnly(True)

        # Change font
        if font is None:
            font = QFont()
            font.setFamily('Consolas')
            font.setPointSize(10)
        self.setFont(font)

    def paintEvent(self, event):
        """Draws background lines behind text."""

        painter = QPainter()
        painter.begin(self.viewport())
        brush = QBrush(AConsoleWindow.BGCOLOR)
        brush.setStyle(Qt.CrossPattern)
        painter.setBrush(brush)
        painter.fillRect(event.rect(), brush)
        painter.end()
        QTextEdit.paintEvent(self, event)


class AOutputConsole(QWidget):

    greeting = '<font color="#dce582" style="text-transform:uppercase;"> {} Welcome to ABrox! {}</font><br>'.\
                                    format('*'*5, '*'*5)
    defaultColor = QColor(239, 240, 241)
    warningColor = QColor(244, 241, 41)
    errorColor = QColor(244, 4, 44)

    def __init__(self, internalModel, parent=None):
        super(AOutputConsole, self).__init__(parent)

        self._internalModel = internalModel
        self._consoleWindow = AConsoleWindow()
        self._consoleTools = None
        self._initConsole()
        self._greet()

    def _initConsole(self):

        self._configureLayout(QHBoxLayout())

    def _configureLayout(self, layout):

        layout.addWidget(self._consoleWindow)
        self.setLayout(layout)

    def _greet(self):
        """Write greeting message to console."""

        self._consoleWindow.append(AOutputConsole.greeting)
        self._align(Qt.AlignCenter)

    def _align(self, alignment):
        cursor = self._consoleWindow.textCursor()
        block = cursor.blockFormat()
        block.setAlignment(alignment)
        cursor.mergeBlockFormat(block)
        self._consoleWindow.setTextCursor(cursor)

    def clearContents(self):
        """Clears all text from console."""

        self._consoleWindow.setText("")
        self._greet()

    def exportContents(self):
        """Opens up a dialog and asks user whether to save or not."""

        # Create dialog
        saveDialog = QFileDialog()
        saveDialog.setAcceptMode(QFileDialog.AcceptSave)
        saveName = saveDialog.getSaveFileName(self, "Save Console Contents as...",
                                              "", ".txt")

        # If user has chosen something
        if saveName[0]:
            with open(saveName[0] + saveName[1], 'w') as outfile:
                txt = self._consoleWindow.toPlainText()
                dummy = '***** Welcome to ABrox! *****\n'
                txt = txt.replace(dummy, '')
                outfile.write(txt)

    def write(self, txt):
        """Called externally to write a message."""

        self._consoleWindow.setTextColor(AOutputConsole.defaultColor)
        self._consoleWindow.append(txt)
        self._align(Qt.AlignLeft)

    def writeError(self, err):
        """Called externally to write an error."""

        self._consoleWindow.setTextColor(AOutputConsole.errorColor)
        self._consoleWindow.append(err)
        self._align(Qt.AlignLeft)

    def writeWarning(self, err):
        """Called externally to write a warning to console."""

        self._consoleWindow.setTextColor(AOutputConsole.warningColor)
        self._consoleWindow.append(err)
        self._align(Qt.AlignLeft)

    def sizeHint(self):
        """Used to make run button visible by shrinking console to 1/5 of display height."""

        screenHeight = QApplication.desktop().screenGeometry().height()
        return QSize(self.width(), screenHeight // 5)
