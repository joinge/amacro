
class Settings:
   def __init__(self):
      self.PROJECT_PATH         = "/home/me/Work/Code/rk"
      self.SCREEN_PATH          = self.PROJECT_PATH + "/screens"
      
      self.ANDROID_SDK_PATH     = "/home/me/Apps/android-sdk-linux"
      
      self.EMULATOR_PATH        = "/home/me/Apps/Genymotion/genymotion"
      
      self.ANDROID_UTILS_PATH   = self.EMULATOR_PATH + "/tools"
      
      self.MACRO_ROOT           = "/home/me/Work/Code/tools/python/amacro"
      
      self.TEMP_PATH            = self.PROJECT_PATH + "/tmp"
      

      
      self.TESSERACT_FONTS_PATH = self.MACRO_ROOT + "/tesseract/fonts"
      self.TESSERACT_PATH       = self.MACRO_ROOT + "/tesseract/tesseract-ocr/build/bin"
      
      self.MACRO_SCRIPTS        = self.MACRO_ROOT + "/scripts"

      self.LOG_FILE             = self.MACRO_ROOT + "/macro.log"
      
      self.DEVICE_NAME          = "S6-Android6"
      
      self.USE_PYTHON_ADB       = True