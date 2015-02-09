'''
Created on Aug 28, 2013

@author: me
'''

from nothreads import myPopen
from printing import myPrint, printResult
import re

class Device():
   def __init__(self):
      self.active_device = None
      self.adb_active_device = None
      self.youwave = None

   def getInfo(self,key):
      
      for i in range(2):
         try:
            return getattr(self,key)
         except:
            self.updateInfo()
      
      return None
   
   def isAndroidVM(self):
      return self.getInfo('android_vm')
   
   def isYouwave(self):
      return self.getInfo('youwave')
         
   def updateInfo(self):

      # First we need to know if we are running an emulator.
      uname_machine = myPopen('adb %s shell uname -m' %self.adb_active_device)
      uname_all = myPopen('adb %s shell uname -a' %self.adb_active_device)
      
      myPopen('adb %s shell mkdir /sdcard/macro'%self.adb_active_device)
      myPopen('adb %s push %s /sdcard/macro'%(self.adb_active_device, ANDROID_UTILS_PATH))
      
      # Query on arch. But really, Android version would be better.
      self.youwave = False
      self.android_vm = False
      if re.search('i686',uname_machine):
         if re.search('qemu',uname_all):
            self.android_vm = True
         else:
            self.youwave = True
            
      event_devices = myPopen('adb %s shell sh /sdcard/macro/getevent' %self.adb_active_device)  
      
      if self.youwave:
         
#          thread = RunUntilTimeout(Popen,1,'adb %s shell getevent > tmp.txt' %ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True)
#          thread.start()
#          thread.join()
#          time.sleep(2)
#          
#          event_devices = open('tmp.txt','r').read()
#          time.sleep(3)
#          event_devices = open('getevent.txt','r').read()#Popen('adb %s shell getevent > tmp.txt' %ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True)
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
         build_prop = myPopen('adb %s shell echo "cat /system/build.prop" %s| su'%(self.adb_active_device,ESC))
         try:
            self.screen_density = int(re.search('[^#]ro\.sf\.lcd_density=([0-9]+)',build_prop).group(1))
         except:
            try:
               if re.search('vbox86p',build_prop):
                  self.screen_density = 160 # Not defined in Android VM
            except:
               self.screen_density = 160
         
         if self.screen_density != 160 and self.screen_density != 240:
            
            myPrint("")
            myPrint("<<<WARNING>>> ")
            myPrint("A screen density of %d detected. This is NOT SUPPORTED!!!"%self.screen_density)
            myPrint("")
                        
      except:
         self.screen_density = 0
         myPrint("ERROR: Unable to parse screen density")
         
      devno = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]([0-9]{1,2})\.[0-9]{1,3}.[0-9]{1,5}', self.active_device)
      if devno:
         self.deviceNo = int(devno.group(1))
            
      self.printInfo()
            
   def printInfo(self):
      
      myPrint("")
      myPrint("Device info updated. New parameters:")
      if self.youwave:
         myPrint("Detected YouWave device")
         myPrint("  Device - touchscreen: /dev/input/event%d"%self.eventTablet)
         myPrint("  Device - keyboard:    /dev/input/event%d"%self.event_keyboard)
         myPrint("  Device - mouse:       /dev/input/event%d"%self.eventMouse)
      else:
         myPrint("youwave detected?       NO")
         
      if self.android_vm:
         myPrint("Detected AndroVM OS")      
      myPrint("Screen density:         %d"%self.screen_density)
      myPrint("")
         
   def adbConnect(self, device_name):
      
      myPrint("Connecting to: %s..."%device_name)
      
      output = myPopen("adb connect %s"%device_name)
   
      if not output or re.search("unable|error",output) or output == '':
         myPrint("ERROR: Unable to connect to: %s"%device_name)
         return False
      else:
         printResult(True)
         self.setActiveDevice(device_name)
         return True
   
   def adbDevices(self):
   
   #    devices_string = Popen("adb devices", stdout=PIPE, shell=True)
      
   #    time.sleep(3)
   #    re.search(r'[0-9]*', old_ids[0]).group(0)
   #    cards_in_roster_numbers = re.findall(r'\d+', cards_in_roster_string)
   #    cards_in_roster = tuple(map(int, cards_in_roster_numbers))
      
      #devices_string = Popen("adb devices | grep -w device | sed s/device//", stdout=PIPE, shell=True).stdout.read()
      devices_string = myPopen("adb devices")
      
      device_list1 = re.findall("\n[a-zA-Z0-9\.:]+",devices_string)
   
   #   devices = re.sub("\tdevice\r", '', devices[0])
   #   lines = re.split("\n+", devices)
      
      device_list = []
      for dev in device_list1:
         device_list.append(re.sub("\n", '', dev))
   #      if l != '':
   #         device_list.append(l)
            
      return device_list
   
   
   def setActive(self, device_id):
            
      if device_id != None:
         windows_friendly_device = re.sub(r':','.',device_id)
         self.active_device = windows_friendly_device
         self.adb_active_device = "-s " + device_id
         
      self.updateInfo()
     
   #   Popen("adb %s shell echo 'echo %d > /sys/devices/platform/samsung-pd.2/s3cfb.0/spi_gpio.3/spi_master/spi3/spi3.0/backlight/panel/brightness' \| su" % (ADB_ACTIVE_DEVICE, percent), stdout=PIPE, shell=True).stdout.read()

   def adb(self, command, **kwargs):
      
      myPopen("adb %s %s" %(self.adb_active_device, command), **kwargs)

   def shell(self, command, **kwargs):
      
      myPopen("adb %s shell %s" %(self.adb_active_device, command), **kwargs)
              
   def takeScreenshot(self, filename=None):
   
   #   Popen("adb shell /system/bin/screencap -p /sdcard/screenshot.png > error.log 2>&1;\
   #          adb pull  /sdcard/screenshot.png screenshot.png >error.log 2>&1", stdout=PIPE, shell=True).stdout.read()
             
   #   Popen("adb shell screencap -p | sed 's/\r$//' > screenshot.png", stdout=PIPE, shell=True).stdout.read()
   
   #   Popen("adb shell screencap | sed 's/\r$//' > img.raw;\
   #          dd bs=800 count=1920 if=img.raw of=img.tmp >/dev/null 2>&1;\
   #          ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i img.tmp screenshot.png >/dev/null 2>&1",
   #          stdout=PIPE, shell=True).stdout.read()
       
      if filename:
         output = filename
      else:
         output = "%s/screenshot_%s.png"%(TEMP_PATH, self.active_device)
         
      ################
      # CURRENT BEST #
      ################
          
   #   Popen("adb %s shell screencap | sed 's/\r$//' > img.raw"%ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
      if not self.isYouwave() and not self.isAndroidVM():
         self.adb('"shell /system/bin/screencap /sdcard/img.raw;\
                    pull /sdcard/img.raw %s/img_%s.raw"'% (TEMP_PATH, self.active_device))
             
         f = open(TEMP_PATH+'/img_%s.raw' % self.active_device, 'rb')
         f1 = open(TEMP_PATH+'/img_%s1.raw' % self.active_device, 'w')
         f.read(12) # ignore 3 first pixels (otherwise the image gets offset)
         rest = f.read() # read rest
         f1.write(rest)
               
         myPopen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i %s/img_%s1.raw %s"
               %(TEMP_PATH,self.active_device,output))
      else:
   #      Popen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x640 -i img_%s1.raw screenshot_%s.png >/dev/null 2>&1"%(ACTIVE_DEVICE,ACTIVE_DEVICE), stdout=PIPE, shell=True).stdout.read()
      
         cmd1 = 'adb %s shell /system/bin/screencap -p /sdcard/screenshot.png' % self.adb_active_device
         cmd2 = 'adb %s pull  /sdcard/screenshot.png "%s"' % (self.adb_active_device, output)
       
         myPopen(cmd1, stdout='devnull', stderr='devnull', log=False)
         myPopen(cmd2, stdout='devnull', stderr='devnull', log=False)
         
      
      # adb pull /dev/graphics/fb0 img.raw
      # dd bs=800 count=1920 if=img.raw of=img.tmp
      # ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt rgb32 -s 480x800 -i img.tmp image.png
      
      # time adb shell screencap -p /sdcard/img.tmp; adb pull /sdcard/img.tmp image2.png
      # adb shell "screencap -p | uuencode - > /sdcard/img2.tmp"; adb pull /sdcard/img2.tmp /dev/stdout | uudecode  > image3.png
      # adb shell screencap -p \| gzip -c \> /mnt/sdcard/s.png.gz; adb pull /mnt/sdcard/s.png.gz;
   #   adb shell screencap -p \| uuencode o | uudecode -o out.png
      
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
   
   
   def adjustBrightness(self, percent=10):
   
      self.shell('echo "echo %d > /sys/devices/platform/samsung-pd.2/s3cfb.0/spi_gpio.3/spi_master/spi3/spi3.0/backlight/panel/brightness" \| su' %percent)
      

   