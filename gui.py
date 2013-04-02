#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

In this example, we create a simple
window in PyQt4.

author: Jan Bodnar
website: zetcode.com 
last edited: October 2011
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

This example shows a tooltip on 
a window and a button

author: Jan Bodnar
website: zetcode.com 
last edited: October 2011
"""

import macro
import sys
from PyQt4 import QtGui, QtCore
from functools import partial

#class embterminal(QtGui.QWidget):
#
#    def __init__(self):
#        QtGui.QWidget.__init__(self)
#        self.process = QtCore.QProcess(self)
#        self.terminal = QtGui.QWidget(self)
#        layout = QtGui.QVBoxLayout(self)
#        layout.addWidget(self.terminal)
#        self.process.start(
#                'xterm',['-into', str(self.terminal.winId())])
#        # Works also with urxvt:
#        #self.process.start(
#                #'urxvt',['-embed', str(self.terminal.winId())])
#
#if __name__ == "__main__":
#    app = QtCore.QApplication(sys.argv)
#    main = embterminal()
#    main.show()
#    sys.exit(app.exec_())


   

class EmittingStream(QtCore.QObject):

   textWritten = QtCore.pyqtSignal(str)
   
   def write(self, text):
      self.textWritten.emit(str(text))

class Example(QtGui.QWidget):
    
   def __init__(self):
      super(Example, self).__init__()
#      self.process = QtCore.QProcess(self)
#      self.terminal = QtGui.QWidget(self)
#      sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
      self.initUI()
      
   def __del__(self):
      # Restore sys.stdout
      sys.stdout = sys.__stdout__
      
   def normalOutputWritten(self, text):
      """Append text to the QTextEdit."""
      # Maybe QTextEdit.append() works as well, but this is how I do it:
      cursor = self.textEdit.textCursor()
      cursor.movePosition(QtGui.QTextCursor.End)
      cursor.insertText(text)
      self.textEdit.setTextCursor(cursor)
      self.textEdit.ensureCursorVisible()
       
   def initUI(self):
       
      QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
      
      self.setToolTip('This is a <b>QWidget</b> widget')

      btn = []
      for i,user in enumerate(macro.accounts.keys()):
         btn.append(QtGui.QPushButton(user, self))
         btn[-1].setToolTip('This is a <b>QPushButton</b> widget')
         btn[-1].clicked.connect(partial(macro.start_marvel, user))
         btn[-1].resize(btn[-1].sizeHint())
         btn[-1].move(50, 50+25*i)
         
      btn = QtGui.QPushButton('Take screenshot', self)
      btn.clicked.connect(macro.take_screenshot_adb)
      btn.resize(btn.sizeHint())
      btn.move(200,50)
      
      btn = QtGui.QPushButton('GIMP', self)
      btn.clicked.connect(macro.gimpScreenshot)
      btn.resize(btn.sizeHint())
      btn.move(200,75)
      
      devices = macro.adbDevices()
#      listWidget = QtGui.QRadioButton()

      for i,device in enumerate(devices):
         btn = QtGui.QRadioButton(device, self)
#         btn.setToolTip('This is a <b>QPushButton</b> widget')
         btn.clicked.connect(partial(macro.setActiveDevice, device))
         btn.resize(btn.sizeHint())
         btn.move(50, 350+25*i)
      
#      listWidget.resize(200,200)
#      listWidget.move(300,75)
#      listWidget.show()
      
#      self.terminal.resize(self.terminal.sizeHint())
#      self.terminal.move(100, 100)
#      QtGui.QWidget(self.terminal)
#      self.process.start('xterm',['-into', str(self.terminal.winId())])
      
      self.setGeometry(300, 300, 450, 450)
      self.setWindowTitle('Tooltips')    
      self.show()
        
def main():
    
   app = QtGui.QApplication(sys.argv)
   ex = Example()
   sys.exit(app.exec_())


if __name__ == '__main__':
   main()