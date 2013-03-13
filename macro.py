#cnee --record --events-to-record -1 --mouse --keyboard -o /tmp/xnee.xns -e /tmp/xnee.log -v

#cnee --record --seconds-to-record 150 --mouse --keyboard -o joinge.xns -e joinge.log -v


from __future__ import print_function
from random import uniform
from subprocess import Popen, PIPE
import numpy as np
import re, time, os, sys, ast, select
import cv2


# Bootlist:
#
# Valhalla25, airman54, nashie88, waygrumpy, xzitrempire(35), xQueenJenniecx, choiiflames, jonathanxxx, 
#
#

accounts = {'JoInge'  :'Mdt9oFSV',
            'JollyMa' :'Mdt9oFSV',
            'JoJanR'  :'Mdt9oFSV',
            'l33tdump':'dumpl33t',
            'Rolfy86' :'acura1986',
            'kinemb86':'kinemb86',
            'MonaBB86':'bb86mona'}


def10 = ['trcoba3', 'trcoba4', 'jabronii', 'Athena2317', 'Lyn3tte', 'Y0liis', 'goma7777', 'Jumpymcspasm', 'Solvicious',
         'Fragment08', 'Hirkyflobble', 'deathsxwill', 'Drimdal', 'erictt 55',
         'Deepblue4550', 'Primo911', 'Monito5',
         'Bigpapi11239899', 'Shanefearn', 'Badbadhorse', 'Quachrtq', 
         'Gibsupsup1', 'cintax33', 'jclen11', 'lemi28']

timeout = 90 # minutes
ip      = "10.0.0.15"

PAD = 60
all_common_cards = ['common_spiderwoman','common_sandman','common_enchantress','common_mockingbird','common_thing','common_beast','common_vulture','common_bullseye']

class Stats:
   def __init__(self):
      self.info = {}
      self.read()
      
   def setReference(self, key, val):

      self.info[key+"_ref"] = val
      
   def clearReference(self, key):
      
      self.info[key+"_ref"] = 0
      
   def getReference(self, key):
      
      if key+"_ref" in self.info:
         return self.info[key+"_ref"]
      else:
         return None
      
   def add(self, key, val):
      
      try:
         relative_val = val - self.info[key+"_ref"]
      except:
         relative_val = val
           
      if key in self.info:
         self.info[key] = self.info[key] + relative_val
      else:
         self.info[key] = relative_val
                  
      self.write()
      
      
   def read(self):
      
      try:
         s = open('stats.txt','r')
         if os.path.getsize('stats.txt') > 0:
            self.info = ast.literal_eval(s.read())
            s.close()
      except:
         pass
      
#      if os.path.getsize('stats.txt') > 0:
#         s = open('stats.txt','a')
          
   
   def write(self):
      s = open('stats.txt','w')
      s.write(str(self.info))
      s.close()
      
   def silverStart(self, key):

      ref = self.getReference(key+'_silver')
      if not ref:
         info = getMyPageStatus()
         try:
            silver_start = info['silver']
            self.setReference(key+'_silver', silver_start)
         except:
            printAction("WARNING: Unable to read silver status for statistics...", newline=True)
      
   def silverEnd(self, key):
      
      info = getMyPageStatus()
      
      try:
         silver_end = info['silver']
         self.add(key+'_silver', silver_end )
         self.clearReference(key+'_silver')       
         self.write()

      except:
         printAction("WARNING: Unable to read silver status for statistics...", newline=True)
 

# IMEI = 358150 04 524460 6
# 35     - British Approvals Board of Telecommunications (all phones)
# 
# 524460 - Serial number
# 6      - Check digit

def getIMEI():
   output = Popen("adb shell dumpsys iphonesubinfo | grep Device | sed s/\".*= \"//", stdout=PIPE, shell=True).stdout.read()
   print( output )
   return int(output)
#   358150045244606

def sumDigits(number,nsum=0):
   
   if number < 10:
      return nsum + number
   else:
      return nsum + sumDigits( number/10, number%10 )
   
def sumIMEIDigits(number,nsum=0,even=True):
   """http://en.wikipedia.org/wiki/IMEI#Check_digit_computation"""
   if number < 10:
      return nsum + number
   else:
      if even:
         return nsum + sumIMEIDigits( number/10, number%10, not even )
      else:
         return nsum + sumIMEIDigits( number/10, sumDigits((number%10)*2), not even )

#def printResult(res):
#   if res:
#      print(":)")
#   else:
#      print(":s")
#
#def printAction(str,res=None,newline=False):
#   string = "   %s"%str
#   if newline:
#      print(string.ljust(PAD,' '))
#   else:
#      print(string.ljust(PAD,' '),end='')
#   
#   if res:
#      printResult(res)

def notify():
   
#   Popen("mplayer audio/ringtones/BentleyDubs.ogg >/dev/null 2>&1", stdout=PIPE, shell=True).stdout.read()
   
   Popen("adb shell echo 'echo 100 > /sys/devices/virtual/timed_output/vibrator/enable' \| su", stdout=PIPE, shell=True).stdout.read()
   time.sleep(.2)
   Popen("adb shell echo 'echo 100 > /sys/devices/virtual/timed_output/vibrator/enable' \| su", stdout=PIPE, shell=True).stdout.read()
   time.sleep(.2)
   Popen("adb shell echo 'echo 100 > /sys/devices/virtual/timed_output/vibrator/enable' \| su", stdout=PIPE, shell=True).stdout.read()
   time.sleep(.2)
   Popen("adb shell echo 'echo 100 > /sys/devices/virtual/timed_output/vibrator/enable' \| su", stdout=PIPE, shell=True).stdout.read()

def printResult(res):
   if res:
      sys.stdout.write(":)")
   else:
      sys.stdout.write(":s")
      
   sys.stdout.flush()
   sys.stdout.write("\n")

def printAction(str,res=None,newline=False):
   string = "   %s"%str
   if newline:
      sys.stdout.write(string.ljust(PAD,' '))
      sys.stdout.flush()
      sys.stdout.write("\n")
   else:
      sys.stdout.write(string.ljust(PAD,' '))
      sys.stdout.flush()
   if res:
      printResult(res)
      
def printNotify(message, timeout=30):
   print("NOTIFICATION: "+message)
   notify()
   print("Type Enter to continue (will do so anyways in 30s)")
   
   select.select( [sys.stdin], [], [], timeout )
#   i, o, e = 
   
#   if (i):
#     print "You said", sys.stdin.readline().strip()
#   else:
#     print "You said nothing!"
   

#    stdout.write("\r%d" % i)
#    stdout.flush()
    
#                  s   s/min min/hr hr/day days/yr
#time_multiplier = [1,  60,   60,    24,    365]

#for r in range(15*60/imap_timeout-4):


#def record_macro(cmd):
#   macro_output = Popen("cnee --stop-key 0 --record --mouse --keyboard -o rec/%s.xns -e rec/%s.log -v"%(cmd,cmd), stdout=PIPE, shell=True).stdout.read()
#   #if macro_output == None:
#      #raise Exception("Unable to record macro: %s"%cmd)
#
#def replay_macro(cmd, replay_offset=(0,0)):
#   #macro_output = Popen("cnee --replay -f rec/%s.xns -v -e rec/%s.log --synchronised-replay"%(cmd,cmd), stdout=PIPE, shell=True).stdout.read()
#   macro_output = Popen("cnee --replay -f rec/%s.xns -v -e rec/%s.log -ns -ro %d,%d --stop-key 0 2>error.log"\
#                        %(cmd,cmd,replay_offset[0],replay_offset[1]), stdout=PIPE, shell=True).stdout.read()
#                        

#######
# ADB #
#######

def connect_adb_wifi():
   
   if Popen("adb devices | grep %s"%ip, stdout=PIPE, shell=True).returncode == None:
      macro_output = Popen("adb connect %s"%ip, stdout=PIPE, shell=True).stdout.read()
      if macro_output == None:
         return False
      else:
         return True
   else:
      return True
   #if macro_output == None:
   #   raise Exception("Unable to connect adb to wifi")  
   
      
def clear_marvel_cache():
   printAction("Clearing Marvel cache...", newline=True)
   macro_output = Popen("adb shell pm clear com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android", stdout=PIPE, shell=True).stdout.read()
   time.sleep(5)

   #if macro_output == None:
   #   raise Exception("Unable to clear Marvel cache")

def launch_marvel():
   macro_output = Popen("adb shell am start -n com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android/.SplashActivity", stdout=PIPE, shell=True).stdout.read()
   #if macro_output == None:
   #   raise Exception("Unable to start Marvel")

#def adb_shell(strings):
#
#   for string in strings:
      

def adb_input(text):
   macro_output = Popen("adb shell input text %s"%(text), stdout=PIPE, shell=True).stdout.read()

def adb_event_batch(events):
   
   sendevent_string = ''
   for i,event in enumerate(events):
      if i != 0:
         sendevent_string += '; '
         
      sendevent_string += "sendevent /dev/input/event%d %d %d %d"%event
        
   Popen("adb shell \"%s\""%sendevent_string, stdout=PIPE, shell=True).stdout.read()
      
#   print( "adb shell %s"%sendevent_string )
      

def adb_event(event_no=2, a=None, b=None ,c=None):
   """Event number: 1 - hardware key (home?)
                    2 - touch
                        0003 2f - ABS_MT_SLOT           : value 0, min 0, max 9, fuzz 0, flat 0, resolution 0
                        0003 30 - ABS_MT_TOUCH_MAJOR    : value 0, min 0, max 255, fuzz 0, flat 0, resolution 0
                        0003 35 - ABS_MT_POSITION_X     : value 0, min 0, max 479, fuzz 0, flat 0, resolution 0
                        0003 36 - ABS_MT_POSITION_Y     : value 0, min 0, max 799, fuzz 0, flat 0, resolution 0
                        0003 39 - ABS_MT_TRACKING_ID    : value 0, min 0, max 65535, fuzz 0, flat 0, resolution 0
                        0003 3a - ABS_MT_PRESSURE       : value 0, min 0, max 30, fuzz 0, flat 0, resolution 0
   """
   
   macro_output = Popen("adb shell sendevent /dev/input/event%d %d %d %d"%(event_no,a,b,c), stdout=PIPE, shell=True).stdout.read()
#   time.sleep(0.5)  
   #adbSend("/dev/input/event2",3,48,10);
   
def left_click(loc):
   
#   adb_event( 2, 0x0003, 0x0039, 0x00000d45 )
#   adb_event( 2, 0x0003, 0x0035, loc[0] )
#   adb_event( 2, 0x0003, 0x0036, loc[1] )
#   adb_event( 2, 0x0003, 0x0030, 0x00000032 )
#   adb_event( 2, 0x0003, 0x003a, 0x00000002 )
#   adb_event( 2, 0x0000, 0x0000, 0x00000000 )
#   adb_event( 2, 0x0003, 0x0039, 0xffffffff )
#   adb_event( 2, 0x0000, 0x0000, 0x00000000 )

   # TODO: use input tap x y
   
   adb_event_batch( [
      ( 2, 0x0003, 0x0039, 0x00000d45 ),
      ( 2, 0x0003, 0x0035, loc[0]     ),
      ( 2, 0x0003, 0x0036, loc[1]     ),
      ( 2, 0x0003, 0x0030, 0x00000032 ),
      ( 2, 0x0003, 0x003a, 0x00000002 ),
      ( 2, 0x0000, 0x0000, 0x00000000 ),
      ( 2, 0x0003, 0x0039, 0xffffffff ),
      ( 2, 0x0000, 0x0000, 0x00000000 )
      ] )
   
   
def enter_text( text ):
   adb_input( text )
  

def adb_login(login_screen_coords, user):
   
   c = np.array(login_screen_coords)
   
   left_click(( 205, 254 )+c) # Login Mobage
   left_click(( 106, 255 )+c) # Login button
   left_click((  76, 108 )+c) # Mobage name field
   enter_text( user )
   left_click((  76, 174 )+c) # Mobage password field
   enter_text( accounts[user] )
   left_click(( 313, 237 )+c) # Login button
   
#   
def home_key():
   
   adb_event( 1, 0x0001, 0x0066, 0x00000001 )
   adb_event( 1, 0x0000, 0x0000, 0x00000000 )
   adb_event( 1, 0x0001, 0x0066, 0x00000000 )
   adb_event( 1, 0x0000, 0x0000, 0x00000000 )

def power_key():
   
   adb_event( 1, 0x0001, 0x0074, 0x00000001 )
   adb_event( 1, 0x0000, 0x0000, 0x00000000 )
   adb_event( 1, 0x0001, 0x0074, 0x00000000 )
   adb_event( 1, 0x0000, 0x0000, 0x00000000 )
   
   
def back_key():
   
   Popen("adb shell input keyevent 4", stdout=PIPE, shell=True).stdout.read()
   
   
   
def swipe(start,stop):

   Popen("adb shell input swipe %d %d %d %d"%(start[0],start[1],stop[0],stop[1]), stdout=PIPE, shell=True).stdout.read()
   
def linear_swipe(start,stop,steps=1):
   xloc = np.linspace(start[0],stop[0],steps+1)
   yloc = np.linspace(start[1],stop[1],steps+1)

   
   adb_event( 2, 0x0003, 0x0039, 0x00000eb0 )
   adb_event( 2, 0x0003, 0x0035, xloc[0] )
   adb_event( 2, 0x0003, 0x0036, yloc[0] )
   adb_event( 2, 0x0003, 0x0030, 0x00000053 )
   adb_event( 2, 0x0003, 0x003a, 0x00000005 )
   adb_event( 2, 0x0000, 0x0000, 0x00000000 )
   
   for i in range(steps):
      adb_event( 2, 0x0003, 0x0035, xloc[i+1] )
      adb_event( 2, 0x0003, 0x0036, yloc[i+1] )
      adb_event( 2, 0x0003, 0x0030, 0x00000042 )
      adb_event( 2, 0x0003, 0x003a, 0x00000005 )
      adb_event( 2, 0x0000, 0x0000, 0x00000000 )
      
   adb_event( 2, 0x0003, 0x0039, 0xffffffff )
   adb_event( 2, 0x0000, 0x0000, 0x00000000 )
   

def scroll(dx,dy):
   
   Popen("adb shell input trackball roll %d %d"%(dx,dy), stdout=PIPE, shell=True).stdout.read()
   
  
   
def unlock_phone():
   
   power_key()
   time.sleep(1)
   home_key()
   time.sleep(.5)
   linear_swipe((187,616),(340,616))


def lock_phone():
   
   power_key()


def take_screenshot_adb():

#   Popen("adb shell /system/bin/screencap -p /sdcard/screenshot.png > error.log 2>&1;\
#          adb pull  /sdcard/screenshot.png screens/screenshot.png >error.log 2>&1", stdout=PIPE, shell=True).stdout.read()
          
#   Popen("adb shell screencap -p | sed 's/\r$//' > screens/screenshot.png", stdout=PIPE, shell=True).stdout.read()

#   Popen("adb shell screencap | sed 's/\r$//' > img.raw;\
#          dd bs=800 count=1920 if=img.raw of=img.tmp >/dev/null 2>&1;\
#          ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i img.tmp screens/screenshot.png >/dev/null 2>&1",
#          stdout=PIPE, shell=True).stdout.read()
      
   ################
   # CURRENT BEST #
   ################
       
   Popen("adb shell screencap | sed 's/\r$//' > img.raw", stdout=PIPE, shell=True).stdout.read()
   
   f = open('img.raw', 'rb')
   f1 = open('img1.raw', 'w')
   f.read(12) # ignore 3 first pixels (otherwise the image gets offset)
   rest = f.read() # read rest
   f1.write(rest)
    
   Popen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i img1.raw screens/screenshot.png >/dev/null 2>&1", stdout=PIPE, shell=True).stdout.read()

   
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
      
      
def readImage(image_file, xbounds=None, ybounds=None):
   image = cv2.imread(image_file)
      
   if not xbounds:
      if not ybounds:
         return image
      else:
         return image[ybounds[0]:ybounds[1],:]
   else:
      if not ybounds:
         return image[:,xbounds[0]:xbounds[1]].copy()
      else:
         return image[ybounds[0]:ybounds[1],xbounds[0]:xbounds[1]].copy()
      
      
def swipeReference(template, destination=(0,0), threshold=0.96, print_coeff=False, xbounds=None, ybounds=None, reuse_last_screenshot=False):
   
   ref = locateTemplate(template, threshold=threshold, retries=2, print_coeff=print_coeff, xbounds=xbounds, ybounds=ybounds, reuse_last_screenshot=reuse_last_screenshot)
   
   if not ref:
      printAction("Unable to navigate to swipe reference...", newline=True)
      return None
   
   if not xbounds:
      xbounds = (0,480)
   if not ybounds:
      ybounds = (0,800)
      
   diff = np.array(destination) - (ref + np.array([xbounds[0],ybounds[0]]))
   
   swipe(ref,map(int,ref+0.613*diff))
   time.sleep(.3)
   swipe(ref,map(int,ref+0.613*diff))
   time.sleep(.5)
   return ref
   

def locateTemplate(template, threshold=0.96, offset=(0,0), retries=1, interval=1, print_coeff=True, xbounds=None, ybounds=None, reuse_last_screenshot=False,
                    click=False, scroll_size=[], swipe_size=[], swipe_ref=['',(0,0)]):
   try:
      image_template = cv2.imread(template)
   except:
      print( template+" does not seem to exist." )
      return False
   
   for i in range(retries):
      if not reuse_last_screenshot:
         take_screenshot_adb()
      
      time.sleep(.1)
      try:
         image_screen   = readImage("screens/screenshot.png", xbounds, ybounds)
#         image_screen   = readImage("test.png", xbounds, ybounds)
      except:
         print("ERROR: Unable to load screenshot.png. This is bad, and weird!!!")
         return False
      
      try:
         result = cv2.matchTemplate(image_screen,image_template,cv2.TM_CCOEFF_NORMED)
      except:
         print("ERROR: Unable to match template \"%s\" with screenshot!!!"%template)
         return False
      
      if print_coeff:
         sys.stdout.write("%.2f "%result.max())
         sys.stdout.flush()
#         print( " %.2f"%result.max(), end='' )
         
      if result.max() > threshold:
         template_coords = np.unravel_index(result.argmax(),result.shape)
         template_coords = np.array([template_coords[1],template_coords[0]])
         object_coords = tuple(template_coords + np.array(offset))
         if click:
            left_click(object_coords)
            time.sleep(3)
         if print_coeff:
            sys.stdout.write("(%d,%d) "%(object_coords[0],object_coords[1]))
            sys.stdout.flush()
#         print(" (%d,%d)"%(object_coords[0],object_coords[1]),end=' ')
         return object_coords
      
      else:
         # See if the cause can be an Android error:
         image_error = cv2.imread("screens/android_error.png")
         err_result  = cv2.matchTemplate(image_screen,image_error,cv2.TM_CCOEFF_NORMED)
         if print_coeff:
            sys.stdout.write("%.2f "%err_result.max())
            sys.stdout.flush()
#         print( " %.2f"%err_result.max(), end='' )
         if err_result.max() > 0.9:
            print(' ')
            printAction( "Android error detected and will (hopefully) be dealt with.", newline=True )
            template_coords = np.unravel_index(err_result.argmax(),err_result.shape)
            template_coords = np.array([template_coords[1],template_coords[0]])
            left_click(template_coords + np.array([319,31]))
            retries = retries + 1                    

      if retries > 1:
         if swipe_ref[0] != '':
            swipeReference(swipe_ref[0], destination=swipe_ref[1], reuse_last_screenshot=False)
         if swipe_size:
            swipe(swipe_size[0],swipe_size[1])
            if interval < 1:
               time.sleep(1)
            else:
               time.sleep(interval)
         if scroll_size:
            scroll(scroll_size[0],scroll_size[1])
            if interval < 1:
               time.sleep(3)
            else:
               time.sleep(interval)
      
   return None
      
   
def check_if_vnc_error():
#   printAction( "Verifying VNC sanity..." )
#   ok_button = locateTemplate('screens/vnc_error.png', correlation_threshold=0.992, offset=(318,124))
#   printResult(not ok_button)
#   if ok_button:
#      replay_macro("left_click",offset=ok_button)
   pass
      
def abort_if_vnc_died():
#   titlebar_coords = locateTemplate('screens/titlebar.png', correlation_threshold=0.6)
#   titlebar_black_coords = locateTemplate('screens/titlebar_black.png', correlation_threshold=0.6)
#   if titlebar_coords == None and titlebar_black_coords == None:
#      raise Exception("VNC appears to have died. Aborting.")
   pass

def preOCR(image_name, color_mask=(1,1,1), threshold=180, invert=True, xbounds=None, ybounds=None):
   
   import scipy.interpolate as interpolate
   
   image = readImage(image_name,xbounds,ybounds)
#   image = readImage(image_name)
   
   # Adjust color information
   image[:,:,0] = image[:,:,0]*color_mask[0]
   image[:,:,1] = image[:,:,1]*color_mask[1]
   image[:,:,2] = image[:,:,2]*color_mask[2]
   
   # Convert to grey scale
   image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   
   # Normalize
   img_min, img_max = image.min(), image.max()
   image = 255*(image-float(img_min))/(float(img_max)-img_min)
   
   #Upinterpolate
   M,N = image.shape
   m_idx = np.linspace(0,1,M)
   n_idx = np.linspace(0,1,N)
   
   K = 2 # Upsampling factor
   m_up_idx = np.linspace(0,1,M*K)
   n_up_idx = np.linspace(0,1,N*K)
      
   image = interpolate.RectBivariateSpline(m_idx, n_idx, image, kx=4, ky=4)(m_up_idx,n_up_idx)
      
   #Inversion
   if invert:
      image = 255-image
      
   # Thresholding
   img = image**20
   image = 255*img/(img+float(threshold)**20)
#   image = 255/(1+(float(threshold)/image)**20)
   
#   image[image>=threshold] = 255
#   image[image< threshold] = 0

   # Reverting to int8
   image = image.astype('uint8')
   
   cv2.imwrite( image_name.strip('.png')+'_processed.png', image )
   
   return image
   

def runOCR(image,mode='',lang='eng'):
   
   if mode == 'line':
      psm = '-psm 7'
   elif mode == '':
      psm = ''
   else:
      print( "ERROR: runOCR() - Mode %s is not supported")
      return ''
   
   if lang=='event_enemy':
      language = 'non'
   else:
      language = 'eng'
   
   cv2.imwrite( 'tmp.png', image )
   Popen("tesseract tmp.png text %s -l %s >/dev/null 2>&1"%(psm,language), shell=True, stdout=PIPE).stdout.read()
   
   if os.path.getsize('text.txt') == 1:
      print( "ERROR: runOCR() returned no output")
      return ''
   
   # TODO make sure file is not empty!!!
   text  = open('text.txt','r').read()
#   text  = re.sub(r'\s', '', text) # Remove whitespaces
#   text  = re.sub(r',', '', text) # Remove commas
   text  = re.sub(r'\n', '', text) # Remove newlines
   
   return text

def gotoMyPage():
   
   printAction("Clicking MyPage button...")
   mypage_button = locateTemplate("screens/mypage_button.png", offset=(56,21), retries=5)
   printResult(mypage_button)
   
   if not mypage_button:
      printAction( "Huh? Unable to find MyPage button!!! That is bad.", newline=True)
      return False
   
   left_click(mypage_button)
   time.sleep(4)
   return True

def getMyPageStatus():
   
   info = {'roster':[]}
   
   print("Get MyPage info...")
   
   entered_mypage = False
   for i in range(2):
      gotoMyPage()
      
      printAction("Locating status screen...")
      swipe((240,600),(240,200))
      time.sleep(.5)
      
      mypage_status_corner = locateTemplate("screens/mypage_status_upper_left_corner.png")
      printResult(mypage_status_corner)
      
      if mypage_status_corner:
         entered_mypage = True
         break
      
      else:
         left_click((200,200)) # Possibly daily reward screen
         time.sleep(5)
         printNotify('Unable to read MyPage. Daily reward?', 60)
                  
   if not entered_mypage:
      printAction( "Adjust scrolling, this isn't working.", newline=True)
      return False

   printAction("Running OCR to figure out cards in roster...")
   cards_in_roster_image  = preOCR("screens/screenshot.png",color_mask=(0,1,0),xbounds=(238,282),ybounds=(mypage_status_corner[1]+274,mypage_status_corner[1]+287))
   cards_in_roster_string = runOCR(cards_in_roster_image,mode='line')

   cards_in_roster_numbers = re.findall(r'\d+', cards_in_roster_string)
   cards_in_roster = tuple(map(int, cards_in_roster_numbers))
   
   try:
      print("Cards: %d/%d"%cards_in_roster)
      info['roster'] = cards_in_roster
      if cards_in_roster[1] - cards_in_roster[0] < 15:
         print("WARNING: Roster is soon full!!!")

   except:
      printAction("Unable to determine roster size.", newline=True)
      info['roster'] = [30,70]
      cv2.imwrite( 'tmp_last_error.png', cards_in_roster_image )
      
   printAction("Running OCR to figure out amount of silver...")
   silver_image  = preOCR("screens/screenshot.png",color_mask=(1,1,0),xbounds=(242,307),ybounds=(mypage_status_corner[1]+300,mypage_status_corner[1]+320))
   silver_string = runOCR( silver_image, mode='line', lang='event_enemy' )
#   silver_numbers = re.search(r'[0-9,]+', silver_string).group(0)
#   silver_numbers = re.sub(r',', '', silver_numbers)
   
   try:
      silver_numbers = re.search(r'.+[,\.][0-9]{1,3}', silver_string).group(0)
      silver_numbers = re.sub(r'\s', '', silver_numbers)
      silver_numbers = re.sub(r',', '', silver_numbers)
      silver_numbers = re.sub(r'\.', '', silver_numbers)


      silver = int(silver_numbers)
      print("Silver: %d"%silver)
      info['silver'] = silver
   
   except:
      printAction("Unable to determine silver amount.", newline=True)
      cv2.imwrite( 'tmp_last_error.png', silver_image )
   
   return info

def gotoEventHome():
   
   gotoMyPage()
         
   printAction("Clicking Fantastic 4 button...")
   event_fantastic4 = locateTemplate("screens/event_fantastic4_button.png", offset=(56,21), retries=5)
   printResult(event_fantastic4)
   
   if not event_fantastic4:
      printAction( "Huh? Unable to find Fantastic 4 event button!!! That is bad.", newline=True)
      return False
   
   left_click(event_fantastic4)
   time.sleep(3)
   return True

   
def eventPlayMission(repeat=50):

   print( "Playing event mission..." )

   for i in range(repeat+1):
      gotoMyPage()
   
      printAction("Searching for event mission button...")
      event_mission_button = locateTemplate("screens/event_newest_event_mission_button.png", threshold=0.95,
                                             offset=(109,23), retries=5, swipe_size=[(240,600),(240,295)])
      printResult(event_mission_button)
      
      if not event_mission_button:
         
         # Double check that the return from mission actually was registered.
         mission_started = locateTemplate('screens/mission_bar.png', print_coeff=False, reuse_last_screenshot=True)
         if mission_started:
            printAction("Seems we failed to return from mission. Retrying.", newline=True)
            back_key()
            time.sleep(1)
         
         else:

            gotoMyPage()
         
            printAction("Searching for event mission button...")
            event_mission_button = locateTemplate("screens/event_newest_event_mission_button.png", threshold=0.95,
                                                   offset=(109,23), retries=5, swipe_size=[(240,600),(240,295)])
            printResult(event_mission_button)
      
            repeat = repeat + 1
                    
      else:
         left_click(event_mission_button)
         printAction( "Avaiting mission screen..." )
         mission_success = False
         
         for i in range(10):
            time.sleep(1)
            
            mission_boss  = locateTemplate('screens/event_mission_boss_screen.png', print_coeff=False)
            out_of_energy = locateTemplate('screens/out_of_energy.png', print_coeff=False, reuse_last_screenshot=True)
            #printResult(out_of_energy)
            
            mission_started = locateTemplate('screens/mission_bar.png', threshold=0.985, reuse_last_screenshot=True)
            #printResult(mission_started)
            
            if mission_boss:
               go_to_boss = locateTemplate("screens/event_mission_go_to_boss.png",
                                            offset=(130,16), retries=5, click=True, ybounds=(0,600), swipe_size=[(240,600),(240,295)])
               if not go_to_boss:
                  print( '' )
                  printAction("Unable to find \"go to boss\" button...", newline=True)
                  return False
               
               printResult(False)
               printAction( "Raid boss detected. Playing the boss...", newline=True )
               
               face_the_enemy = locateTemplate("screens/face_the_enemy_button.png",
                                                offset=(130,16), retries=8, click=True, ybounds=(0,600), swipe_size=[(20,600),(20,295)])
               if not face_the_enemy:
                  printAction("Unable to find \"face the enemy\" button...", newline=True)
                  return False
      
               fight_enemy =  locateTemplate("screens/event_mission_boss_fight_button.png", threshold=0.9,
                                                offset=(85,24), retries=5, click=True)
               if not fight_enemy:
                  printAction("Unable to find \"FIGHT\" button...", newline=True)
                  return False
               
               confirm =  locateTemplate("screens/event_mission_boss_confirm_button.png", threshold=0.9,
                                                offset=(85,24), retries=5, click=True)
               if not confirm:
                  printAction("Unable to find \"FIGHT\" button...", newline=True)
                  return False
               
               return True
               
               
            if out_of_energy:
               print( '' )
               printAction("No energy left! Exiting.", newline=True)
               back_key()
               time.sleep(1)
               return True
               
            if mission_started:
               print( '' )
               printAction("Mission started. Returning.", newline=True)
               back_key()
               time.sleep(1)
               mission_success = True           

         if not mission_success:
            printAction("Timeout when waiting for mission screen", newline=True)
            return False
            


def eventFindEnemy(find_enraged=True, watchdog=10):
   
   printAction("Searching for a decent foe...")
   info = {'is_enraged':False}
   keep_assessing = True
   swipe((10,400),(10,200))
   while keep_assessing and watchdog > 0:
      keep_assessing = False
      is_enraged = False
      for j in range(10):
         ref = swipeReference("screens/event_enemy_info_frame.png", destination=(0,80), ybounds=(150,500), reuse_last_screenshot=True)
         if not ref:
            return info
         time.sleep(1)
         event_enemy_corner = locateTemplate("screens/event_enemy_info.png", threshold=.80, ybounds=(0,400), reuse_last_screenshot=False)
         if event_enemy_corner:
            break
         else:
            printAction("This is fishy fish", newline=True)
         
      printResult(event_enemy_corner)
         
      if not event_enemy_corner:
         printAction("Unable to locate decent foe...")
         return False
      
      if find_enraged:
         printAction("Checking if enemy is enraged...")
         increased_raid_rating = locateTemplate("screens/event_3_times_raid_rating.png", threshold=.85, retries=3, ybounds=(0,450))
         printResult(increased_raid_rating)
         if increased_raid_rating:
            is_enraged = True
         else:
            keep_assessing = True
            watchdog = watchdog - 1
            
      
      printAction("Running OCR to figure out badass name and level...")
   #   printAction("Preprocessing image")
   
      badguy_image  = preOCR("screens/screenshot.png",xbounds=(110,370),ybounds=(event_enemy_corner[1]-49,event_enemy_corner[1]-18))
      badguy_string = runOCR( badguy_image, mode='line')
   
      badguy_name  = re.sub(r' Lv.+', '', badguy_string)
      badguy_level = re.sub(r'.+Lv\.', '', badguy_string)
   #   badguy_level= tuple(map(int, badguy_string))
      
      print( "%s at level %s"%(badguy_name, badguy_level) )
            
      printAction("Running OCR to figure out enemy info...", newline=True)
      e = event_enemy_corner
      enemy_image = preOCR("screens/screenshot.png",color_mask=(0,1,0),xbounds=(e[0],470),ybounds=(e[1],e[1]+144)) #old x: e[0]+250
      enemy_info  = runOCR(enemy_image, mode='', lang='event_enemy')
   
      enemy_health = re.findall(r'\d+', enemy_info)
      try:
         enemy_health = tuple(map(int, enemy_health))
      except:
         print( 'WARNING: Unable to convert enemy health to int.' )
      
      try:
         if int(badguy_level) < 50  or (int(badguy_level) > 85 and not find_enraged):
            printAction("Villain has a level outside [50,85]. Moving on...", newline=True)
            keep_assessing = True
            watchdog = watchdog - 1
            swipe((10,400),(10,350))
      except:
         pass
      
      info['badguy_name']  = badguy_name
      info['badguy_level'] = badguy_level
      info['is_enraged']   = is_enraged
      
   return info
      
def eventKillEnemies():
   
   printAction("Locating the \"face enemy\" button...")
   event_face_enemy = locateTemplate("screens/event_mission_button.png", offset=(240,-54), threshold=0.92, retries=2, reuse_last_screenshot=False, click=True)
   printResult(event_face_enemy)
   if not event_face_enemy:
      printAction("Unable to locate \"face enemy\" button...")
      return False
   
#   swipe((10,500),(10,300))
   time.sleep(1)
   
   for i in range(1):
      take_screenshot_adb()
#      if not i:
#         swipeReference("screens/event_enemy_info_frame.png", destination=(0,80), reuse_last_screenshot=False)
      enraged_enemy_found = False
      for j in range(5):
         info = eventFindEnemy(find_enraged=True)
         if info['is_enraged']:
            enraged_enemy_found = True
            break
#        scroll(0,-1000)
         printAction('Unable to find enraged enemy. Retrying in 30 sec (%d/5)...'%(j+1), newline=True)
         time.sleep(30)
  
         gotoEventHome()
         event_enemies_in_area = locateTemplate("screens/event_enemies_in_area.png",
            offset=(154,89), retries=5, ybounds=(0,400), swipe_size=[(240,600),(240,295)])
         if not event_enemies_in_area:
            return False
         event_face_enemy = locateTemplate("screens/event_mission_button.png",
            offset=(240,-54), threshold=0.92, retries=2, reuse_last_screenshot=False, click=True)
         if not event_face_enemy:
            return False
         take_screenshot_adb()
         
      if not enraged_enemy_found:
         return False
      
      time.sleep(2)
      printAction("Searching for \"go support\" or \"attack\" button...")
      support        = locateTemplate("screens/event_go_support_button.png", threshold=0.92, reuse_last_screenshot=True, click=True)
      attack_villain = locateTemplate("screens/event_attack_button.png", threshold=0.92, reuse_last_screenshot=True, click=True)
      printResult(bool(support or attack_villain))
      if not attack_villain and not support:
         printAction("Unable to find an enemy to attack!", newline=True)
         return False
#      left_click(event_enemy_corner+np.array((66,164)))
#      left_click(event_enemy_corner+np.array((66,164)))
      time.sleep(1)
      
      printAction("Searching for deck select button...")
      for j in range(5):
         swipe((10,400),(10,200))
         select_deck = locateTemplate("screens/select_deck_button.png", threshold=.96, offset=(-144,17), ybounds=(0,600), click=True)
         if select_deck:
            break
      printResult(select_deck)
         
      printAction("Selecting raider deck...")
      raider_deck = locateTemplate("screens/select_deck_raider.png", offset=(205,35), click=True)
      printResult(raider_deck)
      if not raider_deck:
         return False
   
      printAction("Hitting select button...")
      select_button = locateTemplate("screens/select_button.png", offset=(60,16), click=True)
      printResult(select_button)
      if not select_button:
         return False
                  
      # Assess the timer structure. It will basically count number of swipes, shitty.
      weird_bool = True
      watchdog = 15
      while watchdog > 0:
#      for j in range(10):
         if weird_bool:
            printAction("Attempting to locate \"face the enemy\" button...")
         face_the_enemy  = locateTemplate("screens/event_face_the_enemy_button.png", offset=(116,17), ybounds=(0,500))        
         face_the_enemy2 = locateTemplate("screens/event_face_the_enemy_button2.png", offset=(116,17), ybounds=(0,500), reuse_last_screenshot=True) 
         
         if not face_the_enemy and not face_the_enemy2:
            
            out_of_power = locateTemplate('screens/event_out_of_power.png', threshold=0.985, print_coeff=False, reuse_last_screenshot=True)
            if out_of_power:
               print( '' )
               printAction("No attack power left! Exiting.", newline=True)
               return False
            
            end_of_battle = locateTemplate('screens/event_battle_results.png', reuse_last_screenshot=True)
            if end_of_battle:
               print( '' )
               printAction("Villain taken down. Returning.", newline=True)
               return True
            
#            time.sleep(3)
            swipe((240,400),(240,200)) # This sometimes cause trouble with the face the enemy button
            time.sleep(1)
            weird_bool = False
            watchdog = watchdog - 1
            if not watchdog:
               printResult(False)
               printAction("Timeout when hoping for low-power termination ..", newline=True)
               return True
            
         else:
            printResult(True)
            printAction( "Checking if \"ask for support\" option is available..." )
            ask_for_support = locateTemplate("screens/event_ask_for_support_button.png", offset=(112,15), click=True)
            printResult(ask_for_support)
            
            if ask_for_support:
               printAction( "Support asked for. Starting over...", newline=True )
               return True
            
            left_click(face_the_enemy)
            time.sleep(3)
            
            printAction( "Avaiting mission screen..." )

            mission_success = False
            for i in range(10):
               time.sleep(1)
               
               out_of_power    = locateTemplate('screens/event_out_of_power.png',   threshold=0.985, print_coeff=False)
               mission_started = locateTemplate('screens/event_fight_screen.png',   reuse_last_screenshot=True)
               end_of_battle   = locateTemplate('screens/event_battle_results.png', reuse_last_screenshot=True)
               #printResult(mission_started)
                  
               if out_of_power:
                  print( '' )
                  printAction("No attack power left! Exiting.", newline=True)
#                  back_key()
                  return False
               
               if end_of_battle:
                  print( '' )
                  printAction("Villain taken down. Returning.", newline=True)
                  return True
                  
               if mission_started:
                  print( '' )
                  printAction("Mission started. Returning.", newline=True)
                  back_key()
                  time.sleep(int(uniform(1,2)))
                  mission_success = True
                  weird_bool = True
                  break
               
               # Sometimes one end up at the same screen too. Handle this.
               
            
            weird_bool = True
            if not mission_success:
               printResult(False)
               printAction("Timeout when waiting for mission screen. Defeated?", newline=True)
               return True        
        
         
         
#   badguy_name  = re.sub(r' Lv.+', '', badguy_string)
#   badguy_level = re.sub(r'.+Lv\.', '', badguy_string)
#   badguy_level= tuple(map(int, badguy_string))
   
#   print( badguy_level )
   

      
   
def eventPlay():
      
   print("PLAYING EVENT")
   
   for i in range(10):
      
      gotoEventHome()
  
      printAction("Checking if enemies are present in the area...")
      event_enemies_in_area = locateTemplate("screens/event_enemies_in_area.png",
         offset=(154,89), retries=5, ybounds=(0,400), swipe_size=[(240,600),(240,295)])
      printResult(event_enemies_in_area)
      
      if event_enemies_in_area:
         success = eventKillEnemies()
      else:
         success = eventPlayMission()
      
      if not success:
         return False   
      
      time.sleep(2)
   
   return True
      
      
   
def listSortAlignment(alignment_type):
   
   printAction("Making sure alignment is set to \"%s\"..."%alignment_type)
   alignment_button             = locateTemplate("screens/alignment_button_%s.png"%alignment_type, threshold=0.95, offset=(56,22))
   alignment_button_highlighted = locateTemplate("screens/alignment_button_%s_highlighted.png"%alignment_type, threshold=0.95, offset=(56,22))
   printResult(alignment_button or alignment_button_highlighted)
      
   if not alignment_button_highlighted:
      
      if not alignment_button:
         printAction( "Unable to find alignment \"%s\" button!."%alignment_type, newline=True)
         return False
         
      left_click(alignment_button)
      time.sleep(2)


def selectCard(card_name, alignment='all'):
   
   if alignment != 'none':
      listSortAlignment(alignment)
   
   ########
   # TODO # Sort mechanism
   ########
      
   printAction("Locating and selecting the mentioned card...")
#   swipe((240,630),(240,198))
#   time.sleep(.3)
#   swipe((240,630),(240,198))
   swipe((1,630),(479,100))
   time.sleep(.5)
#   swipe((1,630),(479,400))
#   time.sleep(.5)
#   clicked_cards = []
   number_of_cards_selected = 0
   
#   card_coords = locateTemplate("screens/card_%s.png"%card_name, correlation_threshold=0.95, offset=(214,86),
#                                ybounds=(0,600), swipe_ref=['list_select_button_area',()])

   # Cards with stapled lines are skipped (base card)
   top = locateTemplate("screens/list_top_separator.png")
   if not top:
      printResult(False)
      printAction("Could not find the top of list? Weird.", newline=True)
      return False
   
   swipeReference("screens/list_top_separator.png", destination=(20,90), print_coeff=True, reuse_last_screenshot=True)
   
   for i in range(15):
      card_coords = locateTemplate("screens/card_%s.png"%card_name, threshold=0.95, offset=(214,86), ybounds=(0,550))
      select_bar = locateTemplate("screens/list_select_button_area.png", offset=(18,26), ybounds=(150,550), reuse_last_screenshot=True)
      if card_coords and select_bar:
         left_click([select_bar[0],select_bar[1]+150])
         number_of_cards_selected += 1
         time.sleep(.5)
         break
      
#      swipe((1,600),(479,500))
#      time.sleep(1)
      line_separator = swipeReference("screens/list_line_separator.png", destination=(20,90), ybounds=(150,600), threshold=0.85, print_coeff=True, reuse_last_screenshot=True)
      if not line_separator:
         printResult(False)
         printAction("Assuming no more cards can be found...", newline=True)
         break
#      swipe((1,600),(479,295)) # scroll one card at a time
      time.sleep(1)
      
   if number_of_cards_selected == 0:
      printResult(False)
      printAction("Could not find any of the specified cards...", newline=True)
      return False
   
   printResult(True)
   return True
   

def markCards(cards_list, alignment='all'):
   
   stats = Stats()
   listSortAlignment(alignment)
   
   ########
   # TODO # Sort mechanism
   ########
      
   printAction("Locating and marking the mentioned cards...")
#   swipe((240,630),(240,198))
#   time.sleep(.3)
#   swipe((240,630),(240,198))
   swipe((240,630),(240,220))
   time.sleep(.3)
#   clicked_cards = []
   number_of_cards_selected = 0
   
   for i in range(15):
      take_screenshot_adb()
      for card in cards_list:
         card_coords = locateTemplate("screens/card_%s.png"%card, threshold=0.95, offset=(214,86), ybounds=(300,800), reuse_last_screenshot=True)
         
         if card_coords:
            left_click([card_coords[0],card_coords[1]+300])
            number_of_cards_selected += 1
            stats.add(card, 1)
            time.sleep(.5)
            break
            
      
      swipe((240,600),(240,295)) # scroll one card at a time
      time.sleep(1)
      
   if number_of_cards_selected == 0:
      printResult(False)
      printAction("Could not find any of the specified cards...", newline=True)
      return False
   
   return True
   
def sellCards(cards_list, alignment='all'):
      
   print("SELLING")
   printAction("Selling cards: ")
   for card in cards_list:
      print( "%s "%card, end='' )
   print('')
   
   stats = Stats()
      
   printAction("Clicking roster button...")
   menu_button = locateTemplate("screens/menu_button.png", offset=(56,12))
   
   if not menu_button:
      printAction( "Huh? Unable to find menu button!!! That is bad.", newline=True)
      printResult(False)
      return False
   
   left_click(menu_button)
   time.sleep(int(uniform(.5,1)))
   
   roster_button = locateTemplate("screens/main_menu.png", offset=(317,189), retries=3)
   
   if not roster_button:
      printAction( "Unable to find main menu!.", newline=True)
      printResult(False)
      return False
   
   printResult(True)
   left_click(roster_button)
   time.sleep(int(uniform(1,2)))
   
   printAction("Searching for \"Sell Cards\" button...")
   sell_cards_button = locateTemplate("screens/sell_cards_button.png", offset=(107,23), retries=3)
   printResult(sell_cards_button)
   
   if not sell_cards_button:
      printAction( "Unable to find \"Sell Cards\" button!.", newline=True)
      return False

   left_click(sell_cards_button)
   time.sleep(1)
   
   cards_found = markCards(cards_list, alignment='all')
   printResult(cards_found)
   if not cards_found:
      printAction( "No cards were found. Returning.", newline=True)
      return False
   
   printAction("Clicking \"Sell Selected\" button...")
#   scroll(0,500)
   sell_selected_button = locateTemplate("screens/sell_selected_button.png", offset=(92,17), retries=2)
   printResult(sell_selected_button)
   
   if not sell_selected_button:
      printAction( "Unable to find \"Sell Selected\" button", newline=True)
      return False

   left_click(sell_selected_button)
   time.sleep(3)
   
   scroll(0,1000)
   sell_button = locateTemplate("screens/sell_button.png", offset=(49,19), retries=4)
   
   if not sell_button:
      printAction( "Unable to find \"Sell\" button", newline=True)
      return False
      
   left_click(sell_button)
   printResult(True)
   time.sleep(3)

#   if number_of_cards_selected < 10:
#      return False
#   else:
      
   return True


   
def boostCard(card_name, cards_list, alignment='all'):
      
   print("BOOSTING")
   printAction("Boosting card: %s"%card_name, newline=True)
      
   printAction("Clicking \"boost\" button...")
   
   scroll(0,1000)
   time.sleep(2)
   boost_from_fuse = locateTemplate("screens/boost_from_fuse_button.png", offset=(193,19), retries=4)
   printResult(boost_from_fuse)
   
   if not boost_from_fuse:
      printAction( "Huh? Unable to find boost button!!! That is bad.", newline=True)
      return False
   
   left_click(boost_from_fuse)
   time.sleep(4)
   
   swipe((240,650),(240,100))
   time.sleep(1)
     
   listSortAlignment(alignment)
   
   printAction("Checking that multiple cards are selected...")
   multiple_cards_link = locateTemplate("screens/list_multiple_cards_link.png", offset=(54,33))
   printResult(multiple_cards_link)
   
   if multiple_cards_link:
      left_click(multiple_cards_link)
      time.sleep(3)
      swipe((240,650),(240,100))
      time.sleep(1)
   
   ########
   # TODO # Sort mechanism
   ########
      
   printAction("Locating and marking the mentioned cards...")
#   swipe((240,630),(240,198))
#   time.sleep(.3)
#   swipe((240,630),(240,198))
   scroll(0,-1000)
   time.sleep(1)
   swipe((240,600),(240,100))
   time.sleep(1)
   swipe((240,600),(240,100))
   time.sleep(1)
   swipe((240,600),(240,100))
   time.sleep(1)
#   clicked_cards = []
   number_of_cards_selected = 0
   
   for i in range(11):
      take_screenshot_adb()
      for card in cards_list:
         card_coords = locateTemplate("screens/card_%s.png"%card, threshold=0.95, offset=(214,86), ybounds=(300,800), reuse_last_screenshot=True)
         
         if card_coords:
            left_click([card_coords[0],card_coords[1]+300])
            number_of_cards_selected += 1
            time.sleep(.5)
            break
            
      swipe((240,600),(240,295)) # scroll one card at a time
      time.sleep(1)
      
   if number_of_cards_selected == 0:
      printResult(False)
      printAction("Could not find any of the specified cards...", newline=True)
      return False
   
   printResult(True)
   printAction("Clicking \"Boost\" button...")
#   scroll(0,500)
   boost_now = locateTemplate("screens/boost_green_button.png", offset=(58,17), retries=2)
   printResult(boost_now)
   
   if not boost_now:
      printAction( "Unable to find \"Boost\" button", newline=True)
      return True

   left_click(boost_now)
   time.sleep(3)
   
   printAction("Clicking \"Boost\" button (second time)...")
   scroll(0,1000)
   time.sleep(2)
   boost_now = locateTemplate("screens/boost_green_button.png", offset=(58,17), retries=2)
   printResult(boost_now)
   
   if not boost_now:
      printAction( "Unable to find \"Boost\" button", newline=True)
      return False
   
   left_click(boost_now)
   
   printAction("Waiting for boost finished screen...")
   time.sleep(5)
   boost_finished = locateTemplate("screens/boost_finished.png", offset=(58,17), retries=15)
   printResult(boost_finished)
   
   if not boost_finished:
      printAction( "Unable to find \"Boost\" button", newline=True)
      return False
   
   time.sleep(10)
   left_click((200,200))
   time.sleep(3)
   left_click((200,200))
   time.sleep(4)
      
   return True

def fuseCard(card_type, alignment='all'):
      
   print("FUSION")
   
   stats = Stats()
   
   printAction("Clicking fusion button...")
   fusion_button_coords = locateTemplate("screens/fusion_button.png", offset=(60,26), retries=2 )
   fusion_button2_coords = locateTemplate("screens/fusion_button2.png", offset=(60,26))
   printResult(fusion_button_coords or fusion_button2_coords)
   
   if not fusion_button_coords and not fusion_button2_coords:
      printAction( "Huh? Unable to find fusion button!!! That is bad.", newline=True)
      return
   
   if fusion_button_coords:
      left_click(fusion_button_coords)
   else:
      left_click(fusion_button2_coords)
      
   time.sleep(int(uniform(.5,1)))
   
   printAction("Checking if more cards are available...")
   fuse_no_cards_left = locateTemplate("screens/fuse_no_cards_left.png", offset=(195,14))
   printResult(not fuse_no_cards_left)
   
   if fuse_no_cards_left:
      return False

   printAction("Checking if a base card is already selected...")
   for i in range(3):
      change_base_card_coords = locateTemplate("screens/fusion_change_base_card_button.png", offset=(144,15))
      base_card_menu          = locateTemplate("screens/fusion_select_base_card.png", offset=(100,14))
            
      if change_base_card_coords:
         time.sleep(.3)
         left_click(change_base_card_coords)
         time.sleep(1)
         break
         
      if base_card_menu:
         break

   time.sleep(1)
   printResult(change_base_card_coords or base_card_menu)
     
   printAction("Searching for a base card...", newline=True)   
   success = selectCard(card_type, alignment=alignment)
   printResult(success)
   if not success:
      printAction( "Unable to find a base card.", newline=True)
      return False
         
   time.sleep(2)
   printAction("Searching for a fuser card...", newline=True)
#   swipe((240,600),(240,100))
   success = selectCard(card_type, alignment='none')
   if not success:
      printAction( "Unable to find the fuser. This is strange and should not happen.", newline=True)
      return False
            
   printAction("Clicking \"fuse this card\" button...")
   fuse_this_card_button_coords = locateTemplate("screens/fusion_fuse_this_card_button.png", offset=(106,16), retries=5)
   printResult(fuse_this_card_button_coords)
   
   if not fuse_this_card_button_coords:
      return False
   
   time.sleep(1)
   left_click(fuse_this_card_button_coords)
   time.sleep(4) # The fusion thing takes some time.
   
   printAction("Waiting for first fusion screen...")
   rarity_upgraded = locateTemplate("screens/fusion_rarity_upgraded.png", threshold=0.98, offset=(243,70), retries=10)
   
#   if not ironman_fused_screen1:
#      return False
#   
#   for i in range(10):
#      time.sleep(int(uniform(1,2)))
#      ironman_fused_screen1 = locateTemplate("screens/fusion_ironman_fused1.png", offset=(155,200), retries=5)
#            
#      if ironman_fused_screen1:
#         left_click(ironman_fused_screen1)
#         break
   
   printResult(rarity_upgraded) 
   if not rarity_upgraded:
      printAction( "First fusion screen did not appear. Buggy game?", newline=True)
      return False
   
   time.sleep(1)
   stats.add(card_type, 2)
   left_click(rarity_upgraded)
   time.sleep(1)
   
   printAction("Waiting for fusion finished screen...")
   for i in range(10):
      time.sleep(int(uniform(1,2)))
      left_click(rarity_upgraded)
      ironman_finished = locateTemplate("screens/fusion_finished.png", offset=(240,110), retries=3)
            
      if ironman_finished:
         printResult(ironman_finished) 
         printAction( "Fusion successful!", newline=True)
         return True
   
   printResult(ironman_finished) 
   return False
      
      
def tradeCards(receiver='joinge', cards_list=['rare_ironman'], alignment='all'):
      
   print("TRADING")
   printAction("Trading the following cards to %s: "%receiver)
   for card in cards_list:
      print( "%s "%card, end='' )
   print('')
   
#   stats = Stats()
      
   printAction("Searching for recevier...")
   menu_button = locateTemplate("screens/menu_button.png", offset=(56,12))
   
   if not menu_button:
      printAction( "Huh? Unable to find menu button!!! That is bad.", newline=True)
      printResult(False)
      return False
   
   left_click(menu_button)
   time.sleep(1)
   
   player_search_button = locateTemplate("screens/main_menu.png", offset=(107,340), retries=3)
   
   if not player_search_button:
      printAction( "Unable to find main menu!.", newline=True)
      printResult(False)
      return False
   
   printResult(True)
   left_click(player_search_button)
   time.sleep(2)
   
   printAction("Entering receiver name...")
   text_field = locateTemplate("screens/text_box.png", offset=(68,22), retries=3)
   printResult(text_field)
   
   if not text_field:
      printAction( "Unable to find text field to enter receiver!.", newline=True)
      return False

   left_click(text_field)
   time.sleep(1)
   enter_text( receiver )
   time.sleep(1)
   search = locateTemplate("screens/player_search_button.png", offset=(57,17), print_coeff=False, reuse_last_screenshot=True)
   time.sleep(1)
   left_click(search) # Mobage password field
   time.sleep(3)
   printAction("Clicking receiver name...")
   left_click((345,672))
   time.sleep(3)
   
   trade = locateTemplate("screens/player_info_trade_button.png", offset=(55,14), retries=3)
   printResult(trade)
   
   if not trade:
      printAction( "Unable to find trade button on player info page!.", newline=True)
      return False

   left_click(trade)
   time.sleep(2)
   
   for card in cards_list:
      printAction("Adding another card for trade...")
      trade_card = locateTemplate("screens/trade_card_button.png", offset=(59,17), retries=3, ybounds=((450,800)))
      trade_card = tuple(np.array(trade_card) + (0,450))
         
      if not trade_card:
         printAction( "Unable to find card trade button!.", newline=True)
         return False
      
      time.sleep(1)
      left_click(trade_card)
      time.sleep(3)
      printResult(trade_card)
      
      cards_found = selectCard(card, alignment='all')
      printResult(cards_found)
      if not cards_found:
         printAction( "No cards were found. Returning.", newline=True)
         return False
   
   printAction("Trading for 1 silver...")
   trade_silver = locateTemplate("screens/trade_silver_button.png", offset=(59,17), retries=2, ybounds=((0,550)))
      
   if not trade_silver:
      printAction( "Unable to find card trade button!.", newline=True)
      return False
   
   time.sleep(1)
   left_click(trade_silver)
   time.sleep(3)
   printResult(trade_silver)
   
   printAction("Entering 1 silver...")
   text_field = locateTemplate("screens/text_box.png", offset=(68,22), retries=3)
   printResult(text_field)
   
   if not text_field:
      printAction( "Unable to silver text field!.", newline=True)
      return False
   
   left_click(text_field)
   time.sleep(1)
   enter_text( "1" )
   time.sleep(1)
   left_click((453,757))
#   add = locateTemplate("screens/add_button.png", offset=(46,17), reuse_last_screenshot=True)
#   time.sleep(1)
#   left_click(add) # Mobage password field
   time.sleep(3)
   
   scroll(0,1000)
   time.sleep(.5)
   swipe((10,100),(10,600))
   time.sleep(.5)
   
   printAction("Clicking \"Offer Trade\" button...")
   offer_trade = locateTemplate("screens/trade_offer_button.png", offset=(86,15))
   printResult(offer_trade)
   
   if not offer_trade:
      printAction( "Huh? Unable to find \"Offer Trade\" button!!! That is bad.", newline=True)
      return False
   
   left_click(offer_trade)
   time.sleep(3)

   return True
      
def play_mission(mission_number=(3,2), repeat=50, statistics=True):
      
   stats = Stats()
   
   if statistics:
      stats.silverStart("mission_%d-%d"%mission_number)
            
   print( "Playing mission %d-%d..."%mission_number )

   for i in range(repeat+1):
      check_if_vnc_error()
      printAction("Searching for mission %d-%d button..."%mission_number)
      mission_button_coords = locateTemplate("screens/mission_%d_%d.png"%mission_number, threshold=0.992, offset=(215,170), retries=3)
      printResult(mission_button_coords)
      if not mission_button_coords:
         
         # Double check that the return from mission actually was registered.
         mission_started  = locateTemplate('screens/mission_bar.png', print_coeff=False, reuse_last_screenshot=True)
         top_mission_list = locateTemplate('screens/mission_top_decor.png', print_coeff=False, reuse_last_screenshot=True)
         if mission_started:
            printAction("Seems we failed to return from mission. Retrying.", newline=True)
            back_key()
            time.sleep(1)
            repeat = repeat + 1
            
         # Are we simply at the top of the missions list?
         elif top_mission_list:
            printAction("Top of mission screen detected. Realigning...", newline=True)
            scroll(0,1000)
            time.sleep(.3)
            swipe((10,100),(10,350))
            time.sleep(.3)
            
            for i in range(mission_number[1]-1):
               swipe((10,100),(10,690))
               
            time.sleep(1)
            repeat = repeat + 1
            
         else:
            printAction( "Navigating to missions list...", newline=True )
            left_click((181,774)) # mission button
            time.sleep(3)
            scroll(0,1000)
   #         swipe((250,390),(250,80))
            printAction("Searching for \"operations\" button...")
            operations_button = locateTemplate("screens/operations_button.png", offset=(50,15), retries=6, click=True)
            printResult(operations_button)
            
            if not operations_button:
               return True
            #time.sleep(2)
            #left_click((240,602)) #operations button
            
            time.sleep(3)
            printAction( "Locating mission %d button..."%mission_number[0] )
            mission_button_coords = locateTemplate('screens/mission_list_%d.png'%mission_number[0], retries=5, threshold=0.92, offset=(170,10))
            printResult(mission_button_coords)
            if not mission_button_coords:
   #            time.sleep(1)
               printAction( "Locating mission %d button..."%mission_number[0] )
               swipe((20,600),(20,80))
               time.sleep(int(uniform(1,2)))
               mission_button_coords = locateTemplate('screens/mission_list_%d.png'%mission_number[0], threshold=0.92)
               printResult(mission_button_coords)
               
            if not mission_button_coords:
               print( "Unable to locate mission buttion. This shouldn't happen. Dammit!" )
               
               if statistics:
                  stats.silverEnd("mission_%d-%d"%mission_number)
               
               return True # Retry
            
            left_click(mission_button_coords)
            time.sleep(int(uniform(1,2)))
            #printAction( "Navigating to mission %d-%d..."%mission_number, newline=True )
            scroll(0,1000)
            time.sleep(.3)
            swipe((10,100),(10,350))
            time.sleep(.3)
            
            for i in range(mission_number[1]-1):
               swipe((10,100),(10,690))
               
            time.sleep(1)
            
            repeat = repeat + 1
            
            
            #if repeat > 30:
               #print( "30 mission iterations. Assuming error and exiting." )
               #return False
         
      else:
         left_click(mission_button_coords)
         printAction( "Avaiting mission screen..." )
         mission_success = False
         for i in range(10):
            time.sleep(int(uniform(1,2)))
            
            out_of_energy = locateTemplate('screens/out_of_energy.png', threshold=0.985, print_coeff=False)
            #printResult(out_of_energy)
            
            mission_started = locateTemplate('screens/mission_bar.png', threshold=0.985)
            #printResult(mission_started)
               
            if out_of_energy:
               print( '' )
               printAction("No energy left! Exiting.", newline=True)
               back_key()
               
               if statistics:
                  stats.silverEnd("mission_%d-%d"%mission_number)
               
               return True
               
            if mission_started:
               print( '' )
               printAction("Mission started. Returning.", newline=True)
               time.sleep(1)
               back_key()
               time.sleep(int(uniform(1,2)))
               mission_success = True
               
               if statistics:
                  stats.add("mission_%d-%d"%mission_number, 1)
                  
               break
         
         if not mission_success:
            printAction("Timeout when waiting for mission screen", newline=True)
            if statistics:
               stats.silverEnd("mission_%d-%d"%mission_number)
            return False
                                  
   if statistics:
      stats.silverEnd("mission_%d-%d"%mission_number)
          
          
def playNewestMission(repeat=50):

   print( "MISSION: Newest..." )

   for i in range(repeat+1):
      printAction("Searching for newest mission button...")
      mission_newest_button = locateTemplate("screens/mission_newest_button.png", threshold=0.95,
                                             offset=(193,14))
      printResult(mission_newest_button)
                  
      if not mission_newest_button:
         
         # Double check that the return from mission actually was registered.
         mission_started = locateTemplate('screens/mission_bar.png', print_coeff=False, reuse_last_screenshot=True)
         if mission_started:
            printAction("Seems we failed to return from mission. Retrying.", newline=True)
            back_key()
            time.sleep(1)
         
         else:

#            gotoMyPage()

            left_click((181,774)) # mission button
            time.sleep(3)
         
            printAction("Searching for newest mission button...")
            mission_newest_button = locateTemplate("screens/mission_newest_button.png", threshold=0.95,
                                                   offset=(193,14), retries=5, swipe_size=[(240,500),(240,295)])
            printResult(mission_newest_button)
            if not mission_newest_button:
               return False
               
            time.sleep(1)
            
            repeat = repeat + 1
                    
      else:
         left_click(mission_newest_button)
         printAction( "Avaiting mission screen..." )
         mission_success = False
         for i in range(10):
            time.sleep(int(uniform(1,2)))
            
            out_of_energy = locateTemplate('screens/out_of_energy.png', threshold=0.985, print_coeff=False)
            #printResult(out_of_energy)
            
            mission_started = locateTemplate('screens/mission_bar.png', threshold=0.985)
            #printResult(mission_started)
               
            if out_of_energy:
               print( '' )
               printAction("No energy left! Exiting.", newline=True)
               back_key()
               
#               if statistics:
#                  stats.silverEnd("mission_%d-%d"%mission_number)
               
               return True
               
            if mission_started:
               print( '' )
               printAction("Mission started. Returning.", newline=True)
               time.sleep(1)
               back_key()
               time.sleep(int(uniform(1,2)))
               mission_success = True
               
#               if statistics:
#                  stats.add("mission_%d-%d"%mission_number, 1)
                  
               break
         
         if not mission_success:
            printAction("Timeout when waiting for mission screen", newline=True)
#            if statistics:
#               stats.silverEnd("mission_%d-%d"%mission_number)
            return False

def start_marvel(user):
   
   def attempt_start(user):
      unlock_phone()
      clear_marvel_cache()
      launch_marvel()
      check_if_vnc_error()
      #printAction("Searching for
      printAction("Searching for login screen...")
      login_screen_coords = locateTemplate('screens/login_screen.png', threshold=0.95, retries=25, interval=1)
      printResult(login_screen_coords)
      if login_screen_coords:
         adb_login( login_screen_coords, user )
   
      printAction("Searching for home screen...")
      login_success = False
      for i in range(35):
         time.sleep(1)
         if locateTemplate('screens/home_screen.png', threshold=0.95):
            #time.sleep(1)
            left_click((346,551)) # kills ads
            time.sleep(4)
            
            left_click((346,551)) # kills ads
            login_success = True
            break
         
      if not login_success:
         if locateTemplate('screens/home_screen_maintenance.png'):
            printAction("It appears server is under maintenance...", newline=True)
      
#      if login_success:
#         printAction( "Finished login success!!", newline=True)
#      else: 
#         printAction( "login FAILED!!!", newline=True)
#        
      printResult(login_success) 
      return login_success
      
         
   all_ok = False
   for i in range(3):
      print( '' )
      print("Login attempt %d on account %s..."%(i,user))
      login_ok = attempt_start(user)
      if login_ok:
         all_ok = True
         break
      
   return all_ok
   # adb catlog
   
def start_marvel_joinge():
   return start_marvel('JoInge')
   
def start_marvel_jollyma():
   return start_marvel('JollyMa')
   
def start_marvel_jojanr():
   return start_marvel('JoJanR')
   
def exitMarvel():
   check_if_vnc_error()
   
   Popen("adb shell am force-stop com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android", stdout=PIPE, shell=True).stdout.read()
   
#   clear_marvel_cache() # A little harsh...?
   lock_phone()
   check_if_vnc_error()
   
def lock_wait_unlock():
   lock_phone()
   #time.sleep(60*int(uniform(15,25)))
   time.sleep(60)
   
   unlock_phone()

def sellAllCards(cards_list, alignment='all'):
   
   for i in range(10):
      if not sellCards(cards_list, alignment):
         return
      
def fuseAllCards(card_type, alignment='all'):
   
   for i in range(10):
      if not fuseCard(card_type, alignment):
         return
   
def fuseAndBoost(card_type, cards_list, fuse_alignment='all', boost_alignment='all'):
   
   for i in range(10):
      if fuseCard(card_type=card_type, alignment=fuse_alignment):
         boostCard( card_name=card_type, cards_list=cards_list, alignment=boost_alignment )
      else:
         return
   
   
#def test():
#   info = getMyPageStatus()
#   roster_count, roster_capacity = info['roster']
#   
#   print(roster_count)
#   if not roster_count or roster_count > 60:
#      printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
#      sellAllCards(['common_thing','common_blackcat','common_spiderwoman','common_sandman'])


def farmMission24FuseAndBoost():

   play_mission((2,4), 50)
      
   fuseAndBoost('uncommon_ironman',
                ['common_thing','common_blackcat','common_spiderwoman','common_sandman'],
                fuse_alignment='tactics')
   
   try:
      info = getMyPageStatus()
      roster_count, roster_capacity = info['roster']
      
      if not roster_count or roster_count > 60:
         printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
         sellAllCards(['common_thing','common_blackcat','common_spiderwoman','common_sandman'])
   except:
      pass
   
def farmMission24FuseAndSell():

   play_mission((2,4), 50)
   
   fuseAllCards('uncommon_ironman', 'tactics')
      
   sellAllCards(all_common_cards)   
         
   try:
      info = getMyPageStatus()
      roster_count, roster_capacity = info['roster']
      
      if not roster_count or roster_count > 60:
         printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
   except:
      pass
   
   printNotify("Done processing this player!!!")
#   info = getMyPageStatus()
#   roster_count, roster_capacity = info['roster']
#   
#   if not roster_count or roster_count > 50:
#      printAction("Roster exceeds 30 cards. Sell and fuse baby!!!", newline=True)
#      sellAllCards(all_common_cards)
#      fuseAllCards('uncommon_ironman', 'tactics')
      
def getSilver():
   
   play_mission((4,3), 2*23)
   
   time.sleep(.5)
   info = getMyPageStatus()
   
   roster_count, roster_capacity = info['roster']
   
   if not roster_count or roster_count > 55:
      printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
      sellAllCards(['common_medusa', 'common_enchantress'])
      
def farmMission32():

   play_mission((3,2), 40)
   
   fuseAndBoost('uncommon_ironman',
                ['common_thing','common_blackcat','common_spiderwoman','common_sandman'],
                fuse_alignment='tactics')
   
   try:
      info = getMyPageStatus()
      roster_count, roster_capacity = info['roster']
      
      if not roster_count or roster_count > 55:
         printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
         sellAllCards(['common_thing','common_blackcat','common_spiderwoman','common_sandman'])
   except:
      pass
   
   printNotify("Done processing this player!!!")
   

def farmMission32FuseAndBoost():

   play_mission((3,2), 50)
      
   fuseAndBoost('uncommon_ironman',
                ['common_thing','common_blackcat','common_spiderwoman','common_sandman'],
                fuse_alignment='tactics')
   
   try:
      info = getMyPageStatus()
      roster_count, roster_capacity = info['roster']
      
      if not roster_count or roster_count > 60:
         printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
         sellAllCards(['common_thing','common_blackcat','common_spiderwoman','common_sandman'])
   except:
      pass
   
#   info = getMyPageStatus()
#   roster_count, roster_capacity = info['roster']
#   
#   if not roster_count or roster_count > 50:
#      printAction("Roster exceeds 30 cards. Sell and fuse baby!!!", newline=True)
#      sellAllCards(all_common_cards)
#      fuseAllCards('uncommon_ironman', 'tactics')

   
#   sellAllCards(['common_spiderwoman','common_sandman'])
#   fuseAllCards('common_ironman')
#   

#recently_launched = ['joinge', 'jojanr':0, 'jollyma':0]
#users = ['JoInge', 'JoJanR', 'JollyMa']
recently_launched = [0]*accounts.__len__()
#
def getIndex(user):
   for i,usr in enumerate(accounts):
      if accounts.keys()[i] == user:
         return i
   return -1

def randomUserStart(user_list=accounts.keys()):
     
   global recently_launched
   
   need_reset = True
   for user in user_list:
      if recently_launched[getIndex(user)] == 0:
         need_reset = False
         break
         
   if need_reset:
      for user in user_list:
         recently_launched[getIndex(user)] = 0
         
   while True:
      i = int(uniform(0,user_list.__len__()-0.000001))
      if recently_launched[getIndex(user_list[i])] == 0:
         recently_launched[getIndex(user_list[i])] = 1
         return start_marvel(user_list[i])
   
   
def runAll24():
   while True:
      for i in accounts.keys():
         try:
            if randomUserStart():
               farmMission24FuseAndBoost()
               exitMarvel()
         except:
            pass
         time.sleep(3*60)
      
def runAll32():
   while True:
      for i in accounts.keys():
         try:
            if randomUserStart():
               farmMission32()
               exitMarvel()
         except:
            pass
         time.sleep(3*60)
      #time.sleep(60*uniform(5,15))

               
         
def runAll43():
   while True:
      for i in accounts.keys():
         try:
            if randomUserStart():
               play_mission((4,3), 2*23)
               exitMarvel()
         except:
            pass
         time.sleep(60*uniform(1,5))
         
      time.sleep(60*uniform(35,55))
   
      
def blockUntilQuit():
   
   print("Waiting until game is killed.")
   time.sleep(3)
   while True:
      if not re.findall('MARVEL',Popen('adb shell ps', shell=True, stdout=PIPE).stdout.read()):
         break
      time.sleep(3)
   print("Game was killed. Moving on...")
      
def startAndRestartWhenQuit():
   

   for i in accounts.keys():
      randomUserStart()
         
      while True:
         if not re.findall('MARVEL',Popen('adb shell ps', shell=True, stdout=PIPE).stdout.read()):
            break

         time.sleep(2)
         
def adjustBrightness(percent=10):
   
   Popen("adb shell echo 'echo %d > /sys/devices/platform/samsung-pd.2/s3cfb.0/spi_gpio.3/spi_master/spi3/spi3.0/backlight/panel/brightness' \| su"%percent, stdout=PIPE, shell=True).stdout.read()
      
         
def sleepToCharge(preferred=60):
   
   
   output = Popen("adb shell cat /sys/class/power_supply/battery/capacity", stdout=PIPE, shell=True).stdout.read()
   had_to_rest = False
   while int(output) < 50:
      if not had_to_rest:
#         lock_phone()
         print("BATTERY below 20\%. Need to sleep for a bit.")
         had_to_rest = True
         
      output = Popen("adb shell cat /sys/class/power_supply/battery/capacity", stdout=PIPE, shell=True).stdout.read()         
      time.sleep(60)

#   if had_to_rest:
#      unlock_phone()
      
   time.sleep(preferred)
   
def cyclePlayers():

   adjustBrightness()
   while True:
      for i in accounts.keys():
         try:
            if randomUserStart():
               notify()
               blockUntilQuit()
               exitMarvel()
         except:
            pass
         
         
def checkTraining():
   
   while( True ):
      gotoMyPage()
      time.sleep(2)
      ref = locateTemplate('screens/training_searching_text.png', threshold=0.95, interval=1)
      printResult(ref)
      
      if not ref:
         break
      
      time.sleep(1)
      
   notify()

            
def custom1():
   
   i = 0
   while True:
           
      
      try:
         if start_marvel_jojanr():
            play_mission((3,2), 2*23)
            exitMarvel()
      except:
         pass
      
      time.sleep(uniform(1,5))
                
      try:
         if start_marvel_joinge():
            play_mission((3,2), 2*23)
            exitMarvel()
      except:
         pass
      
      time.sleep(uniform(1,5)) 
         
      try:
         if start_marvel_jollyma():
            play_mission((3,2), 2*23)
            exitMarvel()
      except:
         pass
      
      time.sleep(60*uniform(35,55))
      
def custom2():
   
   i = 0
   while True:


      try:
         if start_marvel_joinge():
            play_mission((4,3), 2*23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      

      time.sleep(60*uniform(1,3)) 

      try:
         if start_marvel_jojanr():
            play_mission((4,3), 2*23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      

      time.sleep(60*uniform(1,3)) 
      
      try:
         if start_marvel_jollyma():
            play_mission((4,3), 2*23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60*uniform(1,3))
      
def custom3():
   
   i = 0
   while True:

      try:
         if start_marvel_joinge():
            eventPlay()
            play_mission((3,2), 2*23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60*uniform(1,3)) 

      try:
         if start_marvel_jollyma():
            eventPlay()
            play_mission((3,2), 2*23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60*uniform(1,3)) 
      
      try:
         if start_marvel_jojanr():
            eventPlay()
            play_mission((3,2), 2*23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60*uniform(1,10))

def custom4():
   
   i = 0
   while True:

      try:
         if start_marvel_joinge():
            play_mission((3,2), 2*23)
            notify()
            blockUntilQuit()
      except:
         pass
      
      time.sleep(60*uniform(1,3)) 
      
      try:
         if start_marvel_jojanr():
            eventPlay()
            play_mission((3,2), 2*23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60*uniform(1,3)) 
      
      try:
         if start_marvel_jollyma():
            eventPlay()
            play_mission((3,2), 2*23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60*uniform(1,3))
      
def custom5():

   adjustBrightness()
   while True:
      for i in accounts.keys():
         try:
            if start_marvel(i):
               farmMission24FuseAndBoost()
               exitMarvel()
         except:
            pass
         sleepToCharge(60)
         

def custom6():

   adjustBrightness()
   while True:
      for i in accounts.keys():
            if i=='JoInge' or i=='JollyMa' or i=='JoJanR':
               try:
                  if randomUserStart(['JoInge','JollyMa','JoJanR']):
                     farmMission24FuseAndBoost()
                     exitMarvel()
               except:
                  pass
               sleepToCharge(60)
               
      for i in accounts.keys():
            if i=='l33tdump' or i=='Rolfy86' or i=='kinemb86' or i=='MonaBB86':
               try:
                  if randomUserStart(['l33tdump','Rolfy86','kinemb86','MonaBB86']):
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except:
                  pass
               sleepToCharge(60)
      
      
def custom6b():

   adjustBrightness()
   while True:
      for i in accounts.keys():
            if i=='JoInge' or i=='JollyMa' or i=='JoJanR':
               try:
                  if randomUserStart(['JoInge','JollyMa','JoJanR']):
                     farmMission24FuseAndBoost()
                     notify()
                     blockUntilQuit()
                     exitMarvel()
               except:
                  pass
               sleepToCharge(60)
               
      for i in accounts.keys():
            if i=='l33tdump' or i=='Rolfy86' or i=='kinemb86' or i=='MonaBB86':
               try:
                  if randomUserStart(['l33tdump','Rolfy86','kinemb86','MonaBB86']):
                     farmMission32FuseAndBoost()
                     notify()
                     time.sleep(30)
#                     blockUntilQuit()
                     exitMarvel()
               except:
                  pass
               sleepToCharge(60)
      
def custom7(start_end=False):

   adjustBrightness()
   while True:
      if not start_end:
         for i in accounts.keys():
            if i== 'JoInge' or i=='JollyMa' or i=='JoJanR':
               try:
                  if randomUserStart(['JoInge','JollyMa','JoJanR']):
                     farmMission24FuseAndBoost()
                     
                     exitMarvel()
               except:
                  pass
               sleepToCharge(60)
         
      for i in accounts.keys():
         if i == 'l33tdump' or i=='Rolfy86' or i=='kinemb86' or i=='MonaBB86':
            try:
               if randomUserStart(['l33tdump','Rolfy86','kinemb86','MonaBB86']):
                  farmMission24FuseAndSell()
                  exitMarvel()
            except:
               pass
            sleepToCharge(60)

   

def event1(start_end=False):

   adjustBrightness()
   while True:
      if not start_end:
         for i in accounts.keys():
            if i== 'JoInge' or i=='JollyMa' or i=='JoJanR':
               try:
                  if randomUserStart(['JoInge','JollyMa','JoJanR']):
                     farmMission32()                
                     exitMarvel()
               except:
                  pass
               sleepToCharge(60)
         
      for i in accounts.keys():
         if i == 'l33tdump' or i=='Rolfy86' or i=='kinemb86' or i=='MonaBB86':
            try:
               if randomUserStart(['l33tdump','Rolfy86','kinemb86','MonaBB86']):
                  playNewestMission()
#                  farmMission32()
                  exitMarvel()
            except:
               pass
            sleepToCharge(60)
            
            
#            card_ssr+_thing_stoneskin.png


def event2(start_end=False):

   trade_list = ['ssr+_thing_stoneskin',
                 'sr+_spiderwoman_doublelife',
                 'sr+_spiderwoman_doublelife',
                 'sr+_spiderwoman_doublelife',
                 'sr+_spiderwoman_doublelife']

   adjustBrightness()
   while True:
      try:
         if start_marvel_joinge():
            printNotify('Complete trade and event.', 60*30)
#            tradeCards(receiver='jollyma', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
           
      try:
         if start_marvel_jollyma():
            printNotify('Complete trade and event.', 60*30)
            tradeCards(receiver='l33tdump', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      try:
         if start_marvel('l33tdump'):
            printNotify('Complete trade and event.', 60*30)
            tradeCards(receiver='Rolfy86', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      try:
         if start_marvel('Rolfy86'):
            printNotify('Complete trade and event.', 60*30)
            tradeCards(receiver='kinemb86', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      try:
         if start_marvel('kinemb86'):
            printNotify('Complete trade and event.', 60*30)
            tradeCards(receiver='MonaBB86', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      try:
         if start_marvel('MonaBB86'):
            printNotify('Complete trade and event.', 60*30)
            tradeCards(receiver='jojanr', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      try:
         if start_marvel_jojanr():
            printNotify('Complete trade and event.', 60*30)
            tradeCards(receiver='joinge', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)

def event3(start_end=False):

   trade_list = ['ssr+_thing_stoneskin',
                 'sr+_spiderwoman_doublelife',
                 'sr+_spiderwoman_doublelife',
                 'sr+_spiderwoman_doublelife',
                 'sr+_spiderwoman_doublelife']

   adjustBrightness()
   while True:
      try:
         if start_marvel_joinge():
            printNotify('Complete trade and event.', 60*30)
            tradeCards(receiver='jollyma', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
           
      try:
         if start_marvel_jollyma():
            printNotify('Complete trade and event.', 60*30)
            tradeCards(receiver='jojanr', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
           
      try:
         if start_marvel_jojanr():
            printNotify('Complete trade and event.', 60*30)
            tradeCards(receiver='joinge', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)

if __name__ == "__main__":

#   start_marvel('JoInge')
#   import gui.gui as gui
#   gui.main()

#   fuseAndBoost('uncommon_ironman',
#                ['common_thing','common_blackcat','common_spiderwoman','common_sandman'],
#                fuse_alignment='tactics')
#   fuseCard('uncommon_ironman', alignment='tactics')
#   test()
#   tradeCards(receiver='jollyma', cards_list=['rare+_ironman'], alignment='all')
#   tradeCards(receiver='jollyma', cards_list=['ssr+_thing_stoneskin', 'sr+_spiderwoman_doublelife', 'sr+_spiderwoman_doublelife', 'sr+_spiderwoman_doublelife', 'sr+_spiderwoman_doublelife'], alignment='all')

#   selectCard('rare+_ironman', alignment='all')
#   event1()
#   test()
   custom6()
#   runAll32()
#   custom4()
#   play_mission((3,2))
#   eventKillEnemies()
#   eventFindEnemy()
#   eventPlayMission()
#   runAll()
#   startAndRestartWhenQuit()
#   getMyPageStatus()
#   farmMission24FuseAndBoost()
#   replay_all_macros()
#   getIMEI() 
#   replay_all_macros()
#   find_mission()
#   fuse_ironman()
   #pass

   
   #import sys
   #import select
   #import termios
   #import tty

   #def getkey():
      #old_settings = termios.tcgetattr(sys.stdin)
      #tty.setraw(sys.stdin.fileno())
      #select.select([sys.stdin], [], [], 0)
      #answer = sys.stdin.read(1)
      #termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
      #return answer

   #print "Menu\
   #1) Say Foo\
   #2) Say Bar"

   #answer=getkey()

   #if "1" in answer: print "foo"
   #elif "2" in answer: print "bar"
