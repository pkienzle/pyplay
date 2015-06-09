#!/usr/bin/env python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

EXAMPLE_HTML = """\
<html>
<body>
  <center>
<script language="JavaScript">
    document.write("<p>Python ' + py.version + '</p>')
</script>
  <button onClick="py.showMessage('Hello from WebKit')">Press me</button>
  </center>
</body>
</html>
"""

class HtmlContextExample(QObject):
    @pyqtSlot(str)
    def showMessage(self, msg):
        QMessageBox.information(None, "Info", msg)

    @pyqtProperty(str)
    def version(self):
        return sys.version

class HtmlWindow(QMainWindow):
    def __init__(self, url=None, html=None, context=None, parent=None):
        super(self.__class__, self).__init__(parent)
        #self.layout().setContentMargin(0,0,0,0)

        status = self.statusBar()
        status.setSizeGripEnabled(True)
        self.statusLabel = QLabel("")
        status.addWidget(self.statusLabel, 1)

        self.context = context
        self.web = QWebView()
        self.web.page().mainFrame().javaScriptWindowObjectCleared.connect(self._setContext)
        self.web.loadStarted.connect(self.loadStarted)
        self.web.loadFinished.connect(self.loadFinished)
        self.web.loadProgress.connect(self.loading)
        self.web.statusBarMessage.connect(self.setStatus)
        self.web.titleChanged.connect(self.titleChanged)

        if url:
            self.web.load(QUrl(url))
        elif html:
            self.web.setHtml(html)

        button = QPushButton("Back")
        button.clicked.connect(self.web.back)

        win = QWidget(self)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.web)
        layout.addWidget(button)
        win.setLayout(layout)
        self.setCentralWidget(win)

    def _setContext(self):
        if self.context:
            self.web.page().mainFrame().addToJavaScriptWindowObject("py", self.context)

    def loadStarted(self):
        self.setStatus("Load started")

    def loading(self, percent):
        self.setStatus("Loading %d%%" % percent)

    def loadFinished(self, flag):

        # For testing purposes, assume context has be set with HtmlContextExample
        self.web.page().mainFrame().evaluateJavaScript(r"""
(function (el, str) {
    var div = document.createElement('div');
    div.innerHTML = str;
    while (div.children.length > 0) { el.appendChild(div.children[0]); }
})(document.body, '<hr /><button onClick="py.showMessage(py.version)">Press me</button>');

""")
        self.setStatus("Done")

    def setStatus(self, message):
        self.statusLabel.setText(message)

    def titleChanged(self, title):
        self.setWindowTitle(title)

def main():
    url = sys.argv[1] if len(sys.argv)>1 else "http://google.com"

    app = QApplication([])
    context = HtmlContextExample()
    win = HtmlWindow(url=url, context=context)
    #win = HtmlWindow(html=EXAMPLE_HTML, context=context)
    win.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
