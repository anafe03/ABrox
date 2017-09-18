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
    def __init__(self, parent, internalModel, console):

        # Create instances
        self._parent = parent
        self._internalModel = internalModel
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

        self._parent.signalAbcStarted()
        print('From manager: Starting abc')

    def _onAbcFinished(self):

        self._parent.signalAbcFinished()
        print('From manager: Finished abc')


class APythonAbcProcess(QObject):
    abcFinished = pyqtSignal()
    abcStarted = pyqtSignal()
    consoleLog = pyqtSignal(str)

    def __init__(self, flag):
        """
        Inherit from QObject to create an isolated instance of a python
        subprocess running in a separate thread.
        """
        super(APythonAbcProcess, self).__init__()

        self._flag = flag
        self.__p = None  # keep a reference of process
        self.aborted = False
        self.error = False

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

        # Read output
        # Return read pointer to temp file to start
        f.seek(0)
        # Read log
        print(f.read().decode('utf-8'))
        # Close temporary file - removes it
        f.close()

        # Clear reference to subprocess object
        self.__p = None

    def killProcess(self):
        """Kill process and emit finished."""

        if self.__p is not None:
            self.__p.kill()
            self.abcFinished.emit()
            self.aborted = True

