import os

class Settings:
   def __init__(self):
      home = os.environ['HOME']
      self.PROJECT_PATH         = home + "/Work/Code/rk"
      self.SCREEN_PATH          = self.PROJECT_PATH + "/screens"
      
      self.ANDROID_SDK_PATH     = home + "/Apps/android-sdk-linux"
      
      self.EMULATOR_PATH        = home + "/Apps/genymotion"
      
      self.ANDROID_UTILS_PATH   = self.EMULATOR_PATH + "/tools"
      
      self.MACRO_ROOT           = home + "/Work/Code/tools/python/amacro"
      self.MACRO_ROOT_DEVICE    = "/data/local/macro"
      
      self.TEMP_PATH            = self.PROJECT_PATH + "/tmp"
      

      
      self.TESSERACT_FONTS_PATH = self.MACRO_ROOT + "/tesseract/fonts"
      self.TESSERACT_PATH       = self.MACRO_ROOT + "/tesseract/tesseract-ocr/build/bin"
      
      self.MACRO_SCRIPTS        = self.MACRO_ROOT + "/scripts"

      self.LOG_FILE             = self.MACRO_ROOT + "/macro.log"
      
      self.DEVICE_NAME          = "S6-Android6"
      
      self.USE_PYTHON_ADB       = False
