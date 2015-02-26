'''
Created on Aug 28, 2013

@author: me
'''

from nothreads import myPopen
from printing import myPrint, printResult
import re
from PySide import QtCore
# from PySide import QProcess

import logging
logger = logging.getLogger(__name__)

from Settings import Settings

import os
if os.name == "posix":
   ESC = "\\"
elif os.name == "nt":
   ESC = "^"
else:
   myPrint("WARNING: Unsupported OS")
   ESC = "\\"
   

class Device(QtCore.QObject):
   device_list = QtCore.Signal(list)
   active_device_is_set = QtCore.Signal()
   screenshot_ready = QtCore.Signal(str)
   
   def __init__(self, settings):
      super(Device, self).__init__()
      

      self.process = QtCore.QProcess(self)
      self.process_gimp = QtCore.QProcess(self)
#       self.process.waitForStarted()
      
      self.active_device = None
      self.adb_active_device = None
      self.youwave = None
      
      self.settings = settings
      
      self.adb_cmd = 'adb'
      
      if settings.ANDROID_UTILS_PATH:
         self.adb_cmd = settings.ANDROID_UTILS_PATH + "/adb"
         
      self.device_mutex = QtCore.QMutex()
      self.adb_port = 5037
      

      
   def __del__(self):
      self.process.terminate()
      self.process.waitForFinished()
      self.thread.terminate()
      self.thread.wait()

   @QtCore.Slot(str)
   def getInfo(self,key):
      
      for i in range(2):
         try:
            return getattr(self,key)
         except:
            self.updateInfo()
      
      return None
   
   @QtCore.Slot(str)
   def gimpScreenshot(self, filename=None):
   
      root_path = os.getcwd() 
      
#       if not filename:
#          
#       screenshot_tmp_path = '%s/%s'%(root_path, settings.TEMP_PATH)
#       screenshot_path = '%s/%s'%(root_path, settings.SCREEN_PATH)
#       if device.getInfo('screen_density') == 160:
#          screenshot_path = screenshot_path + '/dpi160'
#          
#       screenshot_tmp = screenshot_tmp_path + '/screenshot_%s.png'%device.active_device
#       screenshot_new = screenshot_path     + '/screenshot_%s.png'%device.active_device
#    
#       myPopen("cp %s %s" %(screenshot_tmp, screenshot_new))
      self.process_gimp.start("gimp", ["%s"%filename] )
#       myPopen("sleep 5; rm %s"%screenshot_new )
      
   
   @QtCore.Slot()
   def isAndroidVM(self):
      return self.getInfo('android_vm')
   
   @QtCore.Slot()
   def isYouwave(self):
      return self.getInfo('youwave')

   @QtCore.Slot()
   def updateInfo(self):
      
      logger.info("Collecting info from the device...")

      # First we need to know if we are running an emulator.
      uname_machine = self.adbShell('uname -m')
      uname_all = self.adbShell('uname -a')
      
      # Copy some scripts to the device we will use later on
      self.adbShell('mkdir /sdcard/macro')
      self.adb('push %s/device /sdcard/macro'%self.settings.MACRO_SCRIPTS, stderr='devnull', stdout='devnull')
      
      # Query on arch. But really, Android version would be better.
      self.youwave = False
      self.android_vm = False
      if re.search('i686',uname_machine):
         if re.search('qemu',uname_all):
            self.android_vm = True
         else:
            self.youwave = True
            
      event_devices = self.adbShell('sh /sdcard/macro/getevent')  
      
      if self.youwave:
         
#          thread = RunUntilTimeout(Popen,1,'adb %s adbShell getevent > tmp.txt' %ADB_ACTIVE_DEVICE, stdout=PIPE, adbShell=True)
#          thread.start()
#          thread.join()
#          time.sleep(2)
#          
#          event_devices = open('tmp.txt','r').read()
#          time.sleep(3)
#          event_devices = open('getevent.txt','r').read()#Popen('adb %s adbShell getevent > tmp.txt' %ADB_ACTIVE_DEVICE, stdout=PIPE, adbShell=True)
         try:
            self.eventTablet = int(re.search('/dev/input/event([0-9]).*\n.*VirtualBox USB Tablet',event_devices).group(1))
         except:
            myPrint("ERROR: Unable to parse input/output event touchscreen device")
         try:
            self.eventMouse = int(re.search('/dev/input/event([0-9]).*\n.*ImExPS/2 Generic Explorer Mouse',event_devices).group(1))
         except:
            myPrint("ERROR: Unable to parse input/output event mouse device")
         try:
            self.event_keyboard = int(re.search('/dev/input/event([0-9]).*\n.*AT Translated Set 2 keyboard',event_devices).group(1))
         except:
            myPrint("ERROR: Unable to parse input/output event keyboard device")
            
      if self.android_vm:
#         try:
#            self.eventTablet = int(re.search('/dev/input/event([0-9]).*\n.*VirtualBox USB Tablet',event_devices).group(1))
#         except:
#            myPrint("ERROR: Unable to parse input/output event touchscreen device")
#         try:
#            self.eventMouse = int(re.search('/dev/input/event([0-9]).*\n.*ImExPS/2 Generic Explorer Mouse',event_devices).group(1))
#         except:
#            myPrint("ERROR: Unable to parse input/output event mouse device")
         try:
            self.event_keyboard = int(re.search('/dev/input/event([0-9]).*\n.*AT Translated Set 2 keyboard',event_devices).group(1))
         except:
            myPrint("ERROR: Unable to parse input/output event keyboard device")
            
      try:
         self.screen_density = int(self.adbShell('getprop ro.sf.lcd_density'))
         
         # OLD METHOD:
#          build_prop = self.adb('adbShell echo "cat /system/build.prop" %s| su'%ESC)
#          try:
#             self.screen_density = int(re.search('[^#]ro\.sf\.lcd_density=([0-9]+)',build_prop).group(1))
#          except:
#             try:
#                if re.search('vbox86p',build_prop):
#                   self.screen_density = 160 # Not defined in Android VM
#             except:
#                self.screen_density = 160
#          
#          if self.screen_density != 160 and self.screen_density != 240:
#             
#             myPrint("")
#             myPrint("<<<WARNING>>> ")
#             myPrint("A screen density of %d detected. This is NOT SUPPORTED!!!"%self.screen_density)
#             myPrint("")
                        
      except:
         self.screen_density = 0
         logger.error("ERROR: Unable to parse screen density")
         
      dumpsys_log = self.adbShell("dumpsys")
      screen_size = re.search('mUnrestrictedScreen=.+ ([0-9]+)x([0-9]+)', dumpsys_log)
      if screen_size:
         self.screen_width  = int(screen_size.group(1))
         self.screen_height = int(screen_size.group(2))
      
         
      devno = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]([0-9]{1,2})\.[0-9]{1,3}.[0-9]{1,5}', self.active_device)
      if devno:
         self.deviceNo = int(devno.group(1))

      self.printInfo()
           
   @QtCore.Slot() 
   def printInfo(self):
      
      logger.info("")
      logger.info("Device info updated. New parameters:")
      if self.youwave:
         logger.info("   Device type:           YouWave emulator")
         logger.info("   Device - touchscreen: /dev/input/event%d"%self.eventTablet)
         logger.info("   Device - keyboard:    /dev/input/event%d"%self.event_keyboard)
         logger.info("   Device - mouse:       /dev/input/event%d"%self.eventMouse)
         
      if self.android_vm:
         logger.info("   Device type:          AndroVM/Genymotion emulator")
         logger.info("   Device - keyboard:    /dev/input/event%d"%self.event_keyboard)
         logger.info("   Screen:               %dx%d  (%d DPI)"%(self.screen_width, self.screen_height, self.screen_density))
      
      logger.info("")
         
   @QtCore.Slot()
   def adbConnect(self, device_name):
      
      logger.info("Connecting to: %s..."%device_name)
      
      output = self.adb("connect %s"%device_name)
   
      if not output or re.search("unable|error",output) or output == '':
         logger.error("Unable to connect to: %s"%device_name)
         return False
      else:
         self.setActiveDevice(device_name)
         return True
   
   @QtCore.Slot()
   def getDeviceList(self):
   
   #    devices_string = Popen("adb devices", stdout=PIPE, adbShell=True)
      
   #    time.sleep(3)
   #    re.search(r'[0-9]*', old_ids[0]).group(0)
   #    cards_in_roster_numbers = re.findall(r'\d+', cards_in_roster_string)
   #    cards_in_roster = tuple(map(int, cards_in_roster_numbers))
      
      #devices_string = Popen("adb devices | grep -w device | sed s/device//", stdout=PIPE, adbShell=True).stdout.read()
      
      devices_string = self.adb("devices")
      
      device_list1 = re.findall("\n[a-zA-Z0-9\.:]+",devices_string)
   
   #   devices = re.sub("\tdevice\r", '', devices[0])
   #   lines = re.split("\n+", devices)
      
      device_list = []
      for dev in device_list1:
         device_list.append(re.sub("\n", '', dev))
   #      if l != ''
   #         device_list.append(l)
            
      self.device_list.emit(device_list)
      return device_list
   
   @QtCore.Slot(str)
   def setActive(self, device_id):
            
      logger.info("Setting active device "+device_id)
      if device_id != None:
         windows_friendly_device = re.sub(r':','.',device_id)
         self.active_device = windows_friendly_device
         self.adb_active_device = "-s " + device_id
         
      self.updateInfo()
      
      self.active_device_is_set.emit()
     
   #   Popen("adb %s adbShell echo 'echo %d > /sys/devices/platform/samsung-pd.2/s3cfb.0/spi_gpio.3/spi_master/spi3/spi3.0/backlight/panel/brightness' \| su" % (ADB_ACTIVE_DEVICE, percent), stdout=PIPE, adbShell=True).stdout.read()

   @QtCore.Slot(str, dict)
   def adb(self, command, **kwargs):
      self.device_mutex.lock()
      
      if re.search("devices", command):
         self.process.start("%s -P %d %s" %(self.adb_cmd, self.adb_port, command))
         
      else:
         if not self.adb_active_device:
            logger.error("You must set active device before using adb.")
            exit(1)
         
         if os.name == "posix":
            self.process.start("sh %s -P %d %s %s" %(self.adb_cmd, self.adb_port, self.adb_active_device, command))
         else:
            self.process.start("%s -P %d %s %s" %(self.adb_cmd, self.adb_port, self.adb_active_device, command))

         
#       self.process.waitForReadyRead()
      self.process.waitForFinished()
      output = str(self.process.readAll())
      self.device_mutex.unlock()
      
      if output and re.search('device not found', output):
         logger.info("Adb lost connection to target.")
         exit()
         
      return output

   @QtCore.Slot(str, dict)
   def adbShell(self, command, **kwargs):
      
      return self.adb("shell %s"%command, **kwargs)
              
   @QtCore.Slot(str)
   def takeScreenshot(self, filename=None):
   
      logger.info("Pulling a fresh screenshot from the device...")
   #   Popen("adb adbShell /system/bin/screencap -p /sdcard/screenshot.png > error.log 2>&1;\
   #          adb pull  /sdcard/screenshot.png screenshot.png >error.log 2>&1", stdout=PIPE, adbShell=True).stdout.read()
             
   #   Popen("adb adbShell screencap -p | sed 's/\r$//' > screenshot.png", stdout=PIPE, adbShell=True).stdout.read()
   
   #   Popen("adb adbShell screencap | sed 's/\r$//' > img.raw;\
   #          dd bs=800 count=1920 if=img.raw of=img.tmp >/dev/null 2>&1;\
   #          ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i img.tmp screenshot.png >/dev/null 2>&1",
   #          stdout=PIPE, adbShell=True).stdout.read()
       
      if filename:
         output = filename
      else:
         output = "%s/screenshot_%s.png"%(self.settings.TEMP_PATH, self.active_device)
         
      ################
      # CURRENT BEST #
      ################
          
   #   Popen("adb %s adbShell screencap | sed 's/\r$//' > img.raw"%ADB_ACTIVE_DEVICE, stdout=PIPE, adbShell=True).stdout.read()
      if not self.isYouwave() and not self.isAndroidVM():
         self.adb('"shell/system/bin/screencap /sdcard/img.raw;\
                    pull /sdcard/img.raw %s/img_%s.raw"'% (self.settings.TEMP_PATH, self.active_device))
             
         f = open(self.settings.TEMP_PATH+'/img_%s.raw' % self.active_device, 'rb')
         f1 = open(self.settings.TEMP_PATH+'/img_%s1.raw' % self.active_device, 'w')
         f.read(12) # ignore 3 first pixels (otherwise the image gets offset)
         rest = f.read() # read rest
         f1.write(rest)
               
         myPopen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i %s/img_%s1.raw %s"
               %(self.settings.TEMP_PATH,self.active_device,output))
      else:
   #      Popen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x640 -i img_%s1.raw screenshot_%s.png >/dev/null 2>&1"%(ACTIVE_DEVICE,ACTIVE_DEVICE), stdout=PIPE, adbShell=True).stdout.read()
         if os.name == "posix":
            logger.debug(self.adbShell("/system/bin/screencap -p | sed 's/\r$//' > %s"%output))
         elif os.name == "nt":
            logger.debug(self.adbShell("/system/bin/screencap -p /sdcard/screenshot.png", stdout='devnull', stderr='devnull', log=False))
            logger.debug(self.adb("pull /sdcard/screenshot.png %s" %output, stdout='devnull', stderr='devnull', log=False))
         else:
            logger.error("Unsupported OS")
            exit(1)
               
      self.screenshot_ready.emit(output)
         
      
      # adb pull /dev/graphics/fb0 img.raw
      # dd bs=800 count=1920 if=img.raw of=img.tmp
      # ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt rgb32 -s 480x800 -i img.tmp image.png
      
      # time adb adbShell screencap -p /sdcard/img.tmp; adb pull /sdcard/img.tmp image2.png
      # adb adbShell "screencap -p | uuencode - > /sdcard/img2.tmp"; adb pull /sdcard/img2.tmp /dev/stdout | uudecode  > image3.png
      # adb adbShell screencap -p \| gzip -c \> /mnt/sdcard/s.png.gz; adb pull /mnt/sdcard/s.png.gz;
   #   adb adbShell screencap -p \| uuencode o | uudecode -o out.png
      
   #def take_screenshot_gtk():
   #   import gtk.gdk
   #   
   #   w = gtk.gdk.get_default_root_window()
   #   #sz = w.get_size()
   #   sz = (480,800+23)
   #   #print "The size of the window is %d x %d" % sz
   #   pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
   #   pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
   #   if (pb != None):
   #      pb.save(),"png")
   #      #print "Screenshot saved to screenshot.png."
   #   else:
   #      print( "Unable to get the screenshot." )
   
   
   @QtCore.Slot(int)
   def adjustBrightness(self, percent=10):
   
      self.adbShell('echo "echo %d > /sys/devices/platform/samsung-pd.2/s3cfb.0/spi_gpio.3/spi_master/spi3/spi3.0/backlight/panel/brightness" \| su' %percent)
      

if __name__ == "__main__":
   
   from Settings import Settings
   settings = Settings()
   
   device = Device(settings)
   
   device.setActive('192.168.100.10:5555')

   device.takeScreenshot('screen.png')
   