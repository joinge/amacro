#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

from __future__ import print_function
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

DEBUG = False

def helloWorld(*args, **kwargs):
   logger.info("Hey there")
#    print "Hey there."
#    print args
#    print kwargs

         

class StreamRedirect(QtGui.QWidget):
   message = QtCore.Signal(str)
   
   def __init__(self):
      super(StreamRedirect, self).__init__()
      
      
   def write(self, text):
      self.message.emit(text)
      

class ConsoleView(QtGui.QGroupBox):
   msg_ready = QtCore.Signal()

   def __init__(self, parent):
      super(ConsoleView, self).__init__("Console")
      
      self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      
      
      self.textEdit = QtGui.QTextEdit(self)  
      
#       self.textEdit.setMinimumHeight(300)
#       self.textEdit.setMinimumWidth(600)
#       self.setMinimumHeight(300)
      
      font = QtGui.QFont("monospace")
      font.setStyleHint(QtGui.QFont.Monospace)
      self.textEdit.setFont(font)
      
#       policy = self.textEdit.sizePolicy()
#       policy.setVerticalStretch(1)
#       policy.setHorizontalStretch(1)
#       self.textEdit.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

      # Create Queue and redirect sys.stdout to this queue
      sys.stdout.message.connect(self.addText, Qt.QueuedConnection)


      logger.info("Console initiated...")

   @QtCore.Slot(int, int)
   def adaptSize(self, width, height):
      self.textEdit.resize(width, height)   


   @QtCore.Slot(str)
   def addText(self, message):
      self.textEdit.moveCursor(QtGui.QTextCursor.End)
      self.textEdit.insertPlainText(message)
      self.textEdit.show()



class DeviceView(QtGui.QGroupBox):
   get_device_list   = QtCore.Signal()
   set_active_device = QtCore.Signal(str)

   def __init__(self, parent, device, settings):

      super(DeviceView, self).__init__("Devices")
      
      self.device = device
      
      self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
      

      
      self.get_device_list.connect(self.device.getDeviceList, Qt.QueuedConnection)
      self.device.device_list.connect(self.updateDeviceList, Qt.QueuedConnection)
      
      self.set_active_device.connect(self.device.setActive, Qt.QueuedConnection)
#       self.device.device_list.connect(self.updateDeviceList, Qt.QueuedConnection)
      
      
      
#       self.update_list_worker = Worker()
      
      
      #      macro.adbConnect("localhost:5558")

      self.model = QtGui.QStandardItemModel()
      self.model.setColumnCount(2)
      self.model.setHorizontalHeaderLabels(["       Device ID", "Type"])

      self.tree = QtGui.QTreeView(self)
      self.tree.setModel(self.model)
      self.tree.setRootIsDecorated(False)

      

      self.tree.setColumnWidth(0,170)
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
      
      self.group_layout = QtGui.QVBoxLayout()
      self.group_layout.addWidget(self.tree)
      self.group_layout.addLayout(self.add_device_layout)

#       self.group_box = QtGui.QGroupBox(self, "Devices")
#       self.group_box.setLayout(self.group_layout)
#       self.final_layout = QtGui.QLayout()
#       self.final_layout.addWidget(self.group_box)

      self.setLayout(self.group_layout)


      self.get_device_list.emit()
      
   @QtCore.Slot(int, int)
   def adaptSize(self, width, height):
      
      self.tree.resize(width, height)
      
      
   @QtCore.Slot(list)
   def updateDeviceList(self, devices):
      
#       devices = devices
      
      self.model.beginResetModel()

      self.deviceActiveList = {}
      self.deviceYouwaveList = {}
      for i, device in enumerate(devices):
#         status = QtGui.QStandardItem("")
         device_item = QtGui.QStandardItem(device)
         self.deviceActiveList[str(i)] = False
         self.deviceYouwaveList[str(i)] = False
         box = QtGui.QStandardItem("      ")
#         box.setTextAlignment(QtCore.Qt.AlignRight)
#         box = QtGui.QCheckBox("Youwave?", self) #QtGui.QStandardItem("xxx")
         device_item.setCheckable(True)
         box.setCheckable(True)
         if i == 0:
            device_item.setCheckState(QtCore.Qt.CheckState(2))
            self.deviceActiveList[str(i)] = True
            self.set_active_device.emit(device)
#         device.item
         self.model.appendRow([device_item, box])
#         model.appendColumn(box)

#       self.tree.resizeColumnToContents()
      self.model.itemChanged.connect(self.deviceClicked)
      self.device_name.setText('')
      
      self.model.beginResetModel()

      
   def deviceConnect(self):
      self.device.adbConnect(str(self.device_name.text()) + ':' + str(self.device_port.text()))
      self.updateDeviceList()
      
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
   take_screenshot   = QtCore.Signal()
   
   def __init__(self, parent, device):
      super(Buttons, self).__init__(parent)
      
      self.device = device
      
      self.imageLabel = QtGui.QLabel()
      self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
#       self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
      self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
#       self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
      self.imageLabel.setScaledContents(True)
      self.imageLabel.resize(16*10,9*10)
      
      self.rotate = QtGui.QCheckBox(self)
      self.rotate.setText('Rotate')
      self.rotate.setToolTip("Huh? Don't ask... <BR> Joey ")
      self.rotate.setChecked(False)
      self.rotate.released.connect(self.updateScreenshot)
      
      self.refresh_timer = QtCore.QTimer()
      self.refresh = QtGui.QCheckBox(self)
      self.refresh.setText('Refresh')
      self.refresh.setChecked(False)
      self.refresh.released.connect(self.autoRefreshScreenshot)
      
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
      self.btn2.clicked.connect(lambda: self.device.gimpScreenshot(self.current_image_filename), Qt.QueuedConnection)
      self.btn2.resize(self.btn2.sizeHint())
#       self.btn2.move(100,75)

      self.setMinimumWidth(500)
#       
#       self.btn3 = QtGui.QPushButton('Clear cache', self)
#       self.btn3.clicked.connect(macro.clearMarvelCache)
#       self.btn3.resize(self.btn3.sizeHint())
#       self.btn3.move(100,100)
      
      self.btn4 = QtGui.QPushButton('Hello', self)
      self.btn4.clicked.connect(helloWorld)
      self.btn4.resize(self.btn4.sizeHint())
#       self.btn4.move(100,125)
      

      self.screenshot_btn = QtGui.QPushButton('Take Screenshot', self)
      self.screenshot_btn.resize(self.screenshot_btn.sizeHint())
#       self.take_screenshot.connect(device.takeScreenshot, Qt.QueuedConnection)
      self.screenshot_btn.clicked.connect(device.takeScreenshot, Qt.QueuedConnection)
      self.device.screenshot_ready.connect(self.updateScreenshot, Qt.QueuedConnection)
      
      self.hlayout = QtGui.QHBoxLayout()
      self.hlayout.addWidget(self.screenshot_btn)
      self.hlayout.addWidget(self.rotate)
      self.hlayout.addWidget(self.refresh)
      self.hlayout.addWidget(self.btn2)
      self.hlayout.addWidget(self.btn4)
      
      self.vlayout = QtGui.QVBoxLayout()
      self.vlayout.addWidget(self.imageLabel)
      self.vlayout.addLayout(self.hlayout)
      
#       self.vlayout = QtGui.QHBoxLayout()
#       self.vlayout.addLayout(self.group_layout)
#       self.vlayout.addWidget(self.imageLabel)
      
      self.setLayout(self.vlayout)
       
      

   @QtCore.Slot(str)
   def updateScreenshot(self, filename=None):
#       fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath())
      
      if filename:
         self.current_image_filename = filename
      else:
         filename = self.current_image_filename
         
      image = QtGui.QImage(filename)
      if image.isNull():
         QtGui.QMessageBox.information(self, "Image Viewer", "Cannot load %s." % filename)
         return
      
      pixmap = QtGui.QPixmap.fromImage(image)
      
      if self.rotate.isChecked():
         rm = QtGui.QMatrix()
         rm.rotate(90)
         pixmap = pixmap.transformed(rm)
      
   
      self.imageLabel.setPixmap(pixmap)
#       self.scaleFactor = 1.0
#    
#       self.printAct.setEnabled(True)
#       self.fitToWindowAct.setEnabled(True)
#       self.updateActions()
#    
#       if not self.fitToWindowAct.isChecked():
#          self.imageLabel.adjustSize()

   @QtCore.Slot()
   def autoRefreshScreenshot(self):
      
      if self.refresh.isChecked():
      
         self.refresh_timer.setInterval(10000)
         self.refresh_timer.timeout.connect(self.device.takeScreenshot, Qt.QueuedConnection)
         self.refresh_timer.start()
         
      else:
         self.refresh_timer.stop()
      
         
            
            
         
         
      
class CentralWidget(QtGui.QWidget):
   def __init__(self, parent, settings):
      super(CentralWidget, self).__init__(parent)
      
      self.settings = settings
         
      self.initUI(settings)
   

   def initUI(self, settings):
      
      self.device_thread = QtCore.QThread()
      self.device = Device(settings)
      self.device.moveToThread(self.device_thread)
      self.device_thread.start()
       
      self.device_list = DeviceView(self, self.device, settings)
      
      self.console = ConsoleView(self)
      
      self.buttons = Buttons(self, self.device)
      
# #       self.ref_service = ReferralService(self)

      frame = QtGui.QFrame()
      frame.setFrameShape(frame.Box)
      
      frame2 = QtGui.QFrame()
      frame2.setFrameShape(frame2.Box)
      
      frame3 = QtGui.QFrame()
      frame3.setFrameShape(frame3.Box)
  
     
      self.horizontal_layout = QtGui.QHBoxLayout()
      self.horizontal_layout.addWidget(self.device_list)
      self.horizontal_layout.addWidget(self.buttons)
      
#       self.grid_layout = QtGui.QGridLayout(self)
# #       self.grid_layout.setSpacing(10)
#       
#       self.grid_layout.addWidget(self.device_list, 0, 0)
# # #       self.grid_layout.a
# #       self.grid_layout.addWidget(self.buttons, 0, 1)
# #       self.grid_layout.addWidget(self.console, 1, 0)
#       
# #       self.grid_layout.addWidget(frame, 1, 1)
# #       self.grid_layout.a
#       self.grid_layout.addWidget(self.buttons, 0, 1)
#       self.grid_layout.addWidget(self.console, 1, 0, 2, 2)
      
#       
#       self.hsplit = QtGui.QSplitter(self)
#       self.hsplit.add
      
      self.vlayout = QtGui.QVBoxLayout()
      self.vlayout.addLayout(self.horizontal_layout)
      self.vlayout.addWidget(self.console)
      
#       self.resizeEvent().connect(self.console.adaptSize)
#       self.resize(self.geometry().width(), self.geometry().height())     
      
      
#       self.group_layout = QtGui.QVBoxLayout()
#       self.group_layout.addLayout(self.horizontal_layout)
#       self.group_layout.addWidget(self.console)
#       self.group_layout.addWidget(self.status_bar)

      self.setLayout(self.vlayout)
      
      
      
#       
# #       self.buttons.move(350,10)
# #       self.ref_service.move(0,250)
#       self.console.move(0,450)
#       
      self.setGeometry(300, 300, 600, 800)
      self.setWindowTitle('Android Macro Control')  
      self.show()
      

#       
#    def queueWork(self, fn, *args, **kwargs):
#       pass
#       
#    def workerFinished(self):
#       print("Worker finished")


   def resizeEvent(self, resizeEvent):
      left,top,right,bottom = self.vlayout.getContentsMargins()
      width,height = (self.geometry().width(), self.geometry().height())
      self.console.adaptSize(width-left-right, 0.5*(height-top-bottom))
#       self.device_list.adaptSize(0.5*self.geometry().width(), 0.5*self.geometry().height())
      
class MainWindow(QtGui.QMainWindow):
    
   def __init__(self, settings):
      QtGui.QMainWindow.__init__(self, parent=None)
      
      self.settings = settings
#       self.worker = Worker()
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

      self.central_widget = CentralWidget(self, settings)
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

      
      self.setWindowTitle('Android Macro Control')  
      self.setGeometry(300, 300, 600, 800)
      self.show()


            
def main():
   app = QtGui.QApplication(sys.argv)

   sys.stdout = StreamRedirect()
   sys.stderr = StreamRedirect()   
   setupLogging()
    
   app.setApplicationName('Android Macro Control GUI')
   
   settings = Settings()
   
   ex = MainWindow(settings)
   
   sys.exit(app.exec_())
   
   # Restore sys.stdout
   sys.stdout = sys.__stdout__


if __name__ == '__main__':

#   import os
#   try:
#      if os.path.exists('dist'):
#         os.chdir('dist/woh_macro')
#   except:
#      pass

   main()
