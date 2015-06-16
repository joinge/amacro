
import os

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import logging
logger = logging.getLogger(__name__)


class GuiSettings(QtGui.QWidget):
   def __init__(self):
      super(GuiSettings).__init__(self)
      
    
      exit_action = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
      exit_action.setShortcut('Ctrl+Q')
      exit_action.setStatusTip('Exit application')
      exit_action.triggered.connect(QtGui.qApp.quit)
            
      menubar = self.menuBar()
      file_menu = menubar.addMenu('&File')
      file_menu.addAction(exit_action)

#       self.central_widget = CentralWidget(self, settings)
#       self.setCentralWidget(self.central_widget)  # new central widget        
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
      

#       self.statusBar().showMessage("Ready")

      
#       self.setWindowTitle('Android Macro Control')  
      self.setGeometry(300, 300, 600, 800)
#       self.show()
      
#       
# 
#    def paintEvent(self, e):
#       dc = QPainter(self)
#       dc.drawLine(0, 0, 100, 100)
#      dc.drawLine(100, 0, 0, 100)
     
class Settings:
   def __init__(self):
      self.ANDROID_SDK_PATH     = "/home/me/Apps/Genymotion/genymotion"
      self.ANDROID_UTILS_PATH   = "/home/me/Apps/Genymotion/genymotion/tools"
      
      self.EMULATOR_PATH        = "/home/me/Apps/Genymotion/genymotion"
      
      self.MACRO_ROOT           = "/home/me/clash/amacro"
      self.TEMP_PATH            = self.MACRO_ROOT + "/tmp"
      self.SCREEN_PATH          = self.MACRO_ROOT + "/screens"

      
      self.TESSERACT_FONTS_PATH = self.MACRO_ROOT + "/tesseract/fonts"
      self.TESSERACT_PATH       = self.MACRO_ROOT + "/tesseract/tesseract-ocr/build/bin"
      
      self.MACRO_SCRIPTS        = self.MACRO_ROOT + "/scripts"

      self.LOG_FILE             = self.MACRO_ROOT + "/macro.log"
      
      self.ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
      self.abc = 'abcdefghijklmnopqrstuvwxyz'
      self.num = '0123456789'
      self.hex = self.num+'abcdef'
      
      try:    os.mkdir(self.TEMP_PATH)
      except: pass
