#-*- coding: utf-8 -*-

import ConfigParser
import editor
import sys
import os

from subprocess import Popen, PIPE, STDOUT

from PySide import QtGui
from PySide.QtCore import QPoint, Qt, QUrl
from PySide.QtWebKit import QWebView
from PySide.QtGui import QMessageBox, QMainWindow, QLabel


class Yame(QMainWindow):
    """
    Yet Another Markdown Editor.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Yame, self).__init__()
        # configure

        config = ConfigParser.ConfigParser()
        config.readfp(open('defaults.cfg'))
        self.parser = config.get('Markdown', 'parser')
        
        # init
        self.filename = ''
        self.saved = True
        self.sync = True
        self.lastSearch = ''
        self.initUI()

    # File actions

    def newFile(self):
        """
        Create a blank new file.
        """
        if self.saved is False and self.editor.toPlainText() != '':
            msgBox = QMessageBox()
            msgBox.setText("The document has been modified.")
            msgBox.setInformativeText("really discard current document?")
            msgBox.setStandardButtons(QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret == QMessageBox.Cancel:
                return
        self.editor.clear()
        self.filename = ''

    def openFile(self, filename = None):
        """
        Open a file.
        """
        if self.saved is False and self.editor.toPlainText() != '':
            msgBox = QMessageBox()
            msgBox.setText("The document has been modified.")
            msgBox.setInformativeText("Really discard current document?")
            msgBox.setStandardButtons(QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret == QMessageBox.Cancel:
                return

        self.editor.clear()
        if not filename:
            fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '',
                ("Markdown Files (*.txt *.md)"))
            self.filename = fname
        else:
            self.filename = filename

        f = open(fname, 'r')

        # change working directory
        os.chdir(os.path.dirname(f.name))

        with f:
            tmp = f.read()
            tmp = tmp.decode('utf-8')
            self.editor.insertPlainText(tmp)
        f.close()

        self.saved = True
        self.saveStatus.setText('Document saved: ' + str(self.saved))

    def saveFileAs(self):
        """
        Save to a new file.
        """
        self.filename = ''
        self.saveFile()

    def saveFile(self):
        """
        Save to a file.
        """
        if self.filename == '':
            fname, _ = QtGui.QFileDialog.getSaveFileName(self, 'Save file',
                '', ("Markdown Files (*.txt *.md)"))
            self.filename = fname

        fel = open(self.filename, 'w')
        for line in self.editor.toPlainText().split('\n'):
            fel.write(line.encode('utf-8') + '\n')
        fel.close()
        self.saved = True
        self.saveStatus.setText('Document saved: ' + str(self.saved))

    # GUI operations

    def togglePanelSync(self):
        """
        Toggle a flag which will ensure sync between editor and web.
        """
        if self.sync is True:
            self.sync = False
            self.web.hide()
        else:
            self.sync = True
            self.web.show()

    def updateStructure(self):
        """
        Parse the header structure.
        """
        self.tree.clear()
        line_nr = 1
        for line in self.editor.toPlainText().split('\n'):
            if not line.find('#'):
                nr, title = line.split(' ')[0], ' '.join(line.split(' ')[1:])
                nr = len(nr)
                item = QtGui.QTreeWidgetItem()
                item.setText(0, title)
                item.setText(1, str(line_nr))
                item.setText(2, str(nr))
                if nr == 1:
                    self.tree.addTopLevelItem(item)
                    first = item
                elif nr == 2:
                    first.addChild(item)
                    second = item
                elif nr == 3:
                    second.addChild(item)
                self.tree.expandItem(item)

            line_nr += 1
        self.saved = False
        self.saveStatus.setText('Document saved: ' + str(self.saved))

    def gotoLine(self):
        """
        Jump to a certain line.
        """
        item = self.tree.selectedItems()[0]
        nr = int(item.text(1))
        self.editor.gotoLine(nr)

    def changeLanguage(self, text):
        """
        Change the language.
        """
        self.editor.setDict(text)

    def closeEvent(self, event):
        """
        Ask if the window can be closed before really closing.
        """
        msg = "Are you sure to quit?"
        if not self.saved:
            msg += '\nWARNING - document is unsaved'
        reply = QtGui.QMessageBox.question(self, 'Message',
            msg , QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def findWord(self):
        """
        Lookup a word.
        """
        text, ok = QtGui.QInputDialog.getText(self, 'Find Word', 
            'Look for:', text=self.lastSearch)
        
        if ok:
            self.lastSearch = text    
            self.editor.find(text)

    # Markdown stuff

    def exportHtml(self):
        """
        Export to an HTML file.
        """
        txt = self.editor.toPlainText().encode('utf-8')
        p = Popen([self.parser], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        grep_stdout = p.communicate(input=txt)[0]
        fname, _ = QtGui.QFileDialog.getSaveFileName(self, 'Save HTML', '',
            ("HTML Files (*.html)"))

        fel = open(fname, 'w')
        fel.write(grep_stdout)
        fel.close()

    def parseMarkdown(self):
        """
        Parse the Markdown stuff.
        """
        self.updateStructure()
        if self.sync is False:
            return

        y = self.web.page().mainFrame().scrollPosition().y()
        txt = self.editor.toPlainText().encode('utf-8')

        if txt is '' or None:
            return

        p = Popen([self.parser], stdout=PIPE, stdin=PIPE, stderr=STDOUT,
            shell=False)
        grep_stdout = p.communicate(input=txt)[0].decode('utf-8')
        path = QUrl.fromUserInput(os.getcwd() + os.sep)
        grep_stdout = grep_stdout.replace('img src=\"', 'img src=\"' +
                                                        path.toString())
        # Can't use baseUrl=path because external img will not be loaded
        # than :-/
        self.web.setHtml(grep_stdout)
        if y:
            self.web.scroll(0, y)
            self.web.page().mainFrame().scroll(0, y)
            self.web.page().mainFrame().setScrollPosition(QPoint(0, y))

    def initUI(self):
        """
        Initialize a UI.
        """
        # Panels
        self.tree = QtGui.QTreeWidget()
        self.tree.itemDoubleClicked.connect(self.gotoLine)
        head = QtGui.QTreeWidgetItem()
        head.setText(0, 'Structure')
        self.tree.setHeaderItem(head)

        self.editor = editor.TextEdit()
        self.editor.textChanged.connect(self.parseMarkdown)
        self.editor.setFrameShape(QtGui.QFrame.StyledPanel)

        self.web = QWebView()
        self.web.setZoomFactor(0.9)
        self.web.setHtml('')
        self.web.show()

        splitter1 = QtGui.QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.editor)
        splitter1.addWidget(self.web)
        splitter1.setStretchFactor(0, 3)
        splitter1.setStretchFactor(1, 1)

        splitter2 = QtGui.QSplitter(Qt.Horizontal)
        splitter2.addWidget(self.tree)
        splitter2.addWidget(splitter1)
        splitter2.setStretchFactor(0, 1)
        splitter2.setStretchFactor(1, 2)

        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(splitter2)
        self.setLayout(hbox)

        # Menu
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')

        newAction = fileMenu.addAction('&New')
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New document')
        newAction.triggered.connect(self.newFile)

        openAction = fileMenu.addAction('&Open...')
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open document')
        openAction.triggered.connect(self.openFile)

        saveAction = fileMenu.addAction('&Save...')
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save document')
        saveAction.triggered.connect(self.saveFile)

        saveAsAction = fileMenu.addAction('&Save As...')
        saveAsAction.setStatusTip('Save document as')
        saveAsAction.triggered.connect(self.saveFileAs)

        fileMenu.addSeparator()

        exitAction = fileMenu.addAction('&Exit')
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)        

        editMenu = menubar.addMenu('&Edit')
        toggleAction = editMenu.addAction('&Toggle Sync...')
        toggleAction.setShortcut('Ctrl+T')
        toggleAction.setStatusTip('Toggle sync between preview and editor.')
        toggleAction.triggered.connect(self.togglePanelSync)

        exportAction = editMenu.addAction('&Export HTML...')
        exportAction.setShortcut('Ctrl+E')
        exportAction.setStatusTip('Export HTML')
        exportAction.triggered.connect(self.exportHtml)

        searchAction = editMenu.addAction('&Find...')
        searchAction.setShortcut('Ctrl+F')
        searchAction.setStatusTip('Search for a word.')
        searchAction.triggered.connect(self.findWord)

        # Toolbar
        combo = QtGui.QComboBox(self)
        combo.addItem("de_DE")
        combo.addItem("en_US")
        combo.activated[str].connect(self.changeLanguage)

        self.toolbar = self.addToolBar('')
        self.toolbar.addAction(newAction)
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(saveAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(toggleAction)
        self.toolbar.addAction(exportAction)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(combo)

        self.statusBar()
        self.saveStatus = QLabel()
        self.saveStatus.setText('Document saved: ' + str(self.saved))
        self.statusBar().addWidget(self.saveStatus)
        self.setCentralWidget(splitter2)

        # The rest
        self.setGeometry(100, 100, 900, 600)
        self.showMaximized()
        self.setWindowTitle('YAME! - Yet Another Markdown Editor!')
        self.show()


def main():
    """
    Main routine.
    """
    app = QtGui.QApplication(sys.argv)
    editor = Yame()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
