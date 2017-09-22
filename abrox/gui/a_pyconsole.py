from PyQt5.QtWidgets import QHBoxLayout, QWidget, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSize
from qtconsole.inprocess import QtInProcessKernelManager
from qtconsole.rich_jupyter_widget import RichJupyterWidget
import os


class AIPythonWidget(RichJupyterWidget):
    """Convenience class for a live IPython console widget. """

    def __init__(self, customBanner=None, *args, **kwargs):
        super(AIPythonWidget, self).__init__(*args, **kwargs)

        # Set banner
        if customBanner is not None:
            self.banner = customBanner

        # Configure kernel
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()
        self.exit_requested.connect(self.stop)

        # Change stylesheet
        self.style_sheet = "QPlainTextEdit, QTextEdit {"\
                           "background-color: #232629;"\
                           "background-clip: padding;"\
                           "color: #eff0f1;"\
                           "selection-background-color: #ccc;" \
                           "}"

        # Change font
        font = QFont()
        font.setFamily('Consolas')
        font.setPointSize(10)
        self.font = font

    def pushVariables(self, variableDict):
        """Given a dictionary containing name / value pairs, push those variables to the IPython console widget """

        self.kernel_manager.kernel.shell.push(variableDict)

    def removeVariable(self, variableName):
        """Given a variable name, deletes variable from namespace."""

        self._execute('del {}'.format(variableName), True)

    def clearTerminal(self):
        """ Clears the terminal """

        self._control.clear()

    def printText(self, text):
        """Prints some plain text to the console."""

        self._append_plain_text(text, True)

    def printHtml(self, html):
        """Prints html text to the console."""

        self._append_html(html, True)

    def executeCommand(self, command):
        """ Execute a command in the frame of the console widget """

        self._execute(command, False)

    def stop(self):
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()


class AConsoleWindow(QWidget):
    """Represents the text edit component used to display the output of the console."""
    def __init__(self, parent=None):
        super(AConsoleWindow, self).__init__(parent)

        self._ipythonConsole = AIPythonWidget()
        self._ipythonConsole.pushVariables({"print_process_id": os.getpid()})

        self._configureLayout()

    def _configureLayout(self):
        """Sets the layout of the window."""

        layout = QHBoxLayout()
        layout.addWidget(self._ipythonConsole)
        self.setLayout(layout)

    def addData(self, data):
        """Called on loading data. Pushes data to the console and informs for loading."""

        self._ipythonConsole.pushVariables({'data': data})

    def removeData(self):
        """Called on clear data. Executes del data in the terminal."""

        self._ipythonConsole.removeVariable('data')

    def addResults(self, results):

        self._ipythonConsole.pushVariables({'results': results})
        self._ipythonConsole.printText('\n')

    def sizeHint(self):
        """
        Re-implement the size hint in order to
        display the console as 1/3 of the screen.
        """

        return QSize(self.width(),
                     int(QApplication.desktop().screenGeometry().height()/3))