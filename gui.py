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
from PyQt4 import Qt, QtGui, QtCore
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

   def __init__(self, parent):
         
      super(DeviceView,self).__init__(parent)
      
      #      macro.adbConnect("localhost:5558")
         
      self.updateList()

      self.tree = QtGui.QTreeView(self)
      self.tree.setModel(self.model)
      self.tree.setRootIsDecorated(False)

#      view.setColumnWidth(0,20)
      self.tree.setColumnWidth(0,170)
      self.tree.setColumnWidth(1,30)
#      self.tree.resize(210,150)
#      tree.move(50,250)

      self.device_name = QtGui.QLineEdit(self)
#      self.ref_field.resize(self.ref_field.sizeHint())
      self.device_name.setToolTip('Device')
      self.device_name.resize(QtCore.QSize(100,self.device_name.sizeHint().height()))
      
      self.device_port = QtGui.QLineEdit(self)
#      self.ref_field.resize(self.ref_field.sizeHint())
      self.device_port.setToolTip('Port')
      self.device_port.setText("5555")
      
      self.device_add = QtGui.QPushButton('Add device', self)
      self.device_add.clicked.connect(self.deviceConnect)
      self.device_add.resize(self.device_add.sizeHint())
      
      self.add_device_layout = QtGui.QHBoxLayout()
      self.add_device_layout.addWidget(self.device_name)
      self.add_device_layout.addWidget(self.device_port)
      self.add_device_layout.addWidget(self.device_add)
      
      self.full_layout = QtGui.QVBoxLayout()
      self.full_layout.addWidget(self.tree)
      self.full_layout.addLayout(self.add_device_layout)

      self.setLayout(self.full_layout)

      a = self.model.item(0,0)
      
   def updateList(self):

      devices = macro.adbDevices()

      self.model = QtGui.QStandardItemModel()
      self.model.setColumnCount(2)
      self.deviceActiveList = {}
      self.deviceYouwaveList = {}
      for i,device in enumerate(devices):
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
            macro.setActiveDevice(device)
#         device.item
         self.model.appendRow([device_item,box])
#         model.appendColumn(box)

      self.model.setHorizontalHeaderLabels(["       Device ID","YW"])
      self.model.itemChanged.connect(self.deviceClicked)
      
   def deviceConnect(self):
      macro.adbConnect(self.device_name.text()+':'+self.device_port.text())
      self.updateList()
      
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
#                macro.setActiveDevice(device_text, self.deviceYouwaveList[str(i)])
               macro.setActiveDevice(device_text)
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

#       print(macro.ACTIVE_DEVICE)
   
#      .connect(partial(macro.startMarvel, user, 1))
   
class ReferralService(QtGui.QFrame):

   def __init__(self, parent):
         
      super(ReferralService,self).__init__(parent)
      self.setStyleSheet("#ReferralService{ margin:0px; border:1px solid rgb(128, 128, 128); padding: 10px; border-radius: 5px }")
      margin = (10,10)
            
      self.setObjectName("ReferralService")
   
      self.start_btn = QtGui.QPushButton('Start', self)
      btn_size = self.start_btn.sizeHint()
      self.start_btn.clicked.connect(self.launchReferral)
      self.start_btn.resize(self.start_btn.sizeHint())
   
      self.ibox = QtGui.QSpinBox(self)
      self.ibox.setMaximum(999)
      self.ibox.setMinimum(1)
      ibox_size = self.ibox.sizeHint()
      self.ibox.resize(QtCore.QSize(ibox_size.width(),btn_size.height()))
      self.ibox.setValue(1)
      self.ibox.setToolTip("Iterations")
   
      self.ref_field = QtGui.QLineEdit(self)
      self.ref_field.resize(self.ref_field.sizeHint())
      self.ref_field.setToolTip('Referral code')
      

      # Boundary stuff
      self.interval_text = QtGui.QLabel(self)
      self.interval_text.setText('Interval:')
      self.interval_text.resize(self.interval_text.sizeHint())

      self.lbox = QtGui.QSpinBox(self)
      self.lbox.setMaximum(999)
      self.lbox.resize(self.lbox.sizeHint())
      self.lbox.setValue(3)
      self.lbox.setToolTip("Wait interval - lower bound")
      
      self.to_text = QtGui.QLabel(self)
      self.to_text.setText('to')
      self.to_text.resize(self.to_text.sizeHint())
      
      self.ubox = QtGui.QSpinBox(self)
      self.ubox.setMaximum(999)
      self.ubox.resize(self.ubox.sizeHint())
      self.ubox.setValue(15)
      self.ubox.setStyleSheet("")
      self.ubox.setToolTip("Wait interval - upper bound")

      self.min_text = QtGui.QLabel(self)
      self.min_text.setText('minutes')
      self.min_text.resize(self.min_text.sizeHint())

      self.nick = QtGui.QComboBox(self)
      self.nick.move(margin[0]+160,margin[1]+30)
      self.nick.blockSignals(True)
      self.nick.addItem(QtCore.QString("Blayd"))
      self.nick.addItem(QtCore.QString("Joey"))
      self.nick.addItem(QtCore.QString("Chris"))
      self.nick.setCurrentIndex(-1)
      self.nick.blockSignals(False)
      self.nick.setCurrentIndex(0)
      self.connect(self.nick, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.setCurrentUser)
      
      self.persist = QtGui.QCheckBox(self)
      self.persist.setText('Never abort')
      self.persist.setToolTip('Specify whether the macro service should continue even if<BR> Joey think it might be a good idea to call it off (because something unexpected may have happened).')
      
      self.draw_ucp = QtGui.QCheckBox(self)
      self.draw_ucp.setText('Draw UCP')
      self.draw_ucp.setToolTip('Draw UCP after tutorial is finished?')
#      self.label = QtGui.QLabel(self)
#      self.label.setText("Hello")
#      self.label.move(-10,0)


      ##########
      # LAYOUT #
      

      self.options_layout = QtGui.QVBoxLayout()

      self.referral_layout = QtGui.QHBoxLayout()
      self.referral_layout.addWidget(self.ref_field)
      self.referral_layout.addWidget(self.ibox)
      
      self.options_layout.addLayout(self.referral_layout)

      self.interval_layout = QtGui.QHBoxLayout()
      self.interval_layout.addWidget(self.interval_text)
      self.interval_layout.addWidget(self.lbox)
      self.interval_layout.addWidget(self.to_text)
      self.interval_layout.addWidget(self.ubox)
      self.interval_layout.addWidget(self.min_text)
      self.interval_layout.addSpacing(2)
      
      self.more_options = QtGui.QHBoxLayout()
      self.more_options.addWidget(self.persist)
      self.more_options.addWidget(self.draw_ucp)
      
      self.options_layout.addLayout(self.interval_layout)
      self.options_layout.addLayout(self.more_options)
     
      self.buttons_layout = QtGui.QVBoxLayout()
      self.buttons_layout.addWidget(self.start_btn)
      self.buttons_layout.addWidget(self.nick)
      
#       self.referral_layout.addWidget(self.start_btn)
     
      self.service_layout = QtGui.QHBoxLayout()
      self.service_layout.addLayout(self.options_layout)
      self.service_layout.addLayout(self.buttons_layout)
      self.service_layout.setAlignment(self.buttons_layout, QtCore.Qt.AlignTop)
      self.setLayout(self.service_layout)

      

      
      self.setStyleSheet("#ReferralService{ margin:0px; border:1px solid rgb(192, 192, 192); padding: 10px; border-radius: 5px }")
#      self.setStyleSheet("background-color: rgb(255,0,0); margin:5px; border:1px solid rgb(0, 255, 0); ")
#      self.setFrameShape(QtGui.QFrame.StyledPanel)
#      self.setFrameStyle(1)
      
      print("Test")
     
   def launchReferral(self):
      
      iterations = self.ibox.value()
      
      lower = self.lbox.value()
      upper = self.ubox.value()
      
      ref_key = str(self.ref_field.text())
      
      never_abort = self.persist.isChecked()
      draw_ucp= self.draw_ucp.isChecked()
      
      macro.createMultipleNewFakeAccounts(iterations, interval=(lower,upper),
                                          referral=ref_key, never_abort=never_abort,
                                          draw_ucp=draw_ucp)
      
   def setCurrentUser(self):
      
      user = str(self.nick.currentText())
      
      macro.user.setCurrent(user)
      
class Buttons(QtGui.QWidget):
   def __init__(self, parent):
      super(Buttons,self).__init__(parent)
      
      self.btn = []
      for i,user in enumerate(macro.info.get('accounts')):
         self.btn.append(QtGui.QPushButton(user, self))
         self.btn[-1].setToolTip('This is a <b>QPushButton</b> widget')
         self.btn[-1].clicked.connect(partial(macro.startMarvel, user, 1))
         self.btn[-1].resize(self.btn[-1].sizeHint())
         self.btn[-1].move(0, 25*i)
         
      self.btn1 = QtGui.QPushButton('Take screenshot', self)
      self.btn1.clicked.connect(macro.take_screenshot_adb)
      self.btn1.resize(self.btn1.sizeHint())
      self.btn1.move(100,50)
      
      self.btn2 = QtGui.QPushButton('GIMP', self)
      self.btn2.clicked.connect(macro.gimpScreenshot)
      self.btn2.resize(self.btn2.sizeHint())
      self.btn2.move(100,75)
      
      self.btn3 = QtGui.QPushButton('Clear cache', self)
      self.btn3.clicked.connect(macro.clearMarvelCache)
      self.btn3.resize(self.btn3.sizeHint())
      self.btn3.move(100,100)
      
      self.btn4 = QtGui.QPushButton('Check Training', self)
      self.btn4.clicked.connect(macro.checkTraining)
      self.btn4.resize(self.btn4.sizeHint())
      self.btn4.move(100,125)
      
      self.custom8_btn = QtGui.QPushButton('Custom 8', self)
      self.custom8_btn.clicked.connect(macro.custom8)
      self.custom8_btn.resize(self.custom8_btn.sizeHint())

class EmittingStream(QtCore.QObject):

   textWritten = QtCore.pyqtSignal(str)
   
   def write(self, text):
      self.textWritten.emit(str(text))

class WoHMacro(QtGui.QWidget):
    
   def __init__(self):
      super(WoHMacro, self).__init__()
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
      
      
      self.device_list = DeviceView(self)
      self.buttons = Buttons(self)
      self.ref_service = ReferralService(self)
      self.console = MyConsole(self)
      
      self.buttons.move(350,10)
      self.ref_service.move(0,250)
      self.console.move(0,450)
      
      

#      self.top_layout = QtGui.QHBoxLayout()
#      self.top_layout.addWidget(self.device_list)
#      self.top_layout.addWidget(self.buttons)
#      
#      self.full_layout = QtGui.QVBoxLayout()
#      self.full_layout.addLayout(self.top_layout)
#      self.full_layout.addWidget(self.ref_service)
#      self.full_layout.addWidget(self.console)
#      self.setLayout(self.full_layout)
#      

      self.setGeometry(300, 300, 600, 800)
      self.setWindowTitle('WoH Macro Control')    
      self.show()
            
def main():
    
   app = QtGui.QApplication(sys.argv)
   app.setApplicationName('WoH Macro Control GUI')
   
   ex = WoHMacro()
   
   myStream = MyStream()
   myStream.message.connect(ex.console.on_myStream_message)
   
#    macro.STDOUT_ALTERNATIVE = myStream
#    sys.stdout = myStream
   sys.exit(app.exec_())


if __name__ == '__main__':

   import os
   try:
      if os.path.exists('dist'):
         os.chdir('dist/woh_macro')
   except:
      pass

   main()
