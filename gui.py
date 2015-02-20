#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

# import macro
import sys

import sip
from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from Queue import Queue

import logging
logger = logging.getLogger(__name__)

from functools import partial
import functools

from Device import Device
from Settings import Settings
from printing import setupLogging

import time
import sys

DEBUG = False

def helloWorld(*args, **kwargs):
   logger.info("Hey there")
#    print "Hey there."
#    print args
#    print kwargs


# very testable class (hint: you can use mock.Mock for the signals)
class Worker(QtCore.QObject):
   
   thread = QtCore.QThread()
   
   def __init__(self, parent=None):
      super(Worker, self).__init__(parent)
      
      self.finished = QtCore.Signal()
      self.output = QtCore.Signal(list)

      self.queue = Queue()
#       self.exiting = False
      

      self.moveToThread(self.thread)
      self.thread.start()
      
#    def __del__(self):
#       self.thread.wait()

   def stop(self):
      self.thread.wait()

      
   @QtCore.Slot()
   def handler(self):
      
      data = self.fn()

      print "self.signal_string)"
      self.emit(QtCore.SIGNAL(self.signal_string), data)
      self.finished.emit()
      
#       if data:
#          self.output.emit(data)
#          
#       file = open('tmp.txt','a')
#       file.write("7")
#       file.close()
#       
      
   def enqueueMethod(self, fn, *args, **kwargs):
      if DEBUG:
         self.fn = lambda: fn(*args, **kwargs)
         
         data = self.fn()

         self.finished.emit()
         
         if data:
            self.output.emit(data)
         
#          return self.handler()
      else:
         self.fn = lambda: fn(*args, **kwargs)
      
         QtCore.QMetaObject.invokeMethod(self, "handler", Qt.QueuedConnection)
      
   def whenFinishedEmit(self, fn):
#       self.signal_string = signal_string
      self.output.connect(fn)

#    def invokeMethod(self, fn, return_type, *args, **kwargs):
# #       from PyQt4 import QtCore
#       
#       if DEBUG:
#          return (lambda: fn( *args, **kwargs))()
#       else:
#          
#          retval = []
#          QtCore.QMetaObject.invokeMethod(self, "run", Qt.QueuedConnection,
#                QtCore.Q_RETURN_ARG(return_type, retval),
#                QtCore.Q_ARG(list, [lambda: fn( *args, **kwargs)]))
# #                                 QtCore.Q_ARG(tuple, (1,2,3)),
# #                                 QtCore.Q_ARG(dict, {'abc':5, 'd':7}))
#          self.finished.emit()
#          self.output.emit([retval])
# 
#    def start(self):
#       self.thread.start()
#       
#    def stop(self):
#       self.thread.stop()


# A QObject (to be run in a QThread) which sits waiting for output to come through a Queue.Queue().
# It blocks until output is available, and one it has got something from the queue, it sends
# it to the "MainThread" by emitting a Qt Signal 
class MyReceiver(QtCore.QObject):
   mysignal = QtCore.Signal(str)
   
   def __init__(self, *args, **kwargs):
      QtCore.QObject.__init__(self, *args, **kwargs)
   
   def emitMessage(self, text):
      self.mysignal.emit(text)
#       while True:
#          text = self.queue.get()
#          self.mysignal.emit(text)
         

class WriteStream(object):
   def __init__(self):
      self.emitter = MyReceiver()
#       self.queue = queue
   
   def write(self, text):
      self.emitter.emitMessage(text)
#       self.mysignal.emit(text)
#       self.queue.put(text)
#       QtCore.QMetaObject.invokeMethod(self, "run", Qt.QueuedConnection, QtCore.Q_ARG(str, text))
      



class MyConsole(QtGui.QWidget):
   queue = Queue()
   msg_ready = QtCore.Signal()

   def __init__(self, parent, worker):
      
      super(MyConsole, self).__init__(parent)
      self.worker = Worker()
      
      self.textEdit = QtGui.QTextEdit(self)  
      
      self.textEdit.setMinimumHeight(300)
      self.setMinimumHeight(300)
      
#       self.textEdit.resize(500,300)   

      # Create Queue and redirect sys.stdout to this queue
#       self.queue = Queue()
#       sys.stdout = WriteStream(self.queue)

      self.msg_ready.connect(self.outOfMessageQueue)


      if not DEBUG:
         sys.stdout = WriteStream()
         sys.stdout.emitter.mysignal.connect(self.intoMessageQueue)


      
      # Create thread that will listen on the other end of the queue, and send the text to the textedit in our application
#       self.thread = QtCore.QThread()
#       self.my_receiver = MyReceiver(self.queue)
#       self.my_receiver.mysignal.connect(self.on_myStream_message)
#       self.my_receiver.moveToThread(self.thread)
#       self.thread.started.connect(self.my_receiver.run)
#       self.thread.start()
      
   @QtCore.Slot()
   def outOfMessageQueue(self):
      message = self.queue.get()
      self.textEdit.moveCursor(QtGui.QTextCursor.End)
      self.textEdit.insertPlainText(message)
      self.textEdit.show()
      
   @QtCore.Slot(str)
   def intoMessageQueue(self, message):
      self.queue.put(message)
      self.msg_ready.emit()


class DeviceView(QtGui.QWidget):

   def __init__(self, parent, settings, worker):

      super(DeviceView, self).__init__(parent)
      
      self.update_list_worker = Worker()
      
      self.device = Device(settings)
      
      #      macro.adbConnect("localhost:5558")

      self.model = QtGui.QStandardItemModel()
      self.model.setColumnCount(2)
      self.model.setHorizontalHeaderLabels(["       Device ID", "Type"])

      self.tree = QtGui.QTreeView(self)
      self.tree.setModel(self.model)
      self.tree.setRootIsDecorated(False)

#       self.tree.setColumnWidth(0,170)
#       self.tree.setColumnWidth(1,30)


      self.device_name = QtGui.QLineEdit(self)
      self.device_name.setToolTip('Device')
      self.device_name.resize(QtCore.QSize(150, self.device_name.height()))
      self.device_name.setMinimumWidth(150)
      
      self.device_port = QtGui.QLineEdit(self)
      self.device_port.setToolTip('Port')
      self.device_port.setText("5555")
      self.device_port.setMaximumWidth(50)
      
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

#       self.updateList()

#       file = open('tmp.txt','a')
#       file.write("1")
#       file.close()

      self.update_list_worker.whenFinishedEmit("deviceList(list)")
      self.connect(self.update_list_worker,
                   QtCore.SIGNAL("deviceList(list)"),
                   self.updateList)
#       
#       self.update_list_worker.connectOutputTo(self.updateList)
      self.update_list_worker.enqueueMethod(self.device.adbDevices)
#       
#       file = open('tmp.txt','a')
#       file.write("8")
#       file.close()
      
#       worker = Worker()
#       worker.output.connect(self.updateList)
#       worker.invokeMethod(self.device.adbDevices, list)
      
      
   @QtCore.Slot(list)
   def updateList(self, devices):
      
#       devices = devices
      
      self.model.beginResetModel()

      self.deviceActiveList = {}
      self.deviceYouwaveList = {}
      for i, device in enumerate(devices):
#         status = QtGui.QStandardItem("")
         device_item = QtGui.QStandardItem(device)
         self.deviceActiveList[str(i)] = False
         self.deviceYouwaveList[str(i)] = False
         box = QtGui.QStandardItem("")
#         box.setTextAlignment(QtCore.Qt.AlignRight)
#         box = QtGui.QCheckBox("Youwave?", self) #QtGui.QStandardItem("xxx")
         device_item.setCheckable(True)
         box.setCheckable(True)
         if i == 0:
            device_item.setCheckState(QtCore.Qt.CheckState(2))
            self.deviceActiveList[str(i)] = True
            self.device.setActive(device)
#         device.item
         self.model.appendRow([device_item, box])
#         model.appendColumn(box)

      self.model.itemChanged.connect(self.deviceClicked)
      self.device_name.setText('')
      
      self.model.beginResetModel()

      
   def deviceConnect(self):
      self.device.adbConnect(str(self.device_name.text()) + ':' + str(self.device_port.text()))
      self.updateList()
      
   def deviceClicked(self):
      
      device_selected = False
      for i in range(self.model.rowCount()):
         if self.model.item(i, 1).checkState() == 2:
            self.deviceYouwaveList[str(i)] = True
         else:
            self.deviceYouwaveList[str(i)] = False
                  
         if self.model.item(i, 0).checkState() == 2:
            device_selected = True
            device_text = str(self.model.item(i, 0).text())
            if self.deviceActiveList[str(i)] == False:
#                macro.setActiveDevice(device_text, self.deviceYouwaveList[str(i)])
               self.device.setActiveDevice(device_text)
               self.deviceActiveList[str(i)] = True
               
               for j in range(self.model.rowCount()):
                  device_text = str(self.model.item(j, 0).text())
                  if not i == j:
                     self.model.item(j, 0).setCheckState(QtCore.Qt.CheckState(0))
                     self.deviceActiveList[str(j)] = False

      if not device_selected:
         for i in range(self.model.rowCount()):
            state = 0
            if self.deviceActiveList[str(i)]:
               state = 2

            self.model.item(i, 0).setCheckState(QtCore.Qt.CheckState(state))

#       print(macro.ACTIVE_DEVICE)
   
#      .connect(partial(macro.startMarvel, user, 1))
   
# class ReferralService(QtGui.QFrame):
# 
#    def __init__(self, parent):
#          
#       super(ReferralService,self).__init__(parent)
#       self.setStyleSheet("#ReferralService{ margin:0px; border:1px solid rgb(128, 128, 128); padding: 10px; border-radius: 5px }")
#       margin = (10,10)
#             
#       self.setObjectName("ReferralService")
#    
#       self.start_btn = QtGui.QPushButton('Start', self)
#       btn_size = self.start_btn.sizeHint()
#       self.start_btn.clicked.connect(self.launchReferral)
#       self.start_btn.resize(self.start_btn.sizeHint())
#    
#       self.ibox = QtGui.QSpinBox(self)
#       self.ibox.setMaximum(999)
#       self.ibox.setMinimum(1)
#       ibox_size = self.ibox.sizeHint()
#       self.ibox.resize(QtCore.QSize(ibox_size.width(),btn_size.height()))
#       self.ibox.setValue(100)
#       self.ibox.setToolTip("Iterations")
#    
#       self.ref_field = QtGui.QLineEdit(self)
#       self.ref_field.resize(self.ref_field.sizeHint())
#       self.ref_field.setToolTip('Referral code')
#       
# 
#       # Boundary stuff
#       self.interval_text = QtGui.QLabel(self)
#       self.interval_text.setText('Interval:')
#       self.interval_text.resize(self.interval_text.sizeHint())
# 
#       self.lbox = QtGui.QSpinBox(self)
#       self.lbox.setMaximum(999)
#       self.lbox.resize(self.lbox.sizeHint())
#       self.lbox.setValue(0)
#       self.lbox.setToolTip("Wait interval - lower bound")
#       
#       self.to_text = QtGui.QLabel(self)
#       self.to_text.setText('to')
#       self.to_text.resize(self.to_text.sizeHint())
#       
#       self.ubox = QtGui.QSpinBox(self)
#       self.ubox.setMaximum(999)
#       self.ubox.resize(self.ubox.sizeHint())
#       self.ubox.setValue(0)
#       self.ubox.setStyleSheet("")
#       self.ubox.setToolTip("Wait interval - upper bound")
# 
#       self.min_text = QtGui.QLabel(self)
#       self.min_text.setText('minutes')
#       self.min_text.resize(self.min_text.sizeHint())
# 
#       self.nick = QtGui.QComboBox(self)
#       self.nick.move(margin[0]+160,margin[1]+30)
#       self.nick.blockSignals(True)
#       self.nick.addItem(QtCore.QString("Blayd"))
#       self.nick.addItem(QtCore.QString("Joey"))
#       self.nick.addItem(QtCore.QString("Chris"))
#       self.nick.setCurrentIndex(-1)
#       self.nick.blockSignals(False)
#       self.nick.setCurrentIndex(0)
#       self.connect(self.nick, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.setCurrentUser)
#       
#       self.persist = QtGui.QCheckBox(self)
#       self.persist.setText('Never abort')
#       self.persist.setToolTip('Specify whether the macro service should continue even if<BR> Joey think it might be a good idea to call it off (because something unexpected may have happened).')
#       self.persist.setChecked(True)
#       
#       self.draw_ucp = QtGui.QCheckBox(self)
#       self.draw_ucp.setText('Draw UCP')
#       self.draw_ucp.setToolTip('Draw UCP after tutorial is finished?')
# #      self.label = QtGui.QLabel(self)
# #      self.label.setText("Hello")
# #      self.label.move(-10,0)
# 
# 
#       ##########
#       # LAYOUT #
#       
# 
#       self.options_layout = QtGui.QVBoxLayout()
# 
#       self.referral_layout = QtGui.QHBoxLayout()
#       self.referral_layout.addWidget(self.ref_field)
#       self.referral_layout.addWidget(self.ibox)
#       
#       self.options_layout.addLayout(self.referral_layout)
# 
#       self.interval_layout = QtGui.QHBoxLayout()
#       self.interval_layout.addWidget(self.interval_text)
#       self.interval_layout.addWidget(self.lbox)
#       self.interval_layout.addWidget(self.to_text)
#       self.interval_layout.addWidget(self.ubox)
#       self.interval_layout.addWidget(self.min_text)
#       self.interval_layout.addSpacing(2)
#       
#       self.more_options = QtGui.QHBoxLayout()
#       self.more_options.addWidget(self.persist)
#       self.more_options.addWidget(self.draw_ucp)
#       
#       self.options_layout.addLayout(self.interval_layout)
#       self.options_layout.addLayout(self.more_options)
#      
#       self.buttons_layout = QtGui.QVBoxLayout()
#       self.buttons_layout.addWidget(self.start_btn)
#       self.buttons_layout.addWidget(self.nick)
#       
# #       self.referral_layout.addWidget(self.start_btn)
#      
#       self.service_layout = QtGui.QHBoxLayout()
#       self.service_layout.addLayout(self.options_layout)
#       self.service_layout.addLayout(self.buttons_layout)
#       self.service_layout.setAlignment(self.buttons_layout, QtCore.Qt.AlignTop)
#       self.setLayout(self.service_layout)
# 
#       
# 
#       
#       self.setStyleSheet("#ReferralService{ margin:0px; border:1px solid rgb(192, 192, 192); padding: 10px; border-radius: 5px }")
# #      self.setStyleSheet("background-color: rgb(255,0,0); margin:5px; border:1px solid rgb(0, 255, 0); ")
# #      self.setFrameShape(QtGui.QFrame.StyledPanel)
# #      self.setFrameStyle(1)
#       
#       print("Test")
#      
#    def launchReferral(self):
#       
#       iterations = self.ibox.value()
#       
#       lower = self.lbox.value()
#       upper = self.ubox.value()
#       
#       ref_key = str(self.ref_field.text())
#       
#       never_abort = self.persist.isChecked()
#       draw_ucp= self.draw_ucp.isChecked()
#       
#       macro.createMultipleNewFakeAccounts(iterations, interval=(lower,upper),
#                                           referral=ref_key, never_abort=never_abort,
#                                           draw_ucp=draw_ucp)
#       
#    def setCurrentUser(self):
#       
#       user = str(self.nick.currentText())
#       
#       macro.user.setCurrent(user)
      
class Buttons(QtGui.QWidget):
   def __init__(self, parent, device):
      super(Buttons, self).__init__(parent)
      
#       self.btn = []
#       for i,user in enumerate(macro.info.get('accounts')):
#          self.btn.append(QtGui.QPushButton(user, self))
#          self.btn[-1].setToolTip('This is a <b>QPushButton</b> widget')
#          self.btn[-1].clicked.connect(partial(macro.startMarvel, user, 1))
#          self.btn[-1].resize(self.btn[-1].sizeHint())
#          self.btn[-1].move(0, 25*i)
#          
#       self.btn1 = QtGui.QPushButton('Take screenshot', self)
#       self.btn1.clicked.connect(self.takeScreenshot)
#       self.btn1.resize(self.btn1.sizeHint())
#       self.btn1.move(100,50)
#       
      self.btn2 = QtGui.QPushButton('GIMP', self)
      self.btn2.clicked.connect(device.gimpScreenshot)
      self.btn2.resize(self.btn2.sizeHint())
#       self.btn2.move(100,75)

      self.setMinimumWidth(75)
#       
#       self.btn3 = QtGui.QPushButton('Clear cache', self)
#       self.btn3.clicked.connect(macro.clearMarvelCache)
#       self.btn3.resize(self.btn3.sizeHint())
#       self.btn3.move(100,100)
      
      self.btn4 = QtGui.QPushButton('Hello', self)
      self.btn4.clicked.connect(helloWorld)
      self.btn4.resize(self.btn4.sizeHint())
#       self.btn4.move(100,125)
      
      self.full_layout = QtGui.QVBoxLayout()
      self.full_layout.addWidget(self.btn2)
      self.full_layout.addWidget(self.btn4)
      self.setLayout(self.full_layout)
#       
#       self.custom8_btn = QtGui.QPushButton('Custom 8', self)
#       self.custom8_btn.clicked.connect(macro.custom8)
#       self.custom8_btn.resize(self.custom8_btn.sizeHint())

class EmittingStream(QtCore.QObject):

   textWritten = QtCore.Signal(str)
   
   def write(self, text):
      self.textWritten.emit(str(text))
      
      
class CentralWidget(QtGui.QWidget):
   def __init__(self, settings, worker):
      super(CentralWidget, self).__init__()
      
      self.settings = settings
      self.worker = worker
         
      self.initUI(settings, worker)
   
   def normalOutputWritten(self, text):
      """Append text to the QTextEdit."""
      # Maybe QTextEdit.append() works as well, but this is how I do it:
      cursor = self.textEdit.textCursor()
      cursor.movePosition(QtGui.QTextCursor.End)
      cursor.insertText(text)
      self.textEdit.setTextCursor(cursor)
      self.textEdit.ensureCursorVisible()
       
   def initUI(self, settings, worker):
       

      
      
#       sys.exit(self.exec_())
      
      
      self.console = MyConsole(self, worker)
      self.device_list = DeviceView(self, settings, worker)
      self.buttons = Buttons(self, self.device_list.device)
# #       self.ref_service = ReferralService(self)
      
  
     
#       self.horizontal_layout = QtGui.QHBoxLayout()
#       self.horizontal_layout.addWidget(self.device_list)
#       self.horizontal_layout.addWidget(self.buttons)
      
      self.grid_layout = QtGui.QGridLayout()
      self.grid_layout.setSpacing(10)
      
      self.grid_layout.addWidget(self.device_list, 1, 0)
#       self.grid_layout.a
      self.grid_layout.addWidget(self.buttons, 1, 1)
      self.grid_layout.addWidget(self.console, 2, 0)
      
      
#       self.full_layout = QtGui.QVBoxLayout()
#       self.full_layout.addLayout(self.horizontal_layout)
#       self.full_layout.addWidget(self.console)
#       self.full_layout.addWidget(self.status_bar)

      self.setLayout(self.grid_layout)
      
      
      
#       
# #       self.buttons.move(350,10)
# #       self.ref_service.move(0,250)
#       self.console.move(0,450)
#       
#       self.setGeometry(300, 300, 600, 800)
      self.setWindowTitle('Android Macro Control')  
      self.show()
      

#       
#    def queueWork(self, fn, *args, **kwargs):
#       pass
#       
#    def workerFinished(self):
#       print("Worker finished")
      
class MainWindow(QtGui.QMainWindow):
    
   def __init__(self, settings):
      QtGui.QMainWindow.__init__(self, parent=None)
      
      self.settings = settings
      self.worker = Worker()
      self.setupUi(settings)
      
   def setupUi(self, settings):
#       self.setObjectName(_fromUtf8("self"))

#       QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
      
#       self.setToolTip('Macro Control GUI')


#       self.resize(300, 300)
# #       self.setGeometry(300, 300, 600, 800)
#       
#       
#       self.centralwidget = QtGui.QWidget(self)
#       self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
#       self.pushButton = QtGui.QPushButton(self.centralwidget)
#       self.pushButton.setGeometry(QtCore.QRect(40, 40, 75, 23))
#       self.pushButton.setObjectName(_fromUtf8("pushButton"))
#       self.setCentralWidget(self.centralwidget)
#       self.menubar = QtGui.QMenuBar(self)
#       self.menubar.setGeometry(QtCore.QRect(0, 0, 184, 21))
#       self.menubar.setObjectName(_fromUtf8("menubar"))
#       self.setMenuBar(self.menubar)
#       self.statusbar = QtGui.QStatusBar(self)
#       self.statusbar.setObjectName(_fromUtf8("statusbar"))
#       self.setStatusBar(self.statusbar)

      exit_action = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
      exit_action.setShortcut('Ctrl+Q')
      exit_action.setStatusTip('Exit application')
      exit_action.triggered.connect(QtGui.qApp.quit)
      
      self.statusBar()
      
      menubar = self.menuBar()
      file_menu = menubar.addMenu('&File')
      file_menu.addAction(exit_action)

      self.central_widget = CentralWidget(settings, self.worker)
      self.setCentralWidget(self.central_widget)  # new central widget        
#         
# #      self.process = QtCore.QProcess(self)
# #      self.terminal = QtGui.QWidget(self)
# #      sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
# 
#       self.status_bar = QtGui.QStatusBar(self)
#       self.status_bar.setObjectName(_fromUtf8("statusbar"))
#       self.status_bar.setToolTip("Initialized")
#       self.setStatusBar(self.status_bar)
#       
#       QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
#       self.setToolTip('Macro Control GUI')
      

      self.statusBar().showMessage("Ready")
      
      
#       self.worker.start()
      
      self.setWindowTitle('Android Macro Control')  
      self.setGeometry(300, 300, 600, 800)
      self.show()
      
      
   def __del__(self):
      # Restore sys.stdout
      sys.stdout = sys.__stdout__
      
#    @QtCore.pyqtSlot(str)
#    def append_text(self,text):
#       text_editor = self.central_widget.console.textEdit
#       text_editor.moveCursor(QtGui.QTextCursor.End)
#       text_editor.insertPlainText( text )
      
#    def normalOutputWritten(self, text):
#       """Append text to the QTextEdit."""
#       # Maybe QTextEdit.append() works as well, but this is how I do it:
#       cursor = self.textEdit.textCursor()
#       cursor.movePosition(QtGui.QTextCursor.End)
#       cursor.insertText(text)
#       self.textEdit.setTextCursor(cursor)
#       self.textEdit.ensureCursorVisible()
       
      
   def queueWork(self, fn, *args, **kwargs):
      pass
      
   def workerFinished(self):
      print("Worker finished")
            
def main():
   
   setupLogging()
    
   app = QtGui.QApplication(sys.argv)
   app.setApplicationName('Android Macro Control GUI')
   
   settings = Settings()
   
   ex = MainWindow(settings)
   
#    myStream.message.connect(ex.console.on_myStream_message)
   
#    macro.STDOUT_ALTERNATIVE = myStream
#    sys.stdout = myStream
   sys.exit(app.exec_())


if __name__ == '__main__':

#   import os
#   try:
#      if os.path.exists('dist'):
#         os.chdir('dist/woh_macro')
#   except:
#      pass

   main()
