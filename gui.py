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

class MyStream(QtCore.QObject):
   message = QtCore.pyqtSignal(str)
   def __init__(self, parent=None):
      super(MyStream, self).__init__(parent)
   
   def write(self, message):
      self.message.emit(str(message))
      
   def flush(self):
      pass
#      sys.stdout.flush()


class MyConsole(QtGui.QWidget):

   def __init__(self, parent):
      
      super(MyConsole,self).__init__(parent)
      
      self.textEdit = QtGui.QTextEdit(self)  
      
      self.textEdit.resize(500,300)   
      
   @QtCore.pyqtSlot(str)
   def on_myStream_message(self, message):
      self.textEdit.moveCursor(QtGui.QTextCursor.End)
      self.textEdit.insertPlainText(message)
      self.textEdit.show()


class DeviceView(QtGui.QWidget):

   def __init__(self, parent, items):
         
      super(DeviceView,self).__init__(parent)
   
      self.model = QtGui.QStandardItemModel()
      self.model.setColumnCount(2)
      self.deviceActiveList = {}
      self.deviceYouwaveList = {}
      for i,device in enumerate(items):
#         status = QtGui.QStandardItem("")
         device_item = QtGui.QStandardItem(device)
         self.deviceActiveList[str(i)] = False
         self.deviceYouwaveList[str(i)] = False
         box = QtGui.QStandardItem("")
#         box.setTextAlignment(QtCore.Qt.AlignRight)
#         box = QtGui.QCheckBox("Youwave?", self) #QtGui.QStandardItem("xxx")
         device_item.setCheckable(True)
         box.setCheckable(True)
         if i==0:
            device_item.setCheckState(QtCore.Qt.CheckState(2))
            self.deviceActiveList[str(i)] = True
            macro.setActiveDevice(device, None)
#         device.item
         self.model.appendRow([device_item,box])
#         model.appendColumn(box)

      self.model.setHorizontalHeaderLabels(["       Device ID","YW"])
      self.model.itemChanged.connect(self.deviceClicked)

      self.tree = QtGui.QTreeView(self)
      self.tree.setModel(self.model)
      self.tree.setRootIsDecorated(False)

#      view.setColumnWidth(0,20)
      self.tree.setColumnWidth(0,170)
      self.tree.setColumnWidth(1,30)
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
      
      device_selected = False
      for i in range(self.model.rowCount()):
         if self.model.item(i,1).checkState() == 2:
            self.deviceYouwaveList[str(i)] = True
         else:
            self.deviceYouwaveList[str(i)] = False
                  
         if self.model.item(i,0).checkState() == 2:
            device_selected = True
            device_text = str(self.model.item(i,0).text())
            if self.deviceActiveList[str(i)] == False:
               macro.setActiveDevice(device_text, self.deviceYouwaveList[str(i)])
               self.deviceActiveList[str(i)] = True
               
               for j in range(self.model.rowCount()):
                  device_text = str(self.model.item(j,0).text())
                  if not i==j:
                     self.model.item(j,0).setCheckState(QtCore.Qt.CheckState(0))
                     self.deviceActiveList[str(j)] = False

      if not device_selected:
         for i in range(self.model.rowCount()):
            state = 0
            if self.deviceActiveList[str(i)]:
               state = 2

            self.model.item(i,0).setCheckState(QtCore.Qt.CheckState(state))
                  
      print(macro.ACTIVE_DEVICE)
   
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
         btn[-1].move(300, 50+25*i)
         
      btn = QtGui.QPushButton('Take screenshot', self)
      btn.clicked.connect(macro.take_screenshot_adb)
      btn.resize(btn.sizeHint())
      btn.move(400,50)
      
      btn = QtGui.QPushButton('GIMP', self)
      btn.clicked.connect(macro.gimpScreenshot)
      btn.resize(btn.sizeHint())
      btn.move(400,75)
      
      btn = QtGui.QPushButton('Clear cache', self)
      btn.clicked.connect(macro.clearMarvelCache)
      btn.resize(btn.sizeHint())
      btn.move(400,100)
      
      btn = QtGui.QPushButton('Check Training', self)
      btn.clicked.connect(macro.checkTraining)
      btn.resize(btn.sizeHint())
      btn.move(400,125)
      
      devices = macro.adbDevices()
#      devices = ["255.255.255.255:5555","127.0.0.1","127.0.0.1","127.0.0.1","127.0.0.1","127.0.0.1","127.0.0.1","127.0.0.1"]

#      listWidget = QtGui.QRadioButton()


#      x = bool(int(settings.value("pyuic4x", "0").toString()))
#  ds    self.pyuic4xCheckBox.setChecked(x)

#      for i,device in enumerate(devices):
#         btn = QtGui.QRadioButton(device, self)
##         btn.setToolTip('This is a <b>QPushButton</b> widget')
#         btn.clicked.connect(partial(macro.setActiveDevice, device, None))
#         btn.resize(btn.sizeHint())
#         btn.move(400, 350+25*i)
         
#      checkbox = QtGui.QCheckBox("Youwave?", self)
#      checkbox.toggled.connect(partial(macro.setActiveDevice, None, checkbox ))
#      checkbox.resize(checkbox.sizeHint())
#      checkbox.move(250, 350)
      
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
      device_list.move(50,50)
      
      self.console = MyConsole(self)
      self.console.move(50,250)
      
      self.custom8_btn = QtGui.QPushButton('Custom 8', self)
      self.custom8_btn.clicked.connect(macro.custom8)
      self.custom8_btn.resize(self.custom8_btn.sizeHint())
      self.custom8_btn.move(400,210)
      

      self.setGeometry(300, 300, 600, 600)
      self.setWindowTitle('Tooltips')    
      self.show()
            
def main():
    
   app = QtGui.QApplication(sys.argv)
   app.setApplicationName('WoH Macro Control GUI')
   
   ex = Example()
   
   myStream = MyStream()
   myStream.message.connect(ex.console.on_myStream_message)
   
   macro.STDOUT_ALTERNATIVE = myStream
   sys.stdout = myStream
   sys.exit(app.exec_())


if __name__ == '__main__':
   main()