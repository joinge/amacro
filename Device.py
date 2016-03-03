'''
Created on Aug 28, 2013

@author: me
'''

import numpy as np
import pylab as pl
import time
from nothreads import myPopen
from printing import myPrint, printAction, printResult, printQueue
from nothreads import myRun
import cv2
import re
import sys
from PySide import QtCore
# from PySide import QProcess

import logging
logger = logging.getLogger(__name__)

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
   
   def __init__(self, settings, parent):
      super(Device, self).__init__(parent)
      
#       self.active_device_is_set.connect(self.takeScreenshot)
      
      self.process_gimp = QtCore.QProcess(self)
#       self.process.waitForStarted()
      
      self.active_device = None
      self.adb_active_device = None
      self.youwave = None
      
      self.settings = settings
      
      if settings.USE_PYTHON_ADB:
         self.adb_cmd = "python adb.zip"
         
      else:
         self.adb_cmd = settings.ANDROID_UTILS_PATH + "/adb"
         
         
      self.image_screen = None
         
      self.android_vm = None
      self.is_phone = None
      self.youwave = None
      self.eventTablet = None
      self.eventMouse = None
      self.event_keyboard = None
         
      self.device_mutex = QtCore.QMutex()
      self.adb_port = 5037
      
      #self.processes = []
      #self.post_processes = []
      
      class DoubleThread():
         def __int__(self):
            pass
      
      self.vm_process = QtCore.QProcess(self)
      self.vm_process.error.connect(self.checkIfValidExit)
      self.vm_process.finished.connect(self.checkIfValidExit)
      self.player_process = QtCore.QProcess(self)
      self.player_process.error.connect(self.checkIfValidExit)
      self.player_process.finished.connect(self.checkIfValidExit)

      
   #def __del__(self):
      #self.process.terminate()
      #self.process.waitForFinished()
      #self.thread.terminate()
      #self.thread.wait()
      
   def start(self):
      printAction("Starting VirtualBox...", newline=True)
      self.running = True
      self.vm_process.startDetached("VBoxManage startvm %s --type headless"%self.settings.DEVICE_NAME)
      time.sleep(10)
      
      printAction("Starting Player...", newline=True)
      self.player_process.startDetached("%s/player --vm-name %s --no-popup"%(self.settings.EMULATOR_PATH, self.settings.DEVICE_NAME))
      time.sleep(60)
      
   def stop(self):
      printAction("Stopping processes...", newline=True)
      self.running = False
      self.player_process.terminate()
      self.vm_process.terminate()
      self.player_process.waitForFinished()
      self.vm_process.waitForFinished()
#       timer = QtCore.QTimer()
#       timer.timeout.connect(self.player_process.kill)
#       timer.timeout.connect(self.vm_process.kill)
#       timer.start(5000)
#       time.sleep(6)
      
      cmds = ["sh -c \"killall %s/player\""%self.settings.EMULATOR_PATH,
              "sh -c \"killall %s/tools/adb\""%self.settings.EMULATOR_PATH,
              "sh -c \"ps -ef | grep VBox | awk '{print $2}' | xargs kill\""]
      for i in range(1):
         for cmd in cmds:
            killproc = QtCore.QProcess()
            try:
               killproc.startDetached(cmd)
               killproc.waitForFinished(5)
            except Exception as e:
               print("Failed to run command: %s"%cmd)
            killproc.terminate()
            killproc.waitForFinished()
#          time.sleep(5)

      
   def restart(self):
      self.stop()
      self.start()
      
   def checkIfValidExit(self):
      printAction("Process quitting. Checking if OK...")
      if self.running:
         printResult(False)
         raise Exception("VM related process quit unexpectedly")
         
      printResult(True)
      
      
#    def isHealthy(self):
#       
#       process = QtCore.QProcess()
#       process.start("sh -c \"ps -ef | grep %s/player2\""%self.settings.EMULATOR_PATH)
#       process.waitForFinished()
#       print process.exitStatus()
#       process.
#       return True
#    
   

#    @QtCore.Slot(str)
#    def getInfo(self,key):
#       
#       for i in range(2):
#          try:
#             return getattr(self,key)
#          except:
#             self.updateInfo()
#       
#       return None
#    
   @QtCore.Slot(str)
   def gimpScreenshot(self, filename=None):
   
      root_path = os.getcwd() 
      
#       if not filename:
#          
#       screenshot_tmp_path = '%s/%s'%(root_path, settings.TEMP_PATH)
#       screenshot_path = '%s/%s'%(root_path, settings.SCREEN_PATH)
#       if self.getInfo('screen_density') == 160:
#          screenshot_path = screenshot_path + '/dpi160'
#          
#       screenshot_tmp = screenshot_tmp_path + '/screenshot_%s.png'%self.active_device
#       screenshot_new = screenshot_path     + '/screeself.s.png'%self.active_device
#    
#       myPopen("cp %s %s" %(screenshot_tmp, screenshot_new))
      self.process_gimp.start("gimp", ["%s"%filename] )
#       myPopen("sleep 5; rm %s"%screenshot_new )
      
   
   @QtCore.Slot()
   def isAndroidVM(self):
      return self.android_vm
   
   @QtCore.Slot()
   def isYouwave(self):
      return self.youwave
   
   @QtCore.Slot()
   def isPhone(self):
      return self.is_phone
   
   def updateScreenOrientation(self):
      
      try:
         dumpsys_inputs = self.adbShell("dumpsys input")
         surface_orientation = re.search('SurfaceOrientation:\s*([0-9])', dumpsys_inputs)
         if surface_orientation:
            if surface_orientation.group(0) == "1":
               self.orientation = "landscape"
            else:
               self.orientation = "portrait"
      except:
         logger.error("ERROR: Unable to parse screen orientation")
         
   def updateScreenDensity(self):
      
      try:
#          try:
         self.screen_density = int(self.adbShell('getprop ro.sf.lcd_density'))
#          except:
#             dumpsys_display = self.adbShell("dumpsys display")
#             devno = re.search('Built-in\sScreen', dumpsys_display)
         
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
         
         
   def updateScreenResolution(self):
      
      dumpsys_log = self.adbShell("dumpsys window policy")
      screen_size = re.search('mUnrestrictedScreen=.+ ([0-9]+)x([0-9]+)', dumpsys_log)
      if screen_size:
         self.screen_width  = int(screen_size.group(1))
         self.screen_height = int(screen_size.group(2))
      

   @QtCore.Slot()
   def updateInfo(self):
      
      logger.info("Collecting info from the device...")

      # First we need to know if we are running an emulator.
      uname_machine = self.adbShell('uname -m')
      uname_all = self.adbShell('uname -a')
      
      # Copy some scripts to the device we will use later on
      self.adbShell('mkdir /sdcard/macro')
      self.adbPush('%s/device /sdcard/macro'%self.settings.MACRO_SCRIPTS, stdout='devnull')
      
      # Query on arch. But really, Android version would be better.
      self.youwave = False
      self.android_vm = False
      if re.search('arm',uname_machine):
         self.is_phone = True
      
      if re.search('i686',uname_machine):
         if re.search('qemu',uname_all) or re.search('genymotion',uname_all):
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
            
      if self.isAndroidVM() or self.isPhone():
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
         self.device_model = self.adbShell('getprop ro.product.model')
      except:
         printAction("ERROR: Unable to find device ID string")
         
         
      self.updateScreenOrientation()
         
      self.updateScreenDensity()
         
      self.updateScreenResolution()
      
         
      devno = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]([0-9]{1,2})\.[0-9]{1,3}.[0-9]{1,5}', self.active_device)
      if devno:
         self.deviceNo = int(devno.group(1))

      self.printInfo()
           
   @QtCore.Slot() 
   def printInfo(self):
      
      logger.info("")
      logger.info("Device info updated. New parameters:")
      if self.isYouwave():
         logger.info("   Device type:           YouWave emulator")
         logger.info("   Device - touchscreen: /dev/input/event%d"%self.eventTablet)
         logger.info("   Device - keyboard:    /dev/input/event%d"%self.event_keyboard)
         logger.info("   Device - mouse:       /dev/input/event%d"%self.eventMouse)
         
      if self.isAndroidVM():
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
      
      self.takeScreenshot()
      
      self.active_device_is_set.emit()
     
   #   Popen("adb %s adbShell echo 'echo %d > /sys/devices/platform/samsung-pd.2/s3cfb.0/spi_gpio.3/spi_master/spi3/spi3.0/backlight/panel/brightness' \| su" % (ADB_ACTIVE_DEVICE, percent), stdout=PIPE, adbShell=True).stdout.read()
   
   def killProcess(self, process, desc='', timeout=5):
      if process.state() == QtCore.QProcess.NotRunning:
         if process.exitStatus() != QtCore.QProcess.NormalExit:
            logger.error("ERROR: %s process died with error code %d"%(desc, process.exitStatus()))
      else:
         print("-----Killing %s process-----"%desc)
         process.kill()
         if not process.waitForFinished(timeout*1000):
            print ret1
            logger.error("ERROR: Unable to kill %s process!"%desc)

   @QtCore.Slot(str, dict)
   def adb(self, command, stdout=False, process=None, binary_output=False, timeout=5):
      
      has_parent = False
      if process:
         has_parent = True
      else:
         process = QtCore.QProcess(self)
         #self.processes.append(process)
      
#       if not process:

      if self.settings.USE_PYTHON_ADB:

         if re.search("devices", command):
            cmd = "%s %s" %(self.adb_cmd, command)
         
         else:
            
            # May seem odd but it allows piping in the shell
            cmd = ""
#             if os.name == "posix":
#                cmd = "\"sh -c "
               

            cmd = cmd + "%s %s" %(self.adb_cmd, command)

   
#             if os.name == "posix":
#                cmd = cmd + "\""
   #       print cmd


      else:
         cmd = ''
         if re.search("devices", command):
            cmd= "%s -P %d %s" %(self.adb_cmd, self.adb_port, command)
            
         else:
            if not self.adb_active_device:
               logger.error("You must set active device before using adb.")
               exit(1)
            
            # May seem odd but it allows piping in the shell
            if os.name == "posix":
               cmd = "sh -c \"%s -P %d %s %s\"" %(self.adb_cmd, self.adb_port, self.adb_active_device, command)
            else:
               cmd = "%s -P %d %s %s" %(self.adb_cmd, self.adb_port, self.adb_active_device, command)

#       print cmd
#
      # Make sure only one adb command is executed at a time
      self.device_mutex.lock()
      
      p1 = process.start(cmd)
      process.waitForStarted(timeout*1000)
      if not binary_output:
         logger.debug(p1)
      if not has_parent:
         process.waitForFinished(timeout*1000)

#       if not stdout:
#          logger.debug(cmd)

#       for i in range(5):
#          process.start(cmd)
#          
#          if not process.waitForFinished():
#             logger.warning("ADB timeout/crash. Command: %s"%cmd) 
#             process.kill()
#             logger.debug("Retry attempt %d/5"%i)
#          else:
#             break
         
         if binary_output:
            output = process.readAllStandardOutput()
         else:
            output = str(process.readAllStandardOutput())
            if output:
               if re.search('device not found', output):
                  logger.info("Adb lost connection to target.")
                  exit()
               if output != "" and stdout:
                  output = str(output)
                  logger.info(output)
            
         errors = process.readAllStandardError()
         if errors != "":
            logger.error(errors)
         
         self.killProcess(process, 'adb(): %s'%cmd, timeout=timeout)

         self.device_mutex.unlock()
         return output

      self.device_mutex.unlock()
      
      
   
   @QtCore.Slot(str, dict)
   def adbPipe(self, cmd1, cmd2, binary_output, timeout=5):
      
      # Creat processes owned by this class (to reduce zombie-process risk)
      process = QtCore.QProcess(self)
      post_process = QtCore.QProcess(self)
      #self.processes.append(process)
      #self.post_processes.append(post_process)
            
      process.setStandardOutputProcess(post_process)
      self.adb(cmd1, binary_output=binary_output, process=process)
      post_process.start(cmd2)
      
      post_process.setProcessChannelMode(QtCore.QProcess.ForwardedChannels)
      
      if not process.waitForStarted(timeout*1000):
         logger.error("ERROR: Command: %s failed to start."%cmd1) 
         self.killProcess(process, 'adbPipe()')
         self.killProcess(post_process, 'adbPipe() post')
         return False
   
      ret1 = post_process.waitForFinished(timeout*1000)
      ret2 = process.waitForFinished(timeout*1000)
      if not ret1:
         logger.error("ERROR: Command: %s timed out."%cmd1)
      if not ret2:
         logger.error("ERROR: Command: %s timed out."%cmd2)
      if not ret1 or not ret2:
         self.killProcess(process, 'adbPipe()')
         self.killProcess(post_process, 'adbPipe() post')
         #process.kill()
         #if not process.waitForFinished(-1):
            #logger.error("ERROR: Unable to kill adbPipe() process!") 
         #post_process.kill()
         #if not post_process.waitForFinished(-1):
            #logger.error("ERROR: Unable to kill adbPipe() process!") 
         #return False

#       self.process.waitForReadyRead()
#       output = QtCore.QByteArray()
#       retries = 0
#       while retries < 5:
#          retries = retries + 1
#          output = output + post_process.readAllStandardOutput()
#          
#          if post_process.waitForFinished(1):
#             break
#          
#       if retries == 4:
#          logger.warning("ADB timeout/crash. Command: %s"%cmd1) 
#          process.kill()
#          post_process.kill
#          return False
         
      if binary_output:
         output = post_process.readAllStandardOutput()
      else:
         output = str(post_process.readAllStandardOutput())
         if output:
            if re.search('device not found', output):
               logger.info("Adb lost connection to target.")
               exit()
            if output != "":
               output = str(output)
               logger.info(output)
##       ret1 = post_process.waitForFinished(5000)
      #ret2 = process.waitForFinished(-1)
      #if ret2:
      
      # Make sure the processes die, and block until they do.QProcess.NormalExit 	
      # Stray ADB processes are sure to eventually crash the program
      self.killProcess(post_process, 'adbPipe() post')
      self.killProcess(process, 'adbPipe()')
            
        
      return output
   

   @QtCore.Slot(str, dict)
   def adbShell(self, command, **kwargs):
      
      return self.adb("shell %s %s"%(self.adb_active_device, command), **kwargs)
              
              
   @QtCore.Slot(str, dict)
   def adbPush(self, command, **kwargs):
      
      return self.adb("push %s %s"%(self.adb_active_device, command), **kwargs)
   
   @QtCore.Slot(str, dict)
   def adbPull(self, command, **kwargs):
      
      return self.adb("pull %s %s"%(self.adb_active_device, command), **kwargs)
   
   
   @QtCore.Slot(str)
   def takeScreenshot(self, filename=None, ybounds=None, timeout=5):
   
      logger.debug("Pulling a fresh screenshot from the device...")
   #   Popen("adb adbShell /system/bin/screencap -p /sdcard/screenshot.png > error.log 2>&1;\
   #          adb pull  /sdcard/screenshot.png screenshot.png >error.log 2>&1", stdout=PIPE, adbShell=True).stdout.read()
             
   #   Popen("adb adbShell screencap -p | sed 's/\r$//' > screenshot.png", stdout=PIPE, adbShell=True).stdout.read()
   
   #   Popen("adb adbShell screencap | sed 's/\r$//' > img.raw;\
   #          dd bs=800 count=1920 if=img.raw of=img.tmp >/dev/null 2>&1;\
   #          ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i img.tmp screenshot.png >/dev/null 2>&1",
   #          stdout=PIPE, adbShell=True).stdout.read()
      if not ybounds:
         ybounds = [0, 1]
      #else:
         #print("   DEBUG: Height: %d   Width: %d   Orientation: %s"%(self.screen_height, self.screen_width, self.orientation))
         #if self.screen_height < self.screen_width:
            #print "   DEBUG: shell sh /sdcard/macro/screenshot %d %d %d"%(self.screen_height, ybounds[0]*self.screen_width, ybounds[1]*self.screen_width)
         #else:
            #print "   DEBUG: shell sh /sdcard/macro/screenshot %d %d %d"%(self.screen_width, ybounds[0]*self.screen_height, ybounds[1]*self.screen_height)
#       print ybounds
       
      if filename:
         output = filename
      else:
         output = "%s/screenshot_%s.png"%(self.settings.TEMP_PATH, self.active_device)
         
      ################
      # CURRENT BEST #
      ################
      
      method = 'partial_screen_stream'
      
      if method == 'partial_screen_stream':
   #      Popen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x640 -i img_%s1.raw screenshot_%s.png >/dev/null 2>&1"%(ACTIVE_DEVICE,ACTIVE_DEVICE), stdout=PIPE, adbShell=True).stdout.read()
#          if os.name == "posix":
         retries = 5
         for i in range(retries):
            try:
#                print("   Height: %d   Width: %d   Orientation: %s"%(self.screen_height, self.screen_width, self.orientation))
   
               if self.screen_height < self.screen_width:
                  process = self.adbPipe("shell sh /sdcard/macro/screenshot %d %d %d"%(self.screen_height, ybounds[0]*self.screen_width, ybounds[1]*self.screen_width), "gunzip -c", binary_output=True, timeout=timeout)
                  data = np.fromstring(process, dtype=np.uint8)
               
#                   print("   Reshaping data")
#                   print data.shape
#                   print (ybounds[1]*self.screen_width - ybounds[0]*self.screen_width, self.screen_height, 4)
                  im = data.reshape((int(round((ybounds[1]-ybounds[0])*self.screen_width)), self.screen_height, 4))
#                   print("   Transposing data")
                  im = im.transpose((1,0,2))
                  im = im[::-1,:,:]
                  
               else:
                  
                  process = self.adbPipe("shell sh /sdcard/macro/screenshot %d %d %d"%(self.screen_width, ybounds[0]*self.screen_height, ybounds[1]*self.screen_height), "gunzip -c", binary_output=True, timeout=timeout)
                  data = np.fromstring(process, dtype=np.uint8)
#                   print("   Reshaping data")
#                   print data.shape
#                   print (ybounds[1]*self.screen_height - ybounds[0]*self.screen_height, self.screen_width, 4)
                  im = data.reshape((int(round((ybounds[1]-ybounds[0])*self.screen_height)), self.screen_width, 4))
            
               
#                print("   Converting color")
               image = cv2.cvtColor(im, cv2.COLOR_BGRA2RGB)
               
               cv2.imwrite("screenshot.png", image)
               
   #                cv2.imshow('', image)
   #                cv2.waitKey()
   #                cv2.destroyAllWindows()
   #                cv2.imshow('', cv2.cvtColor(data.reshape((self.screen_height, ybounds[1]-ybounds[0], 4)), cv2.COLOR_BGRA2RGB)); cv2.waitKey()
               
               return image
            
            except Exception as e:
               print("ERROR: Screenshot failed. Tring to continue (attempt %d)..."%i)
               self.updateScreenOrientation()
               self.updateScreenResolution()
#                print data.shape
               print (ybounds[1]-ybounds[0], self.screen_height, 4)
               time.sleep(1)
 
               print e
   #             print("ERROR: Unable to lock device.")

          
   #   Popen("adb %s adbShell screencap | sed 's/\r$//' > img.raw"%ADB_ACTIVE_DEVICE, stdout=PIPE, adbShell=True).stdout.read()
      elif not self.isYouwave() and not self.isAndroidVM() and not self.isPhone():
         self.adb('"shell/system/bin/screencap /sdcard/img.raw;\
                    pull /sdcard/img.raw %s/img_%s.raw"'% (self.settings.TEMP_PATH, self.active_device))
             
         f = open(self.settings.TEMP_PATH+'/img_%s.raw' % self.active_device, 'rb')
         f1 = open(self.settings.TEMP_PATH+'/img_%s1.raw' % self.active_device, 'w')
         f.read(12) # ignore 3 first pixels (otherwise the image gets offset)
         rest = f.read() # read rest
         f1.write(rest)
               
         myPopen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i %s/img_%s1.raw %s"
               %(self.settings.TEMP_PATH,self.active_device,output))
         
         if self.screen_height > self.screen_width or self.orientation == "portrait":
            process = QtCore.QProcess()
            process.start("mogrify -rotate 270 %s"%output)
            process.waitForFinished(timeout*1000)
            process.terminate()
            process.waitForFinished(timeout*1000)
         
      else:
   #      Popen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x640 -i img_%s1.raw screenshot_%s.png >/dev/null 2>&1"%(ACTIVE_DEVICE,ACTIVE_DEVICE), stdout=PIPE, adbShell=True).stdout.read()
         if os.name == "posix":
            logger.debug(self.adbShell("/system/bin/screencap -p | sed 's/\\r$//' > %s"%output))
         elif os.name == "nt":
            logger.debug(self.adbShell("/system/bin/screencap -p /sdcard/screenshot.png", stdout='devnull', stderr='devnull', log=False))
            logger.debug(self.adb("pull /sdcard/screenshot.png %s" %output, stdout='devnull', stderr='devnull', log=False))
         else:
            logger.error("Unsupported OS")
            exit(1)
            
         if self.screen_height > self.screen_width or self.orientation == "portrait":
            process = QtCore.QProcess()
            process.start("mogrify -rotate 270 %s"%output)
            process.waitForFinished(timeout*1000)
            process.terminate()
            process.waitForFinished(timeout*1000)
            

               
#       self.screenshot_ready.emit(output)
         
         
      # New ways:
      # adb shell "screencap 2>/dev/null | (dd of=/dev/null bs=12 count=1 2>/dev/null; dd bs=$((4*1080)) count=1000 skip=200 2>/dev/null of=/sdcard/img.raw)"; adb pull /sdcard/img.raw
      # adb shell "screencap 2>/dev/null | (dd of=/dev/null bs=12 count=1 2>/dev/null; dd bs=$((4*1080)) count=1000 skip=200 2>/dev/null)" | perl -pe 's/\x0D\x0A/\x0A/g' > img.raw
      # adb shell "screencap 2>/dev/null | (dd of=/dev/null bs=12 count=1 2>/dev/null; dd bs=$((4*1080)) count=1000 skip=200 2>/dev/null)" | sed $'s/\\r$//' > img.raw
      # adb shell "busybox stty raw; screencap 2>/dev/null | (dd of=/dev/null bs=12 count=1920 2>/dev/null; dd bs=$((4*1080)) count=1000 skip=200 2>/dev/null)" > ing.raw
      
      # Best
      # adb shell "busybox stty raw; screencap 2>/dev/null | (dd of=/dev/null bs=12 count=1920 2>/dev/null; dd bs=$((4*1080)) count=1000 skip=200 2>/dev/null) | gzip -c" | gunzip -c > img.raw
         
      
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
      
      
   def adb_input(self, text):
      macro_output = self.adbShell('input text %s' %(text))

   def adb_event_batch(self, events):
      
      sendevent_string = ''
      for i, event in enumerate(events):
         if i != 0:
            sendevent_string += '; '
            
         sendevent_string += "sendevent /dev/input/event%d %d %d %d" % event
           
      self.adbShell('"%s"' % (sendevent_string))
         
   #   print( "adb adbShell %s"%sendevent_string )
         
   
   def adb_event(self, event_no=2, a=None, b=None , c=None):
      """Event number: 1 - hardware key (home?)
                       2 - touch
                           0003 2f - ABS_MT_SLOT           : value 0, min 0, max 9, fuzz 0, flat 0, resolution 0
                           0003 30 - ABS_MT_TOUCH_MAJOR    : value 0, min 0, max 255, fuzz 0, flat 0, resolution 0
                           0003 35 - ABS_MT_POSITION_X     : value 0, min 0, max 479, fuzz 0, flat 0, resolution 0
                           0003 36 - ABS_MT_POSITION_Y     : value 0, min 0, max 799, fuzz 0, flat 0, resolution 0
                           0003 39 - ABS_MT_TRACKING_ID    : value 0, min 0, max 65535, fuzz 0, flat 0, resolution 0
                           0003 3a - ABS_MT_PRESSURE       : value 0, min 0, max 30, fuzz 0, flat 0, resolution 0
      """
      
      macro_output = self.adbShell('sendevent /dev/input/event%d %d %d %d' % (event_no, a, b, c))
   #   time.sleep(0.5)  
      #adbSend("/dev/input/event2",3,48,10);
      
   def homeKey(self):
   
      if self.isYouwave():
         self.adb_event(1, 0x0001, 0x0066, 0x00000001)
         self.adb_event(1, 0x0000, 0x0000, 0x00000000)
         self.adb_event(1, 0x0001, 0x0066, 0x00000000)
         self.adb_event(1, 0x0000, 0x0000, 0x00000000)
      else:
         self.adbShell('input keyevent 4')
   
   def powerKey(self):
      
      if re.search("Xperia Z2", self.device_model):
         self.adb_event(1, 0x0001, 0x0074, 0x00000001)
         self.adb_event(1, 0x0000, 0x0000, 0x00000000)
         self.adb_event(1, 0x0001, 0x0074, 0x00000000)
         self.adb_event(1, 0x0000, 0x0000, 0x00000000)
         
# /dev/input/event1: 0001 0074 00000001
# /dev/input/event1: 0000 0000 00000000
# /dev/input/event1: 0001 0074 00000000
# /dev/input/event1: 0000 0000 00000000

         
      else:
         self.adb_event(1, 0x0001, 0x0074, 0x00000001)
         self.adb_event(1, 0x0000, 0x0000, 0x00000000)
         self.adb_event(1, 0x0001, 0x0074, 0x00000000)
         self.adb_event(1, 0x0000, 0x0000, 0x00000000)
         
      time.sleep(2)
      
      
   def backKey(self):
      
      device.adbShell('input keyevent 4')
      
   def back(self):
      event_no = 5
      
      self.adb_event_batch([
      (event_no, 0x0001, 0x009e, 0x00000001),
      (event_no, 0x0000, 0x0000, 0x00000000),
      (event_no, 0x0001, 0x009e, 0x00000000),
      (event_no, 0x0000, 0x0000, 0x00000000)
      ])
   #       time.sleep(0.2)
   
   def press(self, coords, seconds):
      self.swipe(coords, coords, seconds)
      
   def leftClick(self, loc):
       
#       global isYouwave()
   #   adb_event( 2, 0x0003, 0x0039, 0x00000d45 )
   #   adb_event( 2, 0x0003, 0x0035, loc[0] )
   #   adb_event( 2, 0x0003, 0x0036, loc[1] )
   #   adb_event( 2, 0x0003, 0x0030, 0x00000032 )
   #   adb_event( 2, 0x0003, 0x003a, 0x00000002 )
   #   adb_event( 2, 0x0000, 0x0000, 0x00000000 )
   #   adb_event( 2, 0x0003, 0x0039, 0xffffffff )
   #   adb_event( 2, 0x0000, 0x0000, 0x00000000 )
   
      # TODO: use input tap x y
      
      
      if not self.isYouwave():
         
         self.adbShell('input tap %d %d'%(loc[0],loc[1]))
         
   #      adb_event_batch([
   #         (2, 0x0003, 0x0039, 0x00000d45),
   #         (2, 0x0003, 0x0035, loc[0]),
   #         (2, 0x0003, 0x0036, loc[1]),
   #         (2, 0x0003, 0x0030, 0x00000032),
   #         (2, 0x0003, 0x003a, 0x00000002),
   #         (2, 0x0000, 0x0000, 0x00000000),
   #         (2, 0x0003, 0x0039, 0xffffffff),
   #         (2, 0x0000, 0x0000, 0x00000000)
   #         ])
      
      else:
         
         if self.eventTablet:
            event_no = self.eventTablet
         else:
            event_no = 3
                    
     
         self.adb_event_batch([
            (event_no, 0x0004, 0x0004, 0x00090001),
            (event_no, 0x0001, 0x0110, 0x00000001),
            (event_no, 0x0003, 0x0000, int(loc[0] * 2 ** 15 / 480.0)),
            (event_no, 0x0003, 0x0001, int(loc[1] * 2 ** 15 / 640.0)),
            (event_no, 0x0000, 0x0000, 0x00000000),
            (event_no, 0x0004, 0x0004, 0x00090001),
            (event_no, 0x0001, 0x0110, 0x00000000),
            (event_no, 0x0000, 0x0000, 0x00000000)
            ])
   #       time.sleep(0.2)
   
   def backspace(self):
      
   
      if self.isYouwave() or self.isAndroidVM():
         event_no = self.event_keyboard
         if not event_no:
            event_no = 2
         
         self. adb_event_batch([
            (event_no, 0x0004, 0x0004, 0x0000000e),
            (event_no, 0x0001, 0x000e, 0x00000001),
            (event_no, 0x0000, 0x0000, 0x00000000),
            (event_no, 0x0004, 0x0004, 0x0000000e),
            (event_no, 0x0001, 0x000e, 0x00000000),
            (event_no, 0x0000, 0x0000, 0x00000000)
            ])     
   
      else:
         myPrint("ERROR: backspace() is not implemented for regular phones")     
        
   def right_arrow(self):
   
      if self.isYouwave() or self.isAndroidVM():
         event_no = self.event_keyboard
         if not event_no:
            event_no = 2
         
         self.adb_event_batch([
            (event_no, 0x0004, 0x0004, 0x000000cd),
            (event_no, 0x0001, 0x006a, 0x00000001),
            (event_no, 0x0000, 0x0000, 0x00000000),
            (event_no, 0x0004, 0x0004, 0x000000cd),
            (event_no, 0x0001, 0x006a, 0x00000000),
            (event_no, 0x0000, 0x0000, 0x00000000)
            ])     
   
      else:
         myPrint("ERROR: right_arrow() is not implemented for regular phones")   
          
      
   def enterText(self, text):
      self.adb_input(text)
      
   def swipe(self, start, stop, seconds=None, repeats=1):

      if seconds:
         cmd = 'sh /sdcard/macro/swipe %d %d %d %d %d %d' % (repeats, start[0], start[1], stop[0], stop[1], seconds*1000)
      else:
         cmd = 'sh /sdcard/macro/swipe %d %d %d %d %d' % (repeats, start[0], start[1], stop[0], stop[1])
#       for i in range(repeats):
#          if seconds:
#             cmd = cmd + 'input swipe %d %d %d %d %d; ' % (start[0], start[1], stop[0], stop[1], seconds*1000)
#          else:
#             cmd = cmd + 'input swipe %d %d %d %d; ' % (start[0], start[1], stop[0], stop[1])
         
      if not self.isYouwave():
         if seconds:
            self.adbShell("%s" %cmd, timeout=repeats*seconds+5)
         else:
            self.adbShell("%s" %cmd, timeout=repeats*2)
#          print "%s" % cmd
      else:
         self.linear_swipe(start, stop, steps=5)
         
         
   def linear_swipe(self, start, stop, steps=1):
   
      if not self.isYouwave():
         xloc = np.linspace(start[0], stop[0], steps + 1)
         yloc = np.linspace(start[1], stop[1], steps + 1)
      
         
         self.adb_event(2, 0x0003, 0x0039, 0x00000eb0)
         self.adb_event(2, 0x0003, 0x0035, xloc[0])
         self.adb_event(2, 0x0003, 0x0036, yloc[0])
         self.adb_event(2, 0x0003, 0x0030, 0x00000053)
         self.adb_event(2, 0x0003, 0x003a, 0x00000005)
         self.adb_event(2, 0x0000, 0x0000, 0x00000000)
         
         for i in range(steps):
            self.adb_event(2, 0x0003, 0x0035, xloc[i + 1])
            self.adb_event(2, 0x0003, 0x0036, yloc[i + 1])
            self.adb_event(2, 0x0003, 0x0030, 0x00000042)
            self.adb_event(2, 0x0003, 0x003a, 0x00000005)
            self.adb_event(2, 0x0000, 0x0000, 0x00000000)
            
         self.adb_event(2, 0x0003, 0x0039, 0xffffffff)
         self.adb_event(2, 0x0000, 0x0000, 0x00000000)
      
      else:
         xloc = np.linspace(int(start[0] * 2 ** 15 / 480.0), int(stop[0] * 2 ** 15 / 480.0), steps + 1)
         yloc = np.linspace(int(start[1] * 2 ** 15 / 640.0), int(stop[1] * 2 ** 15 / 640.0), steps + 1)
   
         self.adb_event_batch([
            (3, 0x0004, 0x0004, 0x00090001),
            (3, 0x0001, 0x0110, 0x00000001),
            (3, 0x0000, 0x0000, 0x00000000),
            (3, 0x0003, 0x0000, xloc[0]),
            (3, 0x0003, 0x0001, yloc[0]),
            (3, 0x0000, 0x0000, 0x00000000)
            ])
         
         for i in range(steps):
            self.adb_event_batch([
               (3, 0x0003, 0x0000, xloc[i + 1]),
               (3, 0x0003, 0x0001, yloc[i + 1]),
               (3, 0x0000, 0x0000, 0x00000000)
               ])
   #         time.sleep(1.0/steps)
            
         self.adb_event_batch([         
            (3, 0x0004, 0x0004, 0x00090001),
            (3, 0x0001, 0x0110, 0x00000000),
            (3, 0x0000, 0x0000, 0x00000000)
            ])
   
   
   def scroll(self, dx, dy):
      
      if not self.isYouwave():
         self.adbShell('input trackball roll %d %d' % (dx, dy))
      else:
   #      xint = 200.0
         yint = 200.0
               
         numy = dy / yint
         for i in range(int(numy) + 1):
            if dy > 0:
               self.linear_swipe((5, 400), (5, 400 - yint), steps=5)
            else:
               self.linear_swipe((5, 200), (5, 200 + yint), steps=5)
               
   def unlock_phone(self):
      
      anything = self.locateTemplate("button_once.png",  offset='center', print_coeff=True, threshold=0.02)
      if not anything: 
         self.powerKey()
         time.sleep(1)
         self.homeKey()
         time.sleep(.5)
   #       self.linear_swipe((187, 616), (340, 616))
   
   
   def lock_phone(self):
      
      self.powerKey()

         
   def readImage(self, image_file, xbounds=None, ybounds=None):
      try:
         image = myRun(cv2.imread, image_file)
      except Exception, e:
         myPrint(e)
         myPrint("Unable to read image %"%image_file, msg_type='error')
         
      if not xbounds:
         if not ybounds:
            return image
         else:
            return image[ybounds[0]:ybounds[1], :]
      else:
         if not ybounds:
            return image[:, xbounds[0]:xbounds[1]].copy()
         else:
            return image[ybounds[0]:ybounds[1], xbounds[0]:xbounds[1]].copy()
         
         
   def swipeReference(self, template, destination=(0, 0), threshold=0.96, print_coeff=False, xbounds=None, ybounds=None, reuse_last_screenshot=False):
      
      ref = self.locateTemplate(template, threshold=threshold, retries=2, print_coeff=print_coeff, xbounds=xbounds, ybounds=ybounds, reuse_last_screenshot=reuse_last_screenshot)
      
      if not ref:
         printAction("Unable to navigate to swipe reference...", newline=True)
         return None
      
      if not xbounds:
         xbounds = (0, 480)
      if not ybounds:
         ybounds = (0, 800)
         
      diff = np.array(destination) - (ref + np.array([xbounds[0], ybounds[0]]))
      
      self.swipe(ref, map(int, ref + 0.613 * diff))
      time.sleep(.3)
      self.swipe(ref, map(int, ref + 0.613 * diff))
      time.sleep(.5)
      return ref
      
   def locateTemplateErrorHandler(self, retries=1):
      # See if the cause can be an Android error:

      image_error = self.locateTemplate("android_error.png", recursing=True, threshold=0.9, offset=(65,31), reuse_last_screenshot=True)
      
      if image_error:
         myPrint(' ')
         printAction("Android error detected and will (hopefully) be dealt with.", newline=True)
         self.leftClick(image_error)
         time.sleep(10) # In case we hit a "wait" button
         retries = retries + 1
      
      
   def locateTemplate(self, template, threshold=0.96, offset=(0,0), retries=1, interval=0, print_coeff=False, xbounds=None, ybounds=None, reuse_last_screenshot=False, timeout=15,
                   recursing=None, click=False, scroll_size=[], swipe_size=[], swipe_ref=['', (0, 0)]):

      DEBUG=False
      if not ybounds:
         ybounds = [0,1]
      
      for i in range(retries):
         if not reuse_last_screenshot:
            self.image_screen = self.takeScreenshot(ybounds=ybounds, timeout=timeout)
            
            cv2.imwrite( "../../../rk/screenshot.png", self.image_screen );
            
#             cv2.imshow('', self.image_screen)
#             cv2.waitKey()
#             cv2.destroyAllWindows()
         
         time.sleep(.1)
#          try:
         if not self.screen_density == 480:
#                img_path = self.settings.SCREEN_PATH
#             else:
            myPrint("ERROR: Screen density not supported. Aborting" % self.active_device)
            return False
               
      
#             image_screen = self.readImage(self.settings.TEMP_PATH+"/screenshot_%s.png" %self.active_device, xbounds, ybounds)
            
#             # This means the VM probably crashed
#             if image_screen == None:
#                raise Exception("ERROR: Unable to load image from disk. This shouldn't happen!")
               
   #         image_screen   = readImage("test.png", xbounds, ybounds)
#          except:
#             raise Exception("ERROR: Unable to load screenshot_%s.png. This is bad, and weird!!!" % self.active_device)
         
         result = np.array(0)
         match_found = False
         template = re.sub(r'-[0-9]*\.', '.', template)
         for j in range(5):
                     
            name, ext = os.path.splitext(template)
            if ext == '':
               ext = '.png'
            
            if self.isYouwave():
               template_youwave = name + "_youwave" + ext
               if os.path.exists(self.settings.SCREEN_PATH+'/'+template_youwave):
                  template = template_youwave
         
            if os.path.exists(self.settings.SCREEN_PATH+'/'+name+ext):
               image_template = myRun(cv2.imread, self.settings.SCREEN_PATH+'/'+name+ext)
   
               if DEBUG:
                  pl.imshow(image_template)
                  pl.show()
                  
               if offset == 'center':
                  image_size = np.array([image_template.shape[1],image_template.shape[0]])
                  offset = tuple((image_size/2.0).astype('int'))
                  
               try:
                  result = myRun(cv2.matchTemplate, self.image_screen, image_template, cv2.TM_CCOEFF_NORMED)
               except Exception, e:
                  print(e)
                  myPrint("Unable to match screenshot with template %s"%template)
                  raise Exception()
                  
               if result.max() > threshold:
                  match_found = True
                  break
            
            if j==0:
               template = re.sub(r'\.', '-%d.'%j, template)
            else:
               template = re.sub(r'-[0-9]*\.', '-%d.'%j, template)
            
   #       try:
   #          result = cv2.matchTemplate(image_screen, image_template, cv2.TM_CCOEFF_NORMED)
   #       except:
   #          myPrint("ERROR: Unable to match template \"%s\" with screenshot!!!" % template)
   #          return False
         
         if print_coeff:
            sys.stdout.write("%.2f " % result.max())
            sys.stdout.flush()
         else:
            sys.stdout.write('.')
            sys.stdout.flush()
         printQueue("%.2f " % result.max())
   #         print( " %.2f"%result.max(), end='' )
            
         if match_found:
            template_coords = np.unravel_index(result.argmax(), result.shape)
            template_coords = np.array([template_coords[1], template_coords[0]])
            
            if self.screen_height < self.screen_width:
               object_coords = tuple(template_coords + np.array(offset) + np.array([ybounds[0]*self.screen_width, 0]).astype('int'))
            else:
               object_coords = tuple(template_coords + np.array(offset) + np.array([ybounds[0]*self.screen_height, 0]).astype('int'))
            
            if click:
               self.leftClick(object_coords)
               time.sleep(3)
            if print_coeff:
               sys.stdout.write("(%d,%d) " % (object_coords[0], object_coords[1]))
               sys.stdout.flush()
            else:
               sys.stdout.write(' ')
               sys.stdout.flush()
            printQueue("(%d,%d) " % (object_coords[0], object_coords[1]))
   #         myPrint(" (%d,%d)"%(object_coords[0],object_coords[1]),end=' ')
            return object_coords
         
         else:
            # See if the cause can be an Android error:
            if recursing:
               return
            
            self.locateTemplateErrorHandler(self, retries=1)
            
   
         if retries > 1:
            if swipe_ref[0] != '':
               self.swipeReference(swipe_ref[0], destination=swipe_ref[1], reuse_last_screenshot=False)
            if swipe_size:
               self.swipe(swipe_size[0], swipe_size[1])
               if interval < 1:
                  time.sleep(1)
               else:
                  time.sleep(interval)
            if scroll_size:
               self.scroll(scroll_size[0], scroll_size[1])
               if interval < 1:
                  time.sleep(3)
            
            time.sleep(interval)
         
      return None


if __name__ == "__main__":
   
   from Settings import Settings
   settings = Settings()
   
   device = Device(settings)
   
   device.setActive('192.168.56.101:5555')

   device.takeScreenshot('screen.png')
   
