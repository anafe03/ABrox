from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal
import sys
import subprocess
import tempfile


class AProcessManager:
    """
    Starts a new process with script name. Assumes
    that scripName is the absolute path of a runnable python script.
    Uses a QProcess instance to manage the process.
    """
    def __init__(self, parent, internalModel, console, outputConsole):

        # Create instances
        self._parent = parent
        self._internalModel = internalModel
        self._outputConsole = outputConsole
        self._console = console
        self._flag = {"run": False}
        self._runThread = QThread()
        self._abcProcess = APythonAbcProcess(self._flag)

        self._prepareProcess()

    def _prepareProcess(self):
        """Connect the abc python process handler to the thread object."""

        # Move process to thread (essentially moving run method)
        self._abcProcess.moveToThread(self._runThread)
        # Connect signals
        # It is essential to connect the finished signal of the handler to the quit
        # method of the thread, otherwise it never returns!
        self._abcProcess.abcFinished.connect(self._runThread.quit)
        # Connect run handler signal to thread methods
        self._abcProcess.abcStarted.connect(self._onAbcStarted)
        self._abcProcess.abcAborted.connect(self._onAbcAborted)
        self._abcProcess.consoleLog.connect(self._onConsoleLog)
        # Connect thread signals to run handler methods
        self._runThread.started.connect(self._abcProcess.run)
        self._runThread.finished.connect(self._onAbcFinished)

    def startAbc(self, scriptName):
        """Interface function. Starts python with the _scriptName given."""

        self._abcProcess.addScriptName(scriptName)
        self._runThread.start()

    def stopAll(self):
        """
        Calls killProcess method of QObject, which, in turn, 
        emits finished signal for thread to quit.
        """
        self._abcProcess.killProcess()

    def _onAbcStarted(self):

        self._outputConsole.write('ABC computation running...')
        self._parent.signalAbcStarted()

    def _onAbcFinished(self):

        self._outputConsole.write('ABC computation finished.')
        self._parent.signalAbcFinished(self._abcProcess.error)

    def _onAbcAborted(self):

        self._outputConsole.writeWarning('ABC aborted by user.')
        self._parent.signalAbcAborted()

    def _onConsoleLog(self, text, error):
        """
        Triggered when subprocess reads from temporary output file
        which stores the output of the abc core algorithm.
        """

        if not error:
            self._outputConsole.write(text)
        else:
            self._outputConsole.writeError('ERROR during ABC execution.')
            self._outputConsole.writeError(text)


class APythonAbcProcess(QObject):
    abcFinished = pyqtSignal()
    abcAborted = pyqtSignal()
    abcStarted = pyqtSignal()
    consoleLog = pyqtSignal(str, bool)

    def __init__(self, flag):
        """
        Inherit from QObject to create an isolated instance of a python
        subprocess running in a separate thread.
        """
        super(APythonAbcProcess, self).__init__()

        self._flag = flag
        self._scriptName = None
        self.aborted = False
        self.error = False
        self.__p = None  # keep a reference of process

    def run(self):
        """Initializes a subprocess starting abc."""

        self.abcStarted.emit()
        self._runAbc()
        self.abcFinished.emit()

    def addScriptName(self, name):
        """Update script name for executing the right one."""

        self._scriptName = name

    def _runAbc(self):
        """Starts abc approximation."""

        # Open a temporary file
        f = tempfile.NamedTemporaryFile()

        # Spawn fast-dm subprocess with controlFileName just created
        self.__p = subprocess.Popen([sys.executable, self._scriptName], stdout=f, stderr=f)

        # Block execution of thread until abc finishes
        self.__p.wait()

        # Return read pointer to temp file to start
        f.seek(0)

        # Check return
        if self.__p.returncode != 0:
            self.error = True
            self.consoleLog.emit(f.read().decode('utf-8'), True)
        else:
            self.consoleLog.emit(f.read().decode('utf-8'), False)
        # Close temporary file - removes it
        f.close()

        # Clear reference to subprocess object
        self.__p = None

    def killProcess(self):
        """Kill process and emit finished."""

        if self.__p is not None:
            self.__p.kill()
            self.abcAborted.emit()
            self.aborted = True

