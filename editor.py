
import enchant
import re

from PySide.QtCore import QEvent, Signal, Qt
from PySide.QtGui import QPlainTextEdit, QSyntaxHighlighter, QAction, \
    QTextCharFormat, QMenu, QMouseEvent


class TextEdit(QPlainTextEdit):
    """
    A Text Editor based upon QTextEdit.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(TextEdit, self).__init__()

        self.setStyleSheet("font: 9pt \"Courier\";")

        # Default dictionary based on the current locale.
        self.dict = enchant.Dict("de_DE")
        self.highlighter = Highlighter(self.document())
        self.highlighter.setDict(self.dict)

    def setDict(self, val):
        """
        Reset the dictionary and relaunch spell checker.
        """
        self.dict = enchant.Dict(val)
        self.highlighter = Highlighter(self.document())
        self.highlighter.setDict(self.dict)

    def gotoLine(self, number):
        """
        Go to a given line in the document!
        """
        if number - 1 > 0:
            number -= 1
        cursor = self.textCursor()
        cursor.movePosition(cursor.Start)
        cursor.movePosition(cursor.NextBlock, n=number)
        self.setTextCursor(cursor)

    def getLine(self):
        """
        Retrieve the current line in the document.
        """
        cursor = self.textCursor()
        return cursor.columnNumber()

    def mousePressEvent(self, event):
        """
        React on a mouse event - move cursor to position of the event.
        """
        if event.button() == Qt.RightButton:
            event = QMouseEvent(QEvent.MouseButtonPress, event.pos(),
                Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        QPlainTextEdit.mousePressEvent(self, event)

    def contextMenuEvent(self, event):
        """
        Create a nice looking popup menu.
        """
        popup_menu = self.createStandardContextMenu()

        cursor = self.textCursor()
        cursor.select(cursor.WordUnderCursor)
        self.setTextCursor(cursor)

        if self.textCursor().hasSelection():
            text = unicode(self.textCursor().selectedText())
            if not self.dict.check(text):
                spell_menu = QMenu('Suggestions')
                for word in self.dict.suggest(text):
                    action = SpellAction(word, spell_menu)
                    action.correct.connect(self.correctWord)
                    spell_menu.addAction(action)
                if len(spell_menu.actions()):
                    popup_menu.insertSeparator(popup_menu.actions()[0])
                    popup_menu.insertMenu(popup_menu.actions()[0], spell_menu)

        popup_menu.exec_(event.globalPos())

    def correctWord(self, word):
        """
        Replaces the misspeclled word
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()

        cursor.removeSelectedText()
        cursor.insertText(word)

        cursor.endEditBlock()


class Highlighter(QSyntaxHighlighter):
    """
    Syntac highlighter which will underline misspell words.
    """

    WORDS = u'(?iu)[\w\']+'

    def __init__(self, *args):
        QSyntaxHighlighter.__init__(self, *args)
        self.dict = None

    def setDict(self, dict):
        self.dict = dict

    def highlightBlock(self, text):
        if not self.dict:
            return

        text = unicode(text)

        format = QTextCharFormat()
        format.setUnderlineColor(Qt.red)
        format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

        for word_object in re.finditer(self.WORDS, text):
            if not self.dict.check(word_object.group()):
                self.setFormat(word_object.start(),
                    word_object.end() - word_object.start(), format)


class SpellAction(QAction):
    """
    An Action which will change the selected word.
    """

    correct = Signal(unicode)

    def __init__(self, *args):
        QAction.__init__(self, *args)
        self.triggered.connect(lambda: self.correct.emit(unicode(self
         .text())))
