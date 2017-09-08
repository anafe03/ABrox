from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction


def addActionsToMenu(menu, actions):
    """A helper function to add many actions to a target menu or a toolbar."""

    for action in actions:
        if action is None:
            menu.addSeparator()
        else:
            menu.addAction(action)


def createAction(text, callback=None, parent=None, shortcut=None,
                  icon=None, tip=None, checkable=False):
    """Utility function to create an action with a single command."""

    action = QAction(text, parent)
    if icon is not None:
        action.setIcon(QIcon("./icons/{}.png".format(icon)))
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if callback is not None:
        action.triggered.connect(callback)
    if checkable:
        action.setCheckable(True)
    return action
