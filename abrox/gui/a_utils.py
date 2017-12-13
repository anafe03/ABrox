from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QPushButton, QToolButton, QDialogButtonBox
from PyQt5.QtCore import Qt


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


def createButton(label, iconPath=None, toolText=None, func=None,
                  focusPolicy=None, enabled=True, tool=False):
    """Utility function creating a button. to save typing"""

    button = QPushButton(label)
    if tool:
        button = QToolButton()
        button.setText(label)
    if iconPath is not None:
        button.setIcon(QIcon(iconPath))
    if func is not None:
        button.clicked.connect(func)
    if focusPolicy is not None:
        button.setFocusPolicy(focusPolicy)
    if toolText is not None:
        button.setToolTip(toolText)
        button.setStatusTip(toolText)
    button.setEnabled(enabled)
    return button


def createDialogYesNoButtons(yesFunc, noFunc, resetFunc=None):
    """Creates the no and cancel buttons of a dialog."""

    # Create OK and Cancel buttons
    if resetFunc is not None:
        buttons = QDialogButtonBox(QDialogButtonBox.Ok |
                                   QDialogButtonBox.Cancel |
                                   QDialogButtonBox.Reset,
                                   Qt.Horizontal)
    else:
        buttons = QDialogButtonBox(QDialogButtonBox.Ok |
                                   QDialogButtonBox.Cancel,
                                   Qt.Horizontal)
    buttons.accepted.connect(yesFunc)
    buttons.rejected.connect(noFunc)
    if resetFunc is not None:
        buttons.button(QDialogButtonBox.Reset).clicked.connect(resetFunc)
    return buttons
