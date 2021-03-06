'''
Created on Aug 28, 2013

@author: me
'''

import numpy as np
import pylab as pl
import time
from nothreads import myPopen
from printing import myPrint, printAction, printResult
from nothreads import myRun
import cv2
import re
import sys
from PySide import QtCore, QtGui
# from PySide import QProcess
# from multiprocessing import Queue
from Queue import Queue

import logging
# from antlr import Queue
logger = logging.getLogger(__name__)

import os
if os.name == "posix":
   ESC = "\\"
elif os.name == "nt":
   ESC = "^"
else:
   myPrint("WARNING: Unsupported OS")
   ESC = "\\"
   
# Don't like these global signals but they get the job done

class StartThread(QtCore.QThread):
   set_active = QtCore.Signal(str)
   def __init__(self, wait_condition, mutex_shared, queue, name,  settings, vm_process, player_process):
      super(StartThread, self).__init__(None)
      self.exiting = False
      
      self.waitCondition = wait_condition
      self.mutex_shared = mutex_shared
      self.queue = queue
      
      self.mutex_local = QtCore.QMutex()
      
      self.vm_process = vm_process
      self.player_process = player_process
      
      self.settings = settings
      
      self.name = name
      
   def run(self):
      
      self.mutex_local.lock()
      self.should_continue = True
      self.running = True
      self.mutex_local.unlock()
#       print "StartThread::run() - Waiting for mutex_shared to unlock..."
#       self.mutex_shared.lock()
#       self.timer.start(timeout)
      print "StartThread::run() - Performing work..."

#       time.sleep(6)

#       time.sleep(5)
      self.startDevice()
#       self.timer.stop()
#       self.success.emit()
      print "StartThread::run() - Telling Device that we're done..."
      self.waitCondition.wakeAll()
      
#       print "StartThread::run() - Releasing mutex_shared..."      
#       self.mutex_shared.unlock()
      
   def startDevice(self):

      printAction("Starting VirtualBox...", newline=True)
      
      self.ip = None
      
      self.vm_process.startDetached("VBoxManage startvm %s --type headless"%self.name)
      self.vm_process.waitForStarted()
      time.sleep(15)
      
      printAction("Starting Player...", newline=True)
      self.player_process.startDetached("%s/player --vm-name %s --no-popup"%(self.settings.EMULATOR_PATH, self.name))
      self.player_process.waitForStarted()
      time.sleep(5)
           
      if self.settings.USE_PYTHON_ADB:
         cmds = ["sh -c \"killall adb\""]*5
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
      
      if self.settings.USE_PYTHON_ADB:
         self.stopAdb()
      
      TIMEOUT=5
      i=0
      while i<TIMEOUT and self.should_continue:
         i=i+1
         has_slept=False
         printAction("Checking if system is online (%d/%d)..."%(i,TIMEOUT))
         try:
            ip = self.getIP(self.name)
            if not ip:
               raise Exception()
            time.sleep(5)
            has_slept=True
            break

         except Exception as e:
            print e 
            printResult(False)
            if not has_slept:
               time.sleep(5)
         
      if i<TIMEOUT-1:
         self.ip = str(ip)
         self.queue.put(self.ip)
         self.mutex_local.lock()
         self.running = False
         self.mutex_local.unlock()
      
         return
            
               
   def getIP(self, name):
      proc = QtCore.QProcess()
      
      try:
         proc.start("VBoxManage guestproperty enumerate %s"%name)
         proc.waitForStarted(1e4)
         proc.waitForFinished(5e4)
         dev_prop = proc.readAllStandardOutput()
      except Exception as e:
         print("Failed to run command: VBoxManage guestproperty enumerate %s"%name)
         
      ip_reg = re.search("androvm_ip_management, value: ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", dev_prop)
      
      if ip_reg:
         return ip_reg.group(1)
      
   def stop(self):
      sys.stdout.write("StartThread::run() - Waiting for thread to stop... ")
      self.mutex_local.lock()
      if not self.running:
         self.mutex_local.unlock()
         return
      
      self.should_continue = False
      self.mutex_local.unlock()
      
      for i in range(15):
         self.mutex_local.lock()
         if self.running:
            time.sleep(1)
         else:
            print("")
            return
         self.mutex_local.unlock()
         sys.stdout.write("%d "%(i+1))
      print("")
         

class Device(QtCore.QObject):
   device_list = QtCore.Signal(list)
   active_device_is_set = QtCore.Signal()
   screenshot_ready = QtCore.Signal(str)
   
   def __init__(self, settings, parent):
      super(Device, self).__init__(parent)
      
#       self.active_device_is_set.connect(self.takeScreenshot)
      self.app = QtGui.QApplication(sys.argv)
      
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
      self.ip = None
      self.current_player = None

      self.device_starter = None
      self.wait_condition = QtCore.QWaitCondition()
      self.mutex_shared = QtCore.QMutex()
      self.queue = Queue()
      self.screen_host_coords = None      
      
      #self.processes = []
      #self.post_processes = []
      
      class DoubleThread():
         def __int__(self):
            pass
      
      self.device_orientation = 'portrait' # fits most phones
      
      self.vm_name = ''
      
      self.vm_process = QtCore.QProcess(self)
      self.vm_process.error.connect(self.checkIfValidExit)
      self.vm_process.finished.connect(self.checkIfValidExit)
      self.recorder_process = QtCore.QProcess(self)
      self.avconv_process = QtCore.QProcess(self)
      self.player_process = QtCore.QProcess(self)
      self.player_process.error.connect(self.checkIfValidExit)
      self.player_process.finished.connect(self.checkIfValidExit)

      
   #def __del__(self):
      #self.process.terminate()
      #self.process.waitForFinished()
      #self.thread.terminate()
      #self.thread.wait()
      
   def start(self, name):
      self.current_player = name
      
      TIMEOUT=5
      for i in range(TIMEOUT):
         print "Device::start() - Starting a new thread..."         
         self.device_starter = StartThread(self.wait_condition, self.mutex_shared, self.queue, name, self.settings, self.vm_process, self.player_process)
         self.device_starter.set_active.connect(self.setActive)
         
         print "Device::start() - Locking mutex_shared..."
         self.mutex_shared.lock()
         
         try:
            for i in range(2):
               self.queue.get(block=False)
         except: pass
            
         print "Device::start() - Starting StartThread..."
         self.device_starter.start()
   
         print "Device::start() - Waiting for StartThread to complete (or time out)..."
         if self.wait_condition.wait(self.mutex_shared, 60*1000):
            print "Device::start() - Good news! StartThread signaled completion!"
            self.mutex_shared.unlock()
            
            self.ip = self.queue.get()
            
            self.setActive(self.ip+":5555")
            if self.locateTemplate("android_messaging_icon.png", threshold=0.9, print_coeff=True, timeout=5):
               printResult(True)
               time.sleep(3)
               return True
         else:
            print "Device::start() - Bad news! StartThread timed out!"
            self.mutex_shared.unlock()
            self.stop()
            print ""
         
      return False
      
      
   def stop(self):
      printAction("Stopping processes...", newline=True)
      if self.device_starter:
         self.device_starter.stop()
      self.player_process.terminate()
      self.vm_process.terminate()
      self.player_process.waitForFinished()
      self.vm_process.waitForFinished()
      
#       timer = QtCore.QTimer()
#       timer.timeout.connect(self.player_process.kill)
#       timer.timeout.connect(self.vm_process.kill)
#       timer.start(5000)
#       time.sleep(6)
      cmds = []
      if self.current_player:
         cmds.append("sh -c \"ps -ef | grep player | grep %s | awk '{print $2}' | xargs kill\""%self.current_player)
         cmds.append("sh -c \"ps -ef | grep VBox   | grep %s | awk '{print $2}' | xargs kill\""%self.current_player)
         
      if self.ip:
         cmds.append("sh -c \"ps -ef | grep adb    | grep %s | awk '{print $2}' | xargs kill\""%self.ip)
         cmds.append("sh -c \"ps -ef | grep VBox   | grep %s | awk '{print $2}' | xargs kill\""%self.ip)

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


               
   def stopAdb(self):
      printAction("Stopping ADB...", newline=True)
      
      cmds = ["sh -c \"killall adb\""]*3
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

      
   def restart(self, vm_name=''):
      if self.vm_name == '' and vm_name=='':
         print "ERROR: Device.restart(): VM has never been started before and no name given."
         exit(1) 
      self.stop()
      if vm_name=='':
         self.start(self.vm_name)
      else:
         self.start(vm_name)
         self.vm_name = vm_name
      
      
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
         
   def updateScreenInfo(self):
      self.updateScreenOrientation()
         
      self.updateScreenDensity()
         
      self.updateScreenResolution()
      
   def updateScreenshotMethod(self):
      pixmap = QtGui.QPixmap.grabWindow(self.app.desktop().winId(), 1920,0,1920,1080)
      
      print "WARNING: Device.updateScreenshotMethod() isn't implemented yet"

   @QtCore.Slot()
   def updateInfo(self):
      
      logger.info("Collecting info from the device...")

      # First we need to know if we are running an emulator.
      uname_machine = self.adbShell('uname -m')
      uname_all = self.adbShell('uname -a')
      
      self.arch = None
      
      # Query on arch. But really, Android version would be better.
      self.youwave = False
      self.android_vm = False
      if re.search('arm',uname_machine):
         self.is_phone = True
         self.arch = "arm"
      
      if re.search('i686',uname_machine):
         self.arch = "i686"
         if re.search('qemu',uname_all) or re.search('genymotion',uname_all):
            self.android_vm = True
         else:
            self.youwave = True
            
      # Copy some scripts to the device we will use later on      
      self.adbShell('mkdir %s'%self.settings.MACRO_ROOT_DEVICE)
      self.adbPush('%s/device %s'%(self.settings.MACRO_SCRIPTS, self.settings.MACRO_ROOT_DEVICE), stdout='devnull')
      self.adbPush('%s/ndk/libs/armeabi/decimate %s/decimate_arm'%(self.settings.MACRO_ROOT, self.settings.MACRO_ROOT_DEVICE), stdout='devnull')
      self.adbPush('%s/ndk/libs/x86/decimate %s/decimate_i686'%(self.settings.MACRO_ROOT, self.settings.MACRO_ROOT_DEVICE), stdout='devnull')
      
      event_devices = self.adbShell('%s/getevent'%self.settings.MACRO_ROOT_DEVICE)  
      
      try:
         self.genymotion_virtual_input = int(re.search('/dev/input/event([0-9]).*\n.*Genymotion Virtual Input',event_devices).group(1))
      except:
         pass
      
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
      
      self.updateScreenshotMethod()
      
         
      devno = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]([0-9]{1,2})\.[0-9]{1,3}.[0-9]{1,5}', self.active_device)
      if devno:
         self.deviceNo = int(devno.group(1))

      self.printInfo()
           
   @QtCore.Slot() 
   def printInfo(self):
      
      try:
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
      except Exception as e:
         print e
      
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
      
      image_device = self.takeScreenshot()
      
      QtGui.QPixmap.grabWindow(self.app.desktop().winId()).save(self.settings.TEMP_PATH+'/screenshot_desktop.png', 'png')
      image_desktop = cv2.imread(self.settings.TEMP_PATH+'/screenshot_desktop.png')
      
      result = cv2.matchTemplate(image_desktop, image_device, cv2.TM_CCOEFF_NORMED)

      if result.max() > 0.8:
         coords = np.unravel_index(result.argmax(), result.shape)
         coords = np.array([coords[1], coords[0]])
         
         self.screen_host_coords = coords
         
      else:
         print("WARNING: Unable to match desktop image with device image.")
      
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
               cmd = "sh -c \"%s %s %s\"" %(self.adb_cmd, self.adb_active_device, command)
            else:
               cmd = "%s %s %s" %(self.adb_cmd, self.adb_active_device, command)

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
   def adbShellPipe(self, cmd1, cmd2, **kwargs):
      if self.settings.USE_PYTHON_ADB:
         return self.adbPipe("shell %s %s"%(self.adb_active_device, cmd1), cmd2, **kwargs)
      else:
         return self.adbPipe("shell %s"%(cmd1), cmd2, **kwargs)
   
   @QtCore.Slot(str, dict)
   def adbPipe(self, cmd1, cmd2, binary_output=False, timeout=5):
      
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
      
      if self.settings.USE_PYTHON_ADB:
         return self.adb("shell %s %s"%(self.adb_active_device, command), **kwargs)
      else:
         return self.adb("shell %s"%(command), **kwargs)
              
              
   @QtCore.Slot(str, dict)
   def adbPush(self, command, **kwargs):
      
      if self.settings.USE_PYTHON_ADB:
         return self.adb("push %s %s"%(self.adb_active_device, command), **kwargs)
      else:
         return self.adb("push %s"%(command), **kwargs)
      
   
   @QtCore.Slot(str, dict)
   def adbPull(self, command, **kwargs):
      
      if self.settings.USE_PYTHON_ADB:
         return self.adb("pull %s %s"%(self.adb_active_device, command), **kwargs)
      else:
         return self.adb("pull %s"%(command), **kwargs)
   
   
   @QtCore.Slot(str)
   def takeScreenshot(self, filename=None, xbounds=None, ybounds=None, decimation=1, timeout=5, load_from_file=None):
   
      if load_from_file:
         self.image_screen = cv2.imread( load_from_file );
         return self.image_screen     
         
      logger.debug("Pulling a fresh screenshot from the device...")
   #   Popen("adb adbShell /system/bin/screencap -p /sdcard/screenshot.png > error.log 2>&1;\
   #          adb pull  /sdcard/screenshot.png screenshot.png >error.log 2>&1", stdout=PIPE, adbShell=True).stdout.read()
             
   #   Popen("adb adbShell screencap -p | sed 's/\r$//' > screenshot.png", stdout=PIPE, adbShell=True).stdout.read()
   
   #   Popen("adb adbShell screencap | sed 's/\r$//' > img.raw;\
   #          dd bs=800 count=1920 if=img.raw of=img.tmp >/dev/null 2>&1;\
   #          ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i img.tmp screenshot.png >/dev/null 2>&1",
   #          stdout=PIPE, adbShell=True).stdout.read()
      if not xbounds:
         xbounds = [0, 1]
         
      if not ybounds:
         ybounds = [0, 1]
      #else:
         #print("   DEBUG: Height: %d   Width: %d   Orientation: %s"%(self.screen_height, self.screen_width, self.orientation))
         #if self.screen_height < self.screen_width:
            #print "   DEBUG: shell sh /sdcard/macro/screenshot %d %d %d"%(self.screen_height, xbounds[0]*self.screen_width, xbounds[1]*self.screen_width)
         #else:
            #print "   DEBUG: shell sh /sdcard/macro/screenshot %d %d %d"%(self.screen_width, xbounds[0]*self.screen_height, xbounds[1]*self.screen_height)
#       print xbounds
       
      if filename:
         output = filename
      else:
         output = "%s/screenshot_%s.png"%(self.settings.TEMP_PATH, self.active_device)
         
      ################
      # CURRENT BEST #
      ################
      
      self.Ndec = 1920*1080 / (self.screen_width*self.screen_height)
      
      method = 'partial_screen_stream'
      
      if method == 'partial_screen_stream':
   #      Popen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x640 -i img_%s1.raw screenshot_%s.png >/dev/null 2>&1"%(ACTIVE_DEVICE,ACTIVE_DEVICE), stdout=PIPE, adbShell=True).stdout.read()
#          if os.name == "posix":
         retries = 5
         for i in range(retries):
            try:
   
               if self.screen_height < self.screen_width:
                  
                  if self.device_orientation == 'portrait':
#                   process = self.adbShellPipe("sh %s/screenshot_ref %d %d %d %d"%(self.settings.MACRO_ROOT_DEVICE, self.screen_height, xbounds[0]*self.screen_width, xbounds[1]*self.screen_width, decimation), "gunzip -c", binary_output=True, timeout=timeout)
                     process = self.adbShellPipe("sh %s/screenshot_ref %d %d %d"%(self.settings.MACRO_ROOT_DEVICE, self.screen_height, xbounds[0]*self.screen_width, xbounds[1]*self.screen_width), "gunzip -c", binary_output=True, timeout=timeout)
                  else:
                     process = self.adbShellPipe("sh %s/screenshot_ref %d %d %d"%(self.settings.MACRO_ROOT_DEVICE, self.screen_width, ybounds[0]*self.screen_height, ybounds[1]*self.screen_height), "gunzip -c", binary_output=True, timeout=timeout)
                  
                  data_sample = np.fromstring(process, dtype=np.uint8)
               
#                   print("   Reshaping data_sample")
#                   print data_sample.shape
#                   print (xbounds[1]*self.screen_width - xbounds[0]*self.screen_width, self.screen_height, 4)
                  if self.device_orientation == 'portrait':
                     im = data_sample.reshape((int(round((xbounds[1]-xbounds[0])*self.screen_width)), self.screen_height, 4))
                     im = im.transpose((1,0,2))
                     im = im[::-1,:,:]
                  else:
                     im = data_sample.reshape((int(round((ybounds[1]-ybounds[0])*self.screen_height)), self.screen_width, 4))
#                   print("   Transposing data_sample")

                  
               else:

                  process = self.adbShellPipe("sh %s/screenshot_ref %d %d %d"%(self.settings.MACRO_ROOT_DEVICE, self.screen_width, xbounds[0]*self.screen_height, xbounds[1]*self.screen_height), "gunzip -c", binary_output=True, timeout=timeout)
#                   process = self.adbShellPipe("sh %s/screenshot_ref %d %d %d"%(self.settings.MACRO_ROOT_DEVICE, self.screen_width, xbounds[0]*self.screen_height, xbounds[1]*self.screen_height), "gunzip -c", binary_output=True, timeout=timeout)
                  data_sample = np.fromstring(process, dtype=np.uint8)
#                   print("   Reshaping data_sample")
#                   print data_sample.shape
#                   print (xbounds[1]*self.screen_height - xbounds[0]*self.screen_height, self.screen_width, 4)
                  im = data_sample.reshape((int(round((xbounds[1]-xbounds[0])*self.screen_height)), self.screen_width, 4))
            
               
#                print("   Converting color")
               image = cv2.cvtColor(im, cv2.COLOR_BGRA2RGB)
               
               cv2.imwrite(self.settings.TEMP_PATH+"/screenshot.png", image)
               
#                cv2.imwrite(self.settings.TEMP_PATH+"/screenshot.png", cv2.cvtColor(data_sample.reshape((int(round((ybounds[1]-ybounds[0])*self.screen_width)), self.screen_height, 4)), cv2.COLOR_BGRA2RGB))
#                cv2.imwrite(self.settings.TEMP_PATH+"/screenshot.png", cv2.cvtColor(data_sample.reshape((self.screen_height, int(round((ybounds[1]-ybounds[0])*self.screen_width)), 4)), cv2.COLOR_BGRA2RGB))
               
   #                cv2.imshow('', image)
   #                cv2.waitKey()
   #                cv2.destroyAllWindows()
   #                cv2.imshow('', cv2.cvtColor(data_sample.reshape((self.screen_height, xbounds[1]-xbounds[0], 4)), cv2.COLOR_BGRA2RGB)); cv2.waitKey()
               
               return image
            
            except Exception as e:
               print("ERROR: Screenshot failed. Tring to continue (attempt %d)..."%i)
               if i>1:
                  print("   Before - Height: %d   Width: %d   Orientation: %s"%(self.screen_height, self.screen_width, self.orientation))
                  self.updateScreenOrientation()
                  self.updateScreenResolution()
                  print("   After  - Height: %d   Width: %d   Orientation: %s"%(self.screen_height, self.screen_width, self.orientation))

#                print data_sample.shape
               print (xbounds[1]-xbounds[0], self.screen_height, 4)
#                time.sleep(1)
 
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
      
   def zoom(self, direction='out', amount=0.5):
      
      # Right click and hold
#       self.adb_event(5, 0x0001, 0x014a, 0x00000001)
#       self.adb_event(5, 0x0003, 0x003a, 0x00000001)
#       self.adb_event(5, 0x0003, 0x0035, 0x0000010e) # Y coordinate
#       self.adb_event(5, 0x0003, 0x0036, 0x0000015f) # X coordinate
#       self.adb_event(5, 0x0000, 0x0002, 0x00000000)
#       self.adb_event(5, 0x0003, 0x0035, 0x0000010e)
#       self.adb_event(5, 0x0003, 0x0036, 0x0000026d)
#       self.adb_event(5, 0x0000, 0x0002, 0x00000000)
#       self.adb_event(5, 0x0000, 0x0000, 0x00000000)

#       if self.screen_height > self.screen_width:
      vpos = int(self.screen_height/2)
      if direction=='out':
         hpos = (np.array([0.45-0.15*amount, 0.55+0.15*amount, 0.45, 0.55])*self.screen_width).astype('int') # [(start),(end)]
      else:
         hpos = (np.array([0.45, 0.55, 0.45-0.15*amount, 0.55+0.15*amount])*self.screen_width).astype('int') # [(start),(end)]

#       else:
#          vpos = self.screen_width/2
#          if direction=='in':
#             hpos = (np.array([0.1, 0.9, 0.45, 0.55])*self.screen_height*amount).astype('int') # [(start),(end)]
#          else:
#             hpos = (np.array([0.45, 0.55, 0.1, 0.9])*self.screen_height*amount).astype('int') # [(start),(end)]
      print hpos
      print self.genymotion_virtual_input
      
      ms = self.genymotion_virtual_input
      self.adb_event(ms, 0x0001, 0x014a, 0x00000001)
      self.adb_event(ms, 0x0003, 0x003a, 0x00000001)
      
      self.adb_event(ms, 0x0003, 0x0035, vpos)
      self.adb_event(ms, 0x0003, 0x0036, hpos[0])
      self.adb_event(ms, 0x0000, 0x0002, 0x00000000)
      
      self.adb_event(ms, 0x0003, 0x0035, vpos)
      self.adb_event(ms, 0x0003, 0x0036, hpos[1])
      self.adb_event(ms, 0x0000, 0x0002, 0x00000000)
      self.adb_event(ms, 0x0000, 0x0000, 0x00000000)
      

      self.adb_event(ms, 0x0003, 0x0035, vpos)
      self.adb_event(ms, 0x0003, 0x0036, hpos[2])
      self.adb_event(ms, 0x0000, 0x0002, 0x00000000)
      self.adb_event(ms, 0x0003, 0x0035, vpos)
      self.adb_event(ms, 0x0003, 0x0036, hpos[3])
      self.adb_event(ms, 0x0000, 0x0002, 0x00000000)
      self.adb_event(ms, 0x0000, 0x0000, 0x00000000)
      
      self.adb_event(ms, 0x0001, 0x014a, 0x00000000)
      self.adb_event(ms, 0x0003, 0x003a, 0x00000000)
      self.adb_event(ms, 0x0000, 0x0002, 0x00000000)
      self.adb_event(ms, 0x0000, 0x0000, 0x00000000)
      
      
      
      
      
#       if re.search("Xperia Z2", self.device_model):
#          self.adb_event(1, 0x0001, 0x0074, 0x00000001)
         
      time.sleep(2)
      
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
      
      # This only works on new Android builds
#       self.swipe(coords, coords, seconds)

#       if self.screen_height > self.screen_width:
#       vpos = int(self.screen_height*coords[0])
#       hpos = int(self.screen_width*coords[1])
      hpos = int(coords[0])
      if self.screen_height > self.screen_width:
         vpos = int(self.screen_width-coords[1])
      else:
         vpos = int(self.screen_height-coords[1])

      ms = self.genymotion_virtual_input
      self.adb_event(ms, 0x0001, 0x014a, 0x00000001)
      self.adb_event(ms, 0x0003, 0x003a, 0x00000001)
      
      self.adb_event(ms, 0x0003, 0x0035, vpos)
      self.adb_event(ms, 0x0003, 0x0036, hpos)
      self.adb_event(ms, 0x0000, 0x0002, 0x00000000)
      self.adb_event(ms, 0x0000, 0x0000, 0x00000000)

      time.sleep(seconds)

      self.adb_event(ms, 0x0001, 0x014a, 0x00000000)
      self.adb_event(ms, 0x0003, 0x003a, 0x00000000)

      self.adb_event(ms, 0x0003, 0x0035, vpos)
      self.adb_event(ms, 0x0003, 0x0036, hpos)
      self.adb_event(ms, 0x0000, 0x0002, 0x00000000)
      self.adb_event(ms, 0x0000, 0x0000, 0x00000000)
      
      
      
# /dev/input/event5: 0001 014a 00000001
# /dev/input/event5: 0003 003a 00000001
# /dev/input/event5: 0003 0035 0000002b
# /dev/input/event5: 0003 0036 00000087
# /dev/input/event5: 0000 0002 00000000
# /dev/input/event5: 0000 0000 00000000
# /dev/input/event5: 0001 014a 00000000
# /dev/input/event5: 0003 003a 00000000
# /dev/input/event5: 0003 0035 0000002b
# /dev/input/event5: 0003 0036 00000087
# /dev/input/event5: 0000 0002 00000000
# /dev/input/event5: 0000 0000 00000000

      
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
      
   def rel2abs(self, rel_coord):
      """Transforms from relative coordinates to image coordinates:
         
           (0,0) _________x_______  (1,0)
                 |                |
                 |                |
               y |                |
                 |                |
           (0,1) |________________| (1,1)
      """
      
#       if self.screen_height > self.screen_width:
#          try:
#             coord = rel_coord
#             coord[:,0] = coord[:,0]*self.screen_height
#             coord[:,1] = coord[:,1]*self.screen_width
#             return coord.astype('int')
#          except:
#             return (int(self.screen_height*rel_coord[0]), int(self.screen_width*rel_coord[1]))
#       else:
      try:
         coord = rel_coord
         coord[:,0] = coord[:,0]*self.screen_width
         coord[:,1] = coord[:,1]*self.screen_height
         return coord.astype('int')
      except:
         return (int(self.screen_width*rel_coord[0]), int(self.screen_height*rel_coord[1]))
      
   def swipeRelative(self, start, stop, seconds=None, repeats=1):
      
      start_abs = self.rel2abs(start)
      stop_abs  = self.rel2abs(stop)
      
      print "swipe((%d,%d), (%d,%d))"%(start_abs[0], start_abs[1], stop_abs[0], stop_abs[1])
      self.swipe(start_abs, stop_abs, seconds=seconds, repeats=repeats)
      
   def swipe(self, start, stop, seconds=None, repeats=1):

      if seconds:
         cmd = '%s/swipe %d %d %d %d %d %d' % (self.settings.MACRO_ROOT_DEVICE, repeats, start[0], start[1], stop[0], stop[1], seconds*1000)
      else:
         cmd = '%s/swipe %d %d %d %d %d' % (self.settings.MACRO_ROOT_DEVICE, repeats, start[0], start[1], stop[0], stop[1])
         
#       if seconds:
#          cmd = 'sh /sdcard/macro/swipe %d %d %d %d %d' % (repeats, start[0], start[1], stop[0], stop[1])
#       else:
#          cmd = 'sh /sdcard/macro/swipe %d %d %d %d %d' % (repeats, start[0], start[1], stop[0], stop[1])
         
         
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

         
   def readImage(self, image_file, xbounds=None, ybounds_old=None):
      try:
         image = myRun(cv2.imread, image_file)
      except Exception, e:
         myPrint(e)
         myPrint("Unable to read image %"%image_file, msg_type='error')
         
      if not xbounds:
         if not ybounds_old:
            return image
         else:
            return image[ybounds_old[0]:ybounds_old[1], :]
      else:
         if not ybounds_old:
            return image[:, xbounds[0]:xbounds[1]].copy()
         else:
            return image[ybounds_old[0]:ybounds_old[1], xbounds[0]:xbounds[1]].copy()
         
         
   def swipeReference(self, template, destination=(0, 0), threshold=0.96, print_coeff=False, xbounds=None, ybounds_old=None, reuse_last_screenshot=False):
      
      ref = self.locateTemplate(template, threshold=threshold, retries=2, print_coeff=print_coeff, ybounds=xbounds, xbounds=ybounds_old, reuse_last_screenshot=reuse_last_screenshot)
      
      if not ref:
         printAction("Unable to navigate to swipe reference...", newline=True)
         return None
      
      if not xbounds:
         xbounds = (0, 480)
      if not ybounds_old:
         ybounds_old = (0, 800)
         
      diff = np.array(destination) - (ref + np.array([xbounds[0], ybounds_old[0]]))
      
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
      
      
   def locateTemplate(self, template, threshold=0.96, offset=(0,0), retries=1, interval=0, print_coeff=False, xbounds=None, ybounds=None,
                   reuse_last_screenshot=False, timeout=15, decimation=1, return_all_matches=False,
                   recursing=None, click=False, scroll_size=[], swipe_size=[], swipe_ref=['', (0, 0)]):

      DEBUG=False
      if not ybounds:
         ybounds = [0,1]
         
      if not xbounds:
         xbounds = [0,1]
      xbounds_abs = self.rel2abs((xbounds[0],0))[0], self.rel2abs((xbounds[1],0))[0]
      ybounds_abs = self.rel2abs((0,ybounds[0]))[1], self.rel2abs((0,ybounds[1]))[1]
              
      for i in range(retries):
         if not reuse_last_screenshot:
            
            if self.device_orientation == 'portrait':
               self.image_screen = self.takeScreenshot(xbounds=xbounds, timeout=timeout, decimation=decimation)
               self.image_screen = self.image_screen[int(ybounds_abs[0]):int(ybounds_abs[1])]
            else:
               self.image_screen = self.takeScreenshot(ybounds=ybounds, timeout=timeout, decimation=decimation)
               self.image_screen = self.image_screen[:,int(xbounds_abs[0]):int(xbounds_abs[1])]
            
            
            cv2.imwrite( self.settings.TEMP_PATH+"/screenshot.png", self.image_screen )
            
#             cv2.imshow('', self.image_screen)
#             cv2.waitKey()
#             cv2.destroyAllWindows()
         
         time.sleep(.1)
#          try:
#          if not self.screen_density == 480:
# #                img_path = self.settings.SCREEN_PATH
# #             else:
#             myPrint("ERROR: Screen density not supported. Aborting" % self.active_device)
#             return False
               
      
#             image_screen = self.readImage(self.settings.TEMP_PATH+"/screenshot_%s.png" %self.active_device, xbounds, ybounds)
            
#             # This means the VM probably crashed
#             if image_screen == None:
#                raise Exception("ERROR: Unable to load image from disk. This shouldn't happen!")
               
   #         image_screen   = readImage("test_img_raw.png", xbounds, ybounds)
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
                  cv2.imwrite("%s/template.png"%self.settings.TEMP_PATH, image_template[::decimation,::decimation,:])
                  result = myRun(cv2.matchTemplate, self.image_screen, image_template[::decimation,::decimation,:], cv2.TM_CCOEFF_NORMED)
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
#          printQueue("%.2f " % result.max())
   #         print( " %.2f"%result.max(), end='' )
            
         if match_found:
            template_coords = np.unravel_index(result.argmax(), result.shape)
            template_coords = np.array([template_coords[1], template_coords[0]])
            
            if return_all_matches:
               pass
            
            if self.screen_height < self.screen_width:
               object_coords = tuple(template_coords + np.array(offset) + np.array([xbounds[0]*self.screen_width, ybounds[0]*self.screen_height]).astype('int'))
            else:
               object_coords = tuple(template_coords + np.array(offset) + np.array([xbounds[0]*self.screen_height, ybounds[0]*self.screen_width]).astype('int'))
            
            if click:
               self.leftClick(object_coords)
               time.sleep(3)
            if print_coeff:
               sys.stdout.write("(%d,%d) " % (object_coords[0], object_coords[1]))
               sys.stdout.flush()
            else:
               sys.stdout.write(' ')
               sys.stdout.flush()
#             printQueue("(%d,%d) " % (object_coords[0], object_coords[1]))
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
   
   
   def record(self, end_template, timeout=180):
      
      cmds = ["sh -c \"killall avconv\"", "sh -c \"killall avconv\""]
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
      
      try:
         os.remove("%s/screen_record.mkv"%self.settings.TEMP_PATH)
      except: pass
      
      self.recorder_process.start("python %s/recordscreen.py -n -p %dx%d -s %dx%d %s/screen_record.mkv"%(self.settings.MACRO_ROOT, self.screen_host_coords[0], self.screen_host_coords[1],
                                                                                                self.screen_width, self.screen_height, self.settings.TEMP_PATH))
      self.recorder_process.waitForStarted()
      end_command = QtCore.QByteArray("q\n")
      for i in range(120):
         sys.stdout.write("%s "%i)
         replay_end = self.locateTemplate(end_template, offset='center', threshold=0.8, print_coeff=True)
         if replay_end:
            self.recorder_process.write(end_command)
            time.sleep(2)
            self.recorder_process.terminate()
            self.recorder_process.waitForFinished(2000)
            self.killProcess(self.recorder_process, "recordscreen.py", 5)
            break
         else:
            time.sleep(2)
            
      cmds = ["sh -c \"killall avconv\"", "sh -c \"killall avconv\""]
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
            
      try:
         os.remove("%s/screen_record_compressed.mp4"%self.settings.TEMP_PATH)
      except: pass
      
#       self.avconv_process.start("avconv -i %s/screen_record.mkv -vcodec libx264 -r 30 -pre libx264-slower -an -threads 0 %s/screen_record_compressed.mkv"%\
#                  (self.settings.TEMP_PATH, self.settings.TEMP_PATH))
      self.avconv_process.start("ffmpeg -i %s/screen_record.mkv -codec:v libx264 -crf 21 -bf 2 -flags +cgop -pix_fmt yuv420p -codec:a aac -strict -2 -b:a 384k -r:a 48000 -movflags faststart %s/screen_record_compressed.mp4"%\
                 (self.settings.TEMP_PATH, self.settings.TEMP_PATH))
            
      
      self.avconv_process.waitForStarted()
      self.avconv_process.waitForFinished(180*1000)
      self.avconv_process.terminate()
      self.avconv_process.waitForFinished(5000)
      self.killProcess(self.avconv_process, "avconv", 5)
      
      cmds = ["sh -c \"killall avconv\"", "sh -c \"killall avconv\""]
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
      
   #    proc.kill()
   #    proc2.kill()
      
      return "%s/screen_record_compressed.mp4"%self.settings.TEMP_PATH


if __name__ == "__main__":
   
   from Settings import Settings
   settings = Settings()
   
   device = Device(settings)
   
   device.setActive('192.168.56.102:5555')

   device.takeScreenshot('screen.png')
   
