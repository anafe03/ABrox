from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from abrox.gui.a_utils import *
from abrox.gui.a_editor import APythonTextEditor
from abrox.gui.a_priors import APriorsWindow
from abrox.gui.a_data_viewer import ADataViewer
from abrox.gui.a_settings import ASettingsWindow
from abc import abstractmethod
from abrox.gui import tracksave


class AModelTree(QTreeWidget):
    """
    This class represents the model tree pane 
    for navigating through the models.
    """

    NUM_MODELS = 1
    FONT_SIZE = 9

    def __init__(self, mdiArea, model, console, outputConsole, parent=None):
        super(AModelTree, self).__init__(parent)

        self._mdiArea = mdiArea
        self._internalModel = model
        self._console = console
        self._outputConsole = outputConsole
        self._initTree()

    def _initTree(self):
        """Configure basic settings for tree behavior and components."""

        self._configureProperties()
        self._populate()

    def _configureProperties(self):
        """Customize te tree according to the program needs."""

        # Configure font
        font = self.font()
        font.setPointSize(AModelTree.FONT_SIZE)
        self.setFont(font)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.itemClicked.connect(self._onItemClicked)
        self.itemChanged.connect(self._onItemChanged)
        self.header().close()
        self.setUniformRowHeights(True)
        self.setColumnCount(1)

    def _populate(self):
        """Fills the model according to the _internalModel data."""

        # Clear tree, if anything
        if self.topLevelItem(0):
            self.topLevelItem(0).takeChildren()
            self.takeTopLevelItem(0)

        # Create the root analysis node
        root = AAnalysisNode()
        root.setIcon(0, QIcon('icons/icon.ico'))
        self.addTopLevelItem(root)

        for key in self._internalModel:
            if key == 'data':
                root.addChild(ADataNode('Data', self._internalModel, self._console, self._outputConsole))
            elif key == 'models':
                for model in self._internalModel[key]:
                    modelNode = AModelNode(model, self._internalModel)
                    root.addChild(modelNode)
            elif key == 'summary':
                root.addChild(ASummaryNode(self._internalModel, self._internalModel[key]))
            elif key == 'distance':
                root.addChild(ADistanceNode(self._internalModel, self._internalModel[key]))
            elif key == 'settings':
                root.addChild(ASettingsNode(self._internalModel, self._console, self._outputConsole))

        # Expand all nodes
        self.expandAll()

    def _onItemClicked(self, node):
        """Activated when user clicks on an item in the tree."""

        node.display(self._mdiArea)

    def _onItemChanged(self, node):
        """Activated when item is being edited (a.k.a) only model."""

        # Just to make sure
        if type(node) is AModelNode:
            # Check if no name collision exists
            node.changeTitleOfChildren()
        tracksave.saved = False

    def _popUpAnalysisMenu(self, pos):
        """Display the right-click invoked context menu when analysis node clicked."""

        addModel = createAction('Add Model...', callback= self._addModel, icon='newmodel')
        menu = QMenu()
        addActionsToMenu(menu, (addModel, ))
        menu.exec_(pos)

    def _popUpModelMenu(self, pos):
        """Display the right-click invoked context menu when model node clicked."""

        deleteModel = createAction('Delete Model', callback=self._deleteModel, icon='removemodel')
        menu = QMenu()
        addActionsToMenu(menu, (deleteModel, ))
        menu.exec_(pos)

    def _addModel(self):
        """Adds a model to the analysis."""

        # Add statistical model to internal model
        model = self._internalModel.addModel(name="Model{}".
                                             format(AModelTree.NUM_MODELS + 1))

        # Add model to tree
        root = self.topLevelItem(0)
        root.insertChild(AModelTree.NUM_MODELS + 1,
                         AModelNode(model, self._internalModel))
        AModelTree.NUM_MODELS += 1
        tracksave.saved = False

    def _deleteModel(self):
        """Deletes a model from the analysis."""

        # Get selected
        selected = self.selectedItems()[0]

        # Remove from internal model
        self._internalModel.deleteModel(selected.text(0))

        # Remove from mdi
        selected.destroyFromMdi()

        # Remove from tree
        selected.parent().removeChild(selected)
        del selected
        AModelTree.NUM_MODELS -= 1
        tracksave.saved = False

    def toDict(self):
        """Returns a dictionary of model information."""

        # Get root
        root = self.topLevelItem(0)

        # loop through root's children
        for i in range(root.childCount()):
            node = root.child(i)
            # Extract model simulate
            if type(node) is AModelNode:
                self._internalModel.addSimulateToModel(node.getCodeFromEditor(), node.text(0))
            elif type(node) is ASummaryNode:
                self._internalModel.addSummary(node.getCodeFromEditor())
            elif type(node) is ADistanceNode:
                self._internalModel.addDistance(node.getCodeFromEditor())

        # Return a dict ready to be dumped with json
        return self._internalModel.toDict()

    def updateProject(self):
        """
        Called when a project has been just loaded and 
        the internal model has been updated.
        """

        self._populate()
        self._mdiArea.closeAllSubWindows()

    def currentEditorFont(self):
        """Returns the font of the current editor."""

        # Iterate until finding a widget with an editor
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            if type(iterator.value()) is ASimulateNode or type(iterator.value()) is ASummaryNode:
                return iterator.value().editorFont()
            iterator += 1

    def changeEditorFont(self, font):
        """Called from main window when user changed another font."""

        # Iterate until finding a widget with an editor
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            node = iterator.value()
            # Id node has an editor, change font
            if type(node) is ASimulateNode or \
               type(node) is ASummaryNode or \
               type(node) is ADistanceNode:
                node.setEditorFont(font)
            iterator += 1

    def contextMenuEvent(self, event):
        """Re-implements the right-click, menu-pop-up event."""

        # Get selected items, if many, get first
        items = self.selectedItems()
        if items:
            item = items[0]
            if type(item) is AAnalysisNode:
                self._popUpAnalysisMenu(event.globalPos())
            elif type(item) is AModelNode:
                self._popUpModelMenu(event.globalPos())


class ABaseNode(QTreeWidgetItem):
    """Represents the base class for a node in the project tree."""

    def __init__(self, text):
        super(ABaseNode, self).__init__()

        self.setFlags(self.flags() ^ Qt.ItemIsDropEnabled)
        self.setFlags(self.flags() ^ Qt.ItemIsDragEnabled)
        self.setText(0, text)
        self.subWindow = None

    @abstractmethod
    def display(self, mdiArea):
        """Must be implemented."""
        pass


class AAnalysisNode(ABaseNode):

    def __init__(self, text='Analysis'):
        """
        Represents a top-level node (e.g. the analysis node) in the
        model tree view.
        """
        super(AAnalysisNode, self).__init__(text)

    def display(self, mdiArea): pass


class ADataNode(ABaseNode):

    def __init__(self, text='Data', internalModel=None, console=None, outputConsole=None):
        """Represents a data viewer node."""
        super(ADataNode, self).__init__(text)

        self._internalModel = internalModel
        self._dataViewer = ADataViewer(internalModel, console, outputConsole)
        self.setIcon(0, QIcon('./icons/data.png'))

    def display(self, mdiArea):
        """Displays the data editor table."""
        if self.subWindow in mdiArea.subWindowList():
            mdiArea.setActiveSubWindow(self.subWindow)
        else:
            self.subWindow = AMdiWindow()
            self.subWindow.setWindowIcon(self.icon(0))
            self.subWindow.setWindowTitle('Data Viewer')
            self.subWindow.setWidget(self._dataViewer)
            mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()


class AModelNode(ABaseNode):

    def __init__(self, model, internalModel):
        """Represents a model node in the analysis tree."""
        super(AModelNode, self).__init__(model.name)

        # Customize behavior
        self._internalModel = internalModel
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setIcon(0, QIcon('./icons/model.png'))

        # Store a flag to old name, updated when model changes name
        self.oldName = model.name
        self._addPriorsAndSimulate(model)

    def _addPriorsAndSimulate(self, model):
        """Adds priors and simulate according to model."""

        self.addChild(APriorsNode(self._internalModel, model))
        self.addChild(ASimulateNode(self._internalModel, model.simulate, model.name))

    def display(self, mdiArea):
        """Used to display the content of the node on the mdi area."""

        for i in range(self.childCount()):
            self.child(i).display(mdiArea)

    def changeTitleOfChildren(self):
        """Called when user renames a model."""

        # Change window titles
        for i in range(self.childCount()):
            self.child(i).changeModelName(self.text(0))
        # We change the old name here, since the children update the internal model
        self.oldName = self.text(0)

    def getCodeFromEditor(self):
        """A proxy to get code from current model simulate."""

        # Change window titles
        for i in range(self.childCount()):
            if type(self.child(i)) is ASimulateNode:
                return self.child(i).getCodeFromEditor()

    def destroyFromMdi(self):
        """Called when a model gets deleted. Destroys all MDI windows from model."""

        for i in range(self.childCount()):
            # If subwindow created, destroy
            if self.child(i).subWindow is not None:
                # A very nasty error occurs if we try to close the subWindow
                # if the wrapped C++ object is deleted, so handle it passively
                try:
                    self.child(i).subWindow.close()
                except RuntimeError:
                    pass


class APriorsNode(ABaseNode):

    def __init__(self, internalModel, model, itemName='Priors'):
        """Represents a priors node in the analysis tree."""

        super(APriorsNode, self).__init__(itemName)

        self._internalModel = internalModel
        self.priorsWindow = APriorsWindow(internalModel, model)
        self.setIcon(0, QIcon('./icons/priors.png'))

    def display(self, mdiArea):

        if self.subWindow in mdiArea.subWindowList():
            mdiArea.setActiveSubWindow(self.subWindow)
        else:
            self.subWindow = AMdiWindow()
            self.subWindow.setWindowIcon(self.icon(0))
            self.subWindow.setWindowTitle(self.parent().text(0) + ' Priors')
            self.subWindow.setWidget(self.priorsWindow)
            mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()

    def changeModelName(self, text):
        """Called from AModelNode on name change."""

        if self.subWindow is not None:
            print('Changing model name')
            print(text)
            self._internalModel.renameModel(self.parent().oldName, text)
            self.subWindow.setWindowTitle(text + ' Priors')
            self.priorsWindow.changeModelName(text)


class ASimulateNode(ABaseNode):
    """Represents a simulate node in the analysis tree."""

    def __init__(self, internalModel, code, modelName, text='Simulate'):
        super(ASimulateNode, self).__init__(text)

        self.modelName = modelName
        self._editor = APythonTextEditor(internalModel, code, text, modelName)
        self.setIcon(0, QIcon('./icons/function.png'))

    def display(self, mdiArea):
        """Displays the simulate function editor."""

        if self.subWindow in mdiArea.subWindowList():
            mdiArea.setActiveSubWindow(self.subWindow)
            self.subWindow.show()
        else:
            self.subWindow = AMdiWindow()
            self.subWindow.setWindowIcon(self.icon(0))
            self.subWindow.setWindowTitle(self.parent().text(0) + ' Simulate Function')
            self.subWindow.setWidget(self._editor)
            mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()

    def editorFont(self):
        return self._editor.font()

    def setEditorFont(self, font):
        self._editor.setFont(font)

    def changeModelName(self, text):
        """Called from AModelNode on name change."""

        self.modelName = text
        if self.subWindow is not None:
            self.subWindow.setWindowTitle(text + ' Simulate Function')
            self._editor.changeModelName(text)

    def getCodeFromEditor(self):
        """Returns the text from the editor."""

        return self._editor.toPlainText()


class ASummaryNode(ABaseNode):
    def __init__(self, internalModel, code, text='Summary'):
        """Represents a summary node in the analysis tree."""
        super(ASummaryNode, self).__init__(text)

        self._editor = APythonTextEditor(internalModel, code, text)
        self.setIcon(0, QIcon('./icons/function.png'))

    def display(self, mdiArea):

        if self.subWindow in mdiArea.subWindowList():
            mdiArea.setActiveSubWindow(self.subWindow)
            self.subWindow.show()
        else:
            self.subWindow = AMdiWindow()
            self.subWindow.setWindowIcon(self.icon(0))
            self.subWindow.setWindowTitle(self.text(0) + ' Function')
            self.subWindow.setWidget(self._editor)
            mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()

    def editorFont(self):
        return self._editor.font()

    def setEditorFont(self, font):
        self._editor.setFont(font)

    def getCodeFromEditor(self):
        """Returns the text from the editor."""

        return self._editor.toPlainText()


class ADistanceNode(ABaseNode):
    """Represents a distance node in the analysis tree."""

    def __init__(self, internalModel, code, text='Distance'):
        super(ADistanceNode, self).__init__(text)

        self._editor = APythonTextEditor(internalModel, code, text)
        self.setIcon(0, QIcon('./icons/function.png'))

    def display(self, mdiArea):

        if self.subWindow in mdiArea.subWindowList():
            mdiArea.setActiveSubWindow(self.subWindow)
            self.subWindow.show()
        else:
            self.subWindow = AMdiWindow()
            self.subWindow.setWindowIcon(self.icon(0))
            self.subWindow.setWindowTitle(self.text(0) + ' Function')
            self.subWindow.setWidget(self._editor)
            mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()

    def editorFont(self):
        return self._editor.font()

    def setEditorFont(self, font):
        self._editor.setFont(font)

    def getCodeFromEditor(self):
        """Returns the text from the editor."""

        return self._editor.toPlainText()


class ASettingsNode(ABaseNode):
    def __init__(self, internalModel, console, outputConsole, text='Settings'):
        """Represents an output node in the analysis tree."""
        super(ASettingsNode, self).__init__(text)

        self._settingsWindow = ASettingsWindow(internalModel, console, outputConsole)
        self.setIcon(0, QIcon('./icons/settings.png'))

    def display(self, mdiArea):

        if self.subWindow in mdiArea.subWindowList():
            mdiArea.setActiveSubWindow(self.subWindow)
            self.subWindow.show()
        else:
            self.subWindow = AMdiWindow()
            self.subWindow.setWindowIcon(self.icon(0))
            self.subWindow.setWindowTitle(self.text(0))
            self.subWindow.setWidget(self._settingsWindow)
            mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()


class AMdiWindow(QMdiSubWindow):

    def __init__(self, parent=None):
        super(AMdiWindow, self).__init__(parent)

        self.setOption(QMdiSubWindow.RubberBandMove)
        self.setOption(QMdiSubWindow.RubberBandResize)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowIcon(QIcon('icons/icon.ico'))
        self.setWindowFlags(Qt.SubWindow)
        self.sizeGrip = QSizeGrip(self)

    def closeEvent(self, event):
        """Re-implement the close event to simply hide widget."""

        self.setWidget(QWidget())
        event.accept()
