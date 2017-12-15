from PyQt5.QtCore import QRegExp, Qt, QEvent, QRect, QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget, QPlainTextEdit, QTextEdit
from abrox.gui import tracksave


class ALineNumberArea(QWidget):
    """Represents line numbers component for a python editor."""

    BACKGROUND = QColor(49, 51, 51)
    FOREGROUND = QColor(120, 120, 120)

    def __init__(self, editor):
        super(ALineNumberArea, self).__init__(editor)

        self.editor = editor

    def sizeHint(self):
        """Re-implements the size hint event."""
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        """Re-implements the paint event."""

        self.editor.lineNumberAreaPaintEvent(event)


class APythonTextEditor(QPlainTextEdit):
    """
    This class represents a basic text editor with a re-implemented
    keyPressEvent method to handle TAB press as four whitespaces.
    """

    HIGHLIGHT = QColor(46, 50, 53)

    def __init__(self, internalModel, codeToInsert, functionName,
                       modelName=None, fontFamily="Monospaced",
                       fontSize=12, parent=None):
        super(APythonTextEditor, self).__init__(parent)

        # Store reference to model and name
        self._internalModel = internalModel
        self.modelName = modelName
        self.lineNumberArea = ALineNumberArea(self)

        # Create font and set it as default
        font = QFont(fontFamily, fontSize)
        font.setFixedPitch(True)
        self.setFont(font)

        # Connect callbacks for line-numbers update
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.updateLineNumberAreaWidth(0)
        self._highlighter = APythonHighlighter(self.document())

        # Connect text changed signal to the right callback
        if functionName == 'Simulate':
            self.textChanged.connect(self._updateSimulate)
        elif functionName == 'Summary':
            self.textChanged.connect(self._updateSummary)
        elif functionName == 'Distance':
            self.textChanged.connect(self._updateDistance)

        # Insert provided code
        self._insertCode(codeToInsert, functionName)

    def _updateSimulate(self):
        """Triggered when simulate editor gets changed."""

        self._internalModel.addSimulateToModel(self.toPlainText(), self.modelName)

    def _updateSummary(self):
        """Triggered when summary editor gets changed."""

        self._internalModel.addSummary(self.toPlainText())

    def _updateDistance(self):
        """Triggered when distance editor gets changed."""

        self._internalModel.addDistance(self.toPlainText())

    def changeModelName(self, text):
        """Called when model name changes."""

        self.modelName = text

    def _insertCode(self, code, name):
        """Insert saved code or default entry."""

        if code:
            self.insertPlainText(code)
        else:
            if name.lower() == 'simulate':
                param = 'params'
            elif name.lower() == 'summary':
                param = 'data'
            elif name.lower() == 'distance':
                param = 'simSummary, obsSummary'
            else:
                # Just to make sure that param is defined
                param = ''

            self.insertPlainText('def {}({}):\n'
                                 '    # write your code here\n'
                                 '    pass'.format(name.lower(), param))

    def lineNumberAreaPaintEvent(self, event):
        """Called when line-numbers widget calls its paint event"""

        # Create a painter
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), ALineNumberArea.BACKGROUND)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # The actual drawing of the line numbers goes here
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                pen = QPen(ALineNumberArea.FOREGROUND)
                painter.setPen(pen)
                painter.setFont(self.font())
                painter.drawText(5, top, self.lineNumberArea.width(), height,
                                 Qt.AlignLeft, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def lineNumberAreaWidth(self):
        """calculates and returns the width of the line-number area."""

        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('12') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        """Expands the line number area."""

        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        """Updates viewport of line number area."""

        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(),
                                       rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def highlightCurrentLine(self):
        """Draws a borderless rectangle around the current line."""

        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(APythonTextEditor.HIGHLIGHT)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    def event(self, event):
        """Re-implement key-press event to insert 4 whitespaces instead of a tab."""

        if event.type() == QEvent.KeyPress:
            # If key pressed, we need a resave
            tracksave.saved = False
            if event.key() == Qt.Key_Tab:
                cursor = self.textCursor()
                cursor.insertText("    ")
                return True
        if event.type() == QEvent.Wheel:
            if event.modifiers() == Qt.ControlModifier:
                if event.angleDelta().y() > 0:
                    self.zoomIn(2)
                else:
                    self.zoomOut(2)
        return QPlainTextEdit.event(self, event)

    def resizeEvent(self, event):
        """Re-implements the resize signal."""
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                                              self.lineNumberAreaWidth(), cr.height()))


class APythonHighlighter(QSyntaxHighlighter):

    Rules = []
    Formats = {}
    Colors = {'normal': '#eff0f1',
              'functionname': '#eff0f1',
              'keyword': '#dd580b',
              'builtin': '#598ec6',
              'string': '#a5c261',
              'comment': '#787878',
              'decorator': '#bbb529',
              'number': '#6987bb',
              'constant': '#6390bf',
              'pyqt': '#008b8b',
              'error': '#a31010'}

    def __init__(self, parent=None):
        super(APythonHighlighter, self).__init__(parent)

        self.initializeFormats()

        KEYWORDS = ["and", "as", "assert", "break", "class",
                "continue", "def", "del", "elif", "else", "except",
                "exec", "finally", "for", "from", "global", "if",
                "import", "in", "is", "lambda", "not", "or", "pass",
                "raise", "return", "try", "while", "with",
                "yield", "True", "False", "None"]

        BUILTINS = ["abs", "all", "any", "basestring", "bool",
                "callable", "chr", "classmethod", "cmp", "compile",
                "complex", "delattr", "dict", "dir", "divmod",
                "enumerate", "eval", "execfile", "exit", "file",
                "filter", "float", "frozenset", "getattr", "globals",
                "hasattr", "hex", "id", "int", "isinstance",
                "issubclass", "iter", "len", "list", "locals", "map",
                "max", "min", "object", "oct", "open", "ord", "pow",
                "property", "range", "reduce", "repr", "reversed",
                "round", "set", "setattr", "slice", "sorted", "self",
                "staticmethod", "str", "sum", "super", "tuple", "type",
                "vars", "zip", "print"]
        CONSTANTS = ["NotImplemented", "Ellipsis", "Exception"]

        # Note, that the order determines rule precedence

        # Regexp for bold function names (comes first, so def is orange)
        APythonHighlighter.Rules.append((QRegExp("^def\s+.*(?=\()"), "functionname"))
        # Regexp for keyword
        APythonHighlighter.Rules.append((QRegExp(
                "|".join([r"\b%s\b" % keyword for keyword in KEYWORDS])),
                "keyword"))
        # Regexp for builtin
        APythonHighlighter.Rules.append((QRegExp(
                "|".join([r"\b%s\b" % builtin for builtin in BUILTINS])),
                "builtin"))
        # Regexp for constant
        APythonHighlighter.Rules.append((QRegExp(
                "|".join([r"\b%s\b" % constant for constant in CONSTANTS])), "constant"))
        # Regexp number
        APythonHighlighter.Rules.append((QRegExp(
                r"\b[+-]?[0-9]+[lL]?\b"
                r"|\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b"
                r"|\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b"),
                "number"))
        # Regexp for PyQt5
        APythonHighlighter.Rules.append((QRegExp(
                r"\bPyQt5\b|\bQt?[A-Z][a-z]\w+\b"), "pyqt"))
        # Regexp for decorator
        APythonHighlighter.Rules.append((QRegExp(r"@\w+\b"),
                "decorator"))
        # Regexp for strings
        stringRe = QRegExp(r"""(?:'[^']*'|"[^"]*")""")
        stringRe.setMinimal(True)
        APythonHighlighter.Rules.append((stringRe, "string"))
        self.stringRe = QRegExp(r"""(:?"["]".*"["]"|'''.*''')""")
        self.stringRe.setMinimal(True)
        APythonHighlighter.Rules.append((self.stringRe, "string"))
        self.tripleSingleRe = QRegExp(r"""'''(?!")""")
        self.tripleDoubleRe = QRegExp(r'''"""(?!')''')
        # Regexp for comment
        APythonHighlighter.Rules.append((QRegExp(r"#.*"), "comment"))

    @staticmethod
    def initializeFormats():
        """Prepare color coding scheme for different word types."""

        baseFormat = QTextCharFormat()
        for name, color in APythonHighlighter.Colors.items():
            format = QTextCharFormat(baseFormat)
            format.setForeground(QColor(color))
            if name in ("keyword", "decorator"):
                format.setFontWeight(QFont.Bold)
            if name == "comment":
                format.setFontItalic(True)
            if name == "functionname":
                format.setFontWeight(QFont.Bold)
            APythonHighlighter.Formats[name] = format

    def highlightBlock(self, text):
        NORMAL, TRIPLESINGLE, TRIPLEDOUBLE, ERROR = range(4)

        textLength = len(text)
        prevState = self.previousBlockState()

        self.setFormat(0, textLength,
                       APythonHighlighter.Formats["normal"])

        if text.startswith("Traceback") or text.startswith("Error: "):
            self.setCurrentBlockState(ERROR)
            self.setFormat(0, textLength,
                           APythonHighlighter.Formats["error"])
            return
        if prevState == ERROR and not text.startswith("#"):
            self.setCurrentBlockState(ERROR)
            self.setFormat(0, textLength,
                           APythonHighlighter.Formats["error"])
            return

        for regex, format in APythonHighlighter.Rules:
            i = regex.indexIn(text)
            while i >= 0:
                length = regex.matchedLength()
                self.setFormat(i, length,
                               APythonHighlighter.Formats[format])
                i = regex.indexIn(text, i + length)

        # Slow but good quality highlighting for comments. For more
        # speed, comment this out and add the following to __init__:
        # PythonHighlighter.Rules.append((QRegExp(r"#.*"), "comment"))
        # if not text:
        #     pass
        # elif text[0] == "#":
        #     self.setFormat(0, len(text),
        #                    PythonHighlighter.Formats["comment"])
        # else:
        #     stack = []
        #     for i, c in enumerate(text):
        #         if c in ('"', "'"):
        #             if stack and stack[-1] == c:
        #                 stack.pop()
        #             else:
        #                 stack.append(c)
        #         elif c == "#" and len(stack) == 0:
        #             self.setFormat(i, len(text),
        #                            PythonHighlighter.Formats["comment"])
        #             break

        self.setCurrentBlockState(NORMAL)

        if self.stringRe.indexIn(text) != -1:
            return
        # This is fooled by triple quotes inside single quoted strings
        for i, state in ((self.tripleSingleRe.indexIn(text),
                          TRIPLESINGLE),
                         (self.tripleDoubleRe.indexIn(text),
                          TRIPLEDOUBLE)):
            if self.previousBlockState() == state:
                if i == -1:
                    i = len(text)
                    self.setCurrentBlockState(state)
                self.setFormat(0, i + 3,
                               APythonHighlighter.Formats["string"])
            elif i > -1:
                self.setCurrentBlockState(state)
                self.setFormat(i, len(text),
                               APythonHighlighter.Formats["string"])

    def rehighlight(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QSyntaxHighlighter.rehighlight(self)
        QApplication.restoreOverrideCursor()