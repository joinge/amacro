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


class DeviceView(QtGui.QWidget):

   def __init__(self, parent, items):
   
      super(DeviceView,self).__init__(parent)
   
      self.model = QtGui.QStandardItemModel()
      self.model.setColumnCount(1)
      for i,device in enumerate(items):
#         status = QtGui.QStandardItem("")
         device = QtGui.QStandardItem(device)
#         box = QtGui.QStandardItem("")
#         box.setTextAlignment(QtCore.Qt.AlignRight)
#         box = QtGui.QCheckBox("Youwave?", self) #QtGui.QStandardItem("xxx")
         device.setCheckable(True)
         if i==0:
            device.setCheckState(QtCore.Qt.CheckState(2))
#         device.item
         self.model.appendRow([device])
#         model.appendColumn(box)

      self.model.setHorizontalHeaderLabels(["       Device ID"])
      self.model.itemChanged.connect(self.deviceClicked)

      self.tree = QtGui.QTreeView(self)
      self.tree.setModel(self.model)
      self.tree.setRootIsDecorated(False)

#      view.setColumnWidth(0,20)
      self.tree.setColumnWidth(0,170)
      self.tree.setColumnWidth(1,70)
      self.tree.resize(210,150)
#      tree.move(50,250)

      self.add_btn = QtGui.QPushButton('Add...', self)
      self.add_btn.clicked.connect(macro.checkTraining)
      self.add_btn.resize(self.add_btn.sizeHint())
      self.add_btn.move(0,160)
      
      self.del_btn = QtGui.QPushButton('Delete...', self)
      self.del_btn.clicked.connect(macro.checkTraining)
      self.del_btn.resize(self.del_btn.sizeHint())
      self.del_btn.move(210-self.del_btn.sizeHint().width(),160)
      
      a = self.model.item(0,0)
      
      print("hello")
      
   def deviceClicked(self):
      
      for i in range(self.model.rowCount()):
         if self.model.item(i,0).checkState() == 2:
            macro.setActiveDevice, self.model.item(i,0).text(), None)
      
      print("hello")
   
#      .connect(partial(macro.startMarvel, user, 1))
   

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
      
      self.setToolTip('Macro Control GUI')

      btn = []
      for i,user in enumerate(macro.accounts.keys()):
         btn.append(QtGui.QPushButton(user, self))
         btn[-1].setToolTip('This is a <b>QPushButton</b> widget')
         btn[-1].clicked.connect(partial(macro.startMarvel, user, 1))
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
      
      btn = QtGui.QPushButton('Clear cache', self)
      btn.clicked.connect(macro.clearMarvelCache)
      btn.resize(btn.sizeHint())
      btn.move(200,100)
      
      btn = QtGui.QPushButton('Check Training', self)
      btn.clicked.connect(macro.checkTraining)
      btn.resize(btn.sizeHint())
      btn.move(200,125)
      
#      devices = macro.adbDevices()
      devices = ["255.255.255.255:5555","127.0.0.1","127.0.0.1","127.0.0.1","127.0.0.1","127.0.0.1","127.0.0.1","127.0.0.1"]

#      listWidget = QtGui.QRadioButton()


#      x = bool(int(settings.value("pyuic4x", "0").toString()))
#  ds    self.pyuic4xCheckBox.setChecked(x)

      for i,device in enumerate(devices):
         btn = QtGui.QRadioButton(device, self)
#         btn.setToolTip('This is a <b>QPushButton</b> widget')
         btn.clicked.connect(partial(macro.setActiveDevice, device, None))
         btn.resize(btn.sizeHint())
         btn.move(400, 350+25*i)
         
      checkbox = QtGui.QCheckBox("Youwave?", self)
      checkbox.toggled.connect(partial(macro.setActiveDevice, None, checkbox ))
      checkbox.resize(checkbox.sizeHint())
      checkbox.move(250, 350)
      
#      tableWidget = QtGui.QTableWidget(self)
#      tableWidget.setRowCount(len(devices))
#      tableWidget.setColumnCount(2)
#      tableWidget.setHorizontalHeaderLabels(["Device ID", "Youwave?"])
#      tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
#      tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
#      tableWidget.move(50, 350)
#      
#      for i,device in enumerate(devices):
#         
#         item = QtGui.QTableWidgetItem(device)
#         item.setTextAlignment(QtCore.Qt.AlignCenter)
#         tableWidget.setItem(i, 0, item)
#              
#         no_text = QtGui.QTableWidgetItem("No")
#         no_text.setTextAlignment(QtCore.Qt.AlignCenter)
#         tableWidget.setItem(i, 1, no_text)
#         
#      tableWidget.setColumnWidth(0,120)
#      tableWidget.setColumnWidth(1,70)
#      tableWidget.resize(tableWidget.sizeHint())

#      tableWidget.resizeColumnsToContents()

#      listWidget = QtGui.QListWidget(self)
#      
#      for i in range(10):
#         item = QtGui.QListWidgetItem("Item %i" % i)
#         listWidget.addItem(item)
#       
#      listWidget.move(250, 450)
#      listWidget.show()
#      
#      
#      listWidget.resize(200,200)
#      listWidget.move(300,75)
#      listWidget.show()

      device_list = DeviceView(self,devices)
      device_list.move(50,300)



#      self.terminal.resize(self.terminal.sizeHint())
#      self.terminal.move(100, 100)
#      QtGui.QWidget(self.terminal)
#      self.process.start('xterm',['-into', str(self.terminal.winId())])
      
      self.setGeometry(300, 300, 600, 600)
      self.setWindowTitle('Tooltips')    
      self.show()
        
def main():
    
   app = QtGui.QApplication(sys.argv)
   ex = Example()
   sys.exit(app.exec_())


if __name__ == '__main__':
   main()