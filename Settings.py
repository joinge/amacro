
import os

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
