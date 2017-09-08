import platform
import os
import sys
import ctypes
import qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QLocale
from a_main_window import AMainWindow


__version__ = "1.0.1"


def __main__():
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
    app.setOrganizationName("Heidelberg University")
    app.setApplicationName("bprox")
    # =============================================================== #
    #                       CREATE SPLASH SCREEN                      #
    # =============================================================== #

    # splash = QSplashScreen()
    # splash.setPixmap(QPixmap('./icons/fast_ic.png'))
    # splash.setEnabled(False)
    # splash.show()
    # app.processEvents()
    # time.sleep(5)

    # =============================================================== #
    #                       CREATE MAIN WINDOW                        #
    # =============================================================== #
    mainWindow = AMainWindow()
    mainWindow.showMaximized()
    #splash.finish(mainWindow)
    sys.exit(app.exec_())


