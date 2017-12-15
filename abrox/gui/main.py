from PyQt5.QtWidgets import *
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QPixmap, QFontDatabase
from abrox.gui.a_main_window import AMainWindow
import os
import sys
import ctypes
import qdarkstyle


__version__ = "1.0.1"

# Change script path
PATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(PATH)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    # =============================================================== #
    #               SET APP ID SO ICON IS VISIBLE                     #
    # =============================================================== #
    if sys.platform == "win32":
        myappid = "heidelberg.university.bprox.0.0.1"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # =============================================================== #
    #                   CHANGE LOCALE SETTINGS                        #
    # =============================================================== #
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

    # =============================================================== #
    #                   SET APP GLOBAL INFORMATION                    #
    # =============================================================== #
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    font = QFontDatabase.systemFont(QFontDatabase.GeneralFont)
    font.setPointSize(font.pointSize() + 1)
    app.setFont(font)
    app.setOrganizationName("Heidelberg University")
    app.setApplicationName("abrox")

    # =============================================================== #
    #                       CREATE SPLASH SCREEN                      #
    # =============================================================== #
    splash = QSplashScreen()
    splash.setPixmap(QPixmap('./icons/logo.png'))
    splash.setEnabled(False)
    splash.show()
    app.processEvents()
    #time.sleep(3)

    # =============================================================== #
    #                       CREATE MAIN WINDOW                        #
    # =============================================================== #
    mainWindow = AMainWindow()
    mainWindow.showMaximized()
    splash.finish(mainWindow)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
