#cnee --record --events-to-record -1 --mouse --keyboard -o /tmp/xnee.xns -e /tmp/xnee.log -v

#cnee --record --seconds-to-record 150 --mouse --keyboard -o joinge.xns -e joinge.log -v


from __future__ import print_function
from random import uniform
from subprocess import Popen, PIPE
import numpy as np
import re, time, os, sys, ast, select
import cv2

ACTIVE_DEVICE = ''
ADB_ACTIVE_DEVICE = ''
YOUWAVE = False
# STDOUT_ALTERNATIVE = None
ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
abc = 'abcdefghijklmnopqrstuvwxyz'

SCREEN_PATH = './screens'
TEMP_PATH   = './tmp'

try:    os.mkdir(TEMP_PATH)
except: pass

if os.name == "posix":
   ESC = "\\"
elif os.name == "nt":
   ESC = "^"
else:
   print("WARNING: Unsupported OS")
   ESC = "\\"

devnull = open(os.devnull,'w')

# Bootlist:
#
# Valhalla25, airman54, nashie88, waygrumpy, xzitrempire(35), xQueenJenniecx, choiiflames, jonathanxxx, 
#
#
#http://www.neoseeker.com/forums/59268/t1810708-card-skilling-forumla/#9

# RarityDifferencevalue / 4 * (1+feeder_skill_level) * (1/TargetSkillLevel)

#
#The rarity difference values
#
#If the feeder card is:
#2 rarities higher - 160
#1 rarity high - 80
#Same rarity - 60
#1 rarity lower - 40
#2 rarities lower - 24
#3 rarities lower - 16
#4 rarities lower - 2

# Windows build:
#
# py2exe
# Inno Setup
# or
# pylunch

def10 = ['trcoba3', 'trcoba4', 'jabronii', 'Athena2317', 'Lyn3tte', 'Y0liis', 'goma7777', 'Jumpymcspasm', 'Solvicious',
         'Fragment08', 'Hirkyflobble', 'deathsxwill', 'Drimdal', 'erictt 55',
         'Deepblue4550', 'Primo911', 'Monito5',
         'Bigpapi11239899', 'Shanefearn', 'Badbadhorse', 'Quachrtq',
         'Gibsupsup1', 'cintax33', 'jclen11', 'lemi28']

timeout = 90 # minutes
ip = "10.0.0.15"

PAD = 60
all_feeder_cards = [
'common_spiderwoman',
'common_sandman',
'common_beast',
'common_blackcat',
'common_blackpanther',
'common_bullseye',
'common_enchantress',
'common_falcon',
'common_iceman',
'common_invisiblewoman',
'common_kingpin',
'common_medusa',
'common_mockingbird',
'common_mrfantastic',
'common_psylocke',
'common_sif',
'common_thing',
'common_valkyrie',
'common_vision',
'common_vulture'
]

sell_cards = ['common_mrfantastic']

class Stats:
   def __init__(self):
      self.info = {}
      self.read()
      
   def setReference(self, key, val):

      self.info[key + "_ref"] = val
      
   def clearReference(self, key):
      
      self.info[key + "_ref"] = 0
      
   def getReference(self, key):
      
      if key + "_ref" in self.info:
         return self.info[key + "_ref"]
      else:
         return None
      
   def add(self, key, val):
      
      try:
         relative_val = val - self.info[key + "_ref"]
      except:
         relative_val = val
           
      if key in self.info:
         self.info[key] = self.info[key] + relative_val
      else:
         self.info[key] = relative_val
                  
      self.write()
      
      
   def read(self):
      
      try:
         s = open('stats.txt', 'r')
         if os.path.getsize('stats.txt') > 0:
            self.info = ast.literal_eval(s.read())
            s.close()
      except:
         print("ERROR: Unable to open stats.txt")
      
#      if os.path.getsize('stats.txt') > 0:
#         s = open('stats.txt','a')
          
   
   def write(self):
      s = open('stats.txt', 'w')
      s.write(str(self.info))
      s.close()
      
   def silverStart(self, key):

      ref = self.getReference(key + '_silver')
      if not ref:
         info = getMyPageStatus()
         try:
            silver_start = info['silver']
            self.setReference(key + '_silver', silver_start)
         except:
            printAction("WARNING: Unable to read silver status for statistics...", newline=True)
      
   def silverEnd(self, key):
      
      info = getMyPageStatus()
      
      try:
         silver_end = info['silver']
         self.add(key + '_silver', silver_end)
         self.clearReference(key + '_silver')       
         self.write()

      except:
         printAction("WARNING: Unable to read silver status for statistics...", newline=True)
 
class Device():
   def __init__(self):
      pass

   def getInfo(self,key):
      
      for i in range(2):
         try:
            if getattr(self,key):
               return getattr(self,key)
               break
         except:
            self.updateInfo()
      
      return None
         
   def updateInfo(self):
      
      global YOUWAVE
      # First we need to know if we are running an emulator.
      uname = Popen('adb %s shell uname -m' %ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
      
      if re.search('i686',uname):
         YOUWAVE = True
      else:
         YOUWAVE = False
         
      if YOUWAVE:
         
#          thread = RunUntilTimeout(Popen,1,'adb %s shell getevent > tmp.txt' %ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True)
#          thread.start()
#          thread.join()
#          time.sleep(2)
#          
#          event_devices = open('tmp.txt','r').read()
         Popen('adb %s push getevent /sdcard/' %ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
         event_devices = Popen('adb %s shell sh /sdcard/getevent' %ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()    
#          time.sleep(3)
#          event_devices = open('getevent.txt','r').read()#Popen('adb %s shell getevent > tmp.txt' %ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True)
         try:
            self.eventTablet = int(re.search('/dev/input/event([0-9]).*\n.*VirtualBox USB Tablet',event_devices).group(1))
         except:
            print("ERROR: Unable to parse input/output event touchscreen device")
         try:
            self.eventMouse = int(re.search('/dev/input/event([0-9]).*\n.*ImExPS/2 Generic Explorer Mouse',event_devices).group(1))
         except:
            print("ERROR: Unable to parse input/output event mouse device")
         try:
            self.eventKeyboard = int(re.search('/dev/input/event([0-9]).*\n.*AT Translated Set 2 keyboard',event_devices).group(1))
         except:
            print("ERROR: Unable to parse input/output event keyboard device")
            
            
      try:
         build_prop = Popen('adb %s shell echo "cat /system/build.prop" %s| su'%(ADB_ACTIVE_DEVICE,ESC), stdout=PIPE, shell=True).stdout.read()
         self.screenDensity = int(re.search('[^#]ro\.sf\.lcd_density=([0-9]+)',build_prop).group(1))
         
         if self.screenDensity != 160 and self.screenDensity != 240:
            
            print("")
            print("<<<WARNING>>> ")
            print("A screen density of %d detected. This is NOT SUPPORTED!!!"%self.screenDensity)
            print("")
                        
      except:
         print("ERROR: Unable to parse input/output event devices")
            
      self.printInfo()
            
   def printInfo(self):
      
      print("")
      print("Device info updated. New parameters:")
      if YOUWAVE:
         print("Youwave detected?       YES")
         print("  Device - touchscreen: /dev/input/event%d"%self.eventTablet)
         print("  Device - keyboard:    /dev/input/event%d"%self.eventKeyboard)
         print("  Device - mouse:       /dev/input/event%d"%self.eventMouse)
      else:
         print("Youwave detected?       NO")         
      print("Screen density:         %d"%self.screenDensity)
      print("")
  
#   Popen("adb %s shell echo 'echo %d > /sys/devices/platform/samsung-pd.2/s3cfb.0/spi_gpio.3/spi_master/spi3/spi3.0/backlight/panel/brightness' \| su" % (ADB_ACTIVE_DEVICE, percent), stdout=PIPE, shell=True).stdout.read()

 
class InfoMeta():
   pass
 
# The info object reads itself from the info folder!!! 
class Info(InfoMeta):
   try:
      files = os.listdir('info')
   except:
      os.mkdir('info')
   
   first_run = True
   for file in files:
      
      s = open('info/%s' % file, 'r')
      
      attr_name = re.sub('.txt', '', file)

      if first_run:
         print("Reading Info attributes")
         first_run= False
         
      # Make these settings class variables
      setattr(InfoMeta, attr_name, ast.literal_eval(s.read()))
      s.close()
      
   
   def __init__(self):
      pass
#       self.read()
#      self.adbInfo()
      
   def read(self):

      try:
         files = os.listdir('info')
      except:
         os.mkdir('info')
         return
      
      first_run = True
      for file in files:
         
         s = open('info/%s' % file, 'r')
         
         attr_name = re.sub('.txt', '', file)

         # Only read once
         if not hasattr(Info,attr_name) and first_run:
            print("Reading Info attributes")
         # Make these settings class variables
         setattr(Info, attr_name, ast.literal_eval(s.read()))
         s.close()
         first_run= False
      
#      if os.path.getsize('stats.txt') > 0:
#         s = open('stats.txt','a')

   def write(self):
      
      from pprint import pprint
            
      for key in self.__dict__.keys():
      
         s = open('info/%s.txt' % key, 'w')
         pprint(getattr(Info, key), stream=s)
         s.close()
         

# The user object deals with user info 
class User():
   def __init__(self):
      self.current = 'Blayd'
      
   def setCurrent(self, user):
      
      printAction("Current user:")
      print(user)
      
      self.current = user
      
   def getCurrent(self):
      
      return self.current
      

info = Info() # Ideally, don't use this one directly (long term)
device = Device()
user = User()
      
# IMEI = 358150 04 524460 6
# 35     - British Approvals Board of Telecommunications (all phones)
# 
# 524460 - Serial number
# 6      - Check digit

def getIMEI():
   output = Popen("adb %s shell dumpsys iphonesubinfo | grep Device | sed s/\".*= \"//" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
   print(output)
   return int(output)
#   358150045244606

def sumDigits(number, nsum=0):
   
   if number < 10:
      return nsum + number
   else:
      return nsum + sumDigits(number / 10, number % 10)
   
def sumIMEIDigits(number, nsum=0, even=True):
   """http://en.wikipedia.org/wiki/IMEI#Check_digit_computation"""
   if number < 10:
      return nsum + number
   else:
      if even:
         return nsum + sumIMEIDigits(number / 10, number % 10, not even)
      else:
         return nsum + sumIMEIDigits(number / 10, sumDigits((number % 10) * 2), not even)

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

def updateSource():
   
   # On rsync parameters:
   # https://www.itefix.no/i2/content/bug-cwrsync-throwing-chown-failed
   
   print("Updating source to latest version...")
   
   old_dir = os.getcwd()
   
   # Check if we're in the dist folder
   if re.search('woh_macro',old_dir):
      os.chdir('../sync/bin')
   
   # Otherwise assume we're in the source folder
   else:
      os.chdir('./dist/sync/bin')
      
   IS_DEVELOPER = os.path.exists('../../content')
#    IS_DEVELOPER = False
      
   sync_dir = os.getcwd()
   sync_drive_and_path = os.path.splitdrive(sync_dir)
   sync_drive = sync_drive_and_path[0].lower().replace(':','')
   sync_path_cygwin_style = "/cygdrive/%s"%sync_drive \
                          + sync_drive_and_path[1].replace("\\","/")
   
   server = open('../server.txt','r').read()
         
   # If a local contents folder exists, sync from this one
   if IS_DEVELOPER:
      print("Content directory detected. Assuming developer PC")
      sources = ['%s/../../content/**'%sync_path_cygwin_style,
                 '%s/../../gui/**'%sync_path_cygwin_style]
      #Update contents folder:
      source_files = ['../../../macro.py','../../../gui.py']
      for src in source_files:
         rsync_cmd = 'rsync -e "./ssh -oStrictHostKeyChecking=no" -rtvu %s/%s %s/../../content/'\
                     %(sync_path_cygwin_style,src,sync_path_cygwin_style)
         print(Popen(rsync_cmd, stdout=PIPE, shell=True).stdout.read())
      
   else:
      print("Not content directory detected. Assuming client PC")
      server = open('../server.txt','r').read()
      sources = ['macro@' + server + ':macro/**']
   
   for source in sources:
      rsync_cmd = 'rsync -e "./ssh -oStrictHostKeyChecking=no" -rtvu %s %s/../../woh_macro/'\
                  %(source,sync_path_cygwin_style)
      print(Popen(rsync_cmd, stdout=PIPE, shell=True).stdout.read())

   # If a local contents folder exists, push changes to server
   if IS_DEVELOPER:
      destination = 'macro@' + server + ':macro/'
      sources = ['../../gui/**', '../../content/**']
      for source in sources: 
         rsync_cmd = 'rsync -e "./ssh -oStrictHostKeyChecking=no" -rtvu %s/%s %s'\
                     %(sync_path_cygwin_style,source,destination)
         print(Popen(rsync_cmd, stdout=PIPE, shell=True).stdout.read())


   os.chdir(old_dir)
   

   

baseN = [
"Jax",
"Damon",
"Dexter",
"Axel",
"Cason",
"Titus",
"Kace",
"Maximus",
"Ryker",
"Harley",
"Ajax",
"Zander",
"Zeke",
"Zenon",
"Phoenix",
"Rocco",
"Jett",
"Gunner",
"Pierce",
"Cadmus",
]

emails = [
'gmail.com',
'yahoo.com',
'hotmail.com'
 ]

def getBaseName():
   
# for i in {1..20}; do curl -L http://www.spinxo.com/ | sed -r -n "s/^\s+([a-zA-Z]+)<\/a><\/li>.*$/\1/p" >> data/nick_seeds_joey.txt; done
# cat info/nick_seeds.txt | sort -R > ./info/nick_seeds2.txt

   printAction("Fetching nick seeds...")
   current_nick = user.getCurrent()
   f = open('./data/nick_seeds_%s.txt'%current_nick.lower(), 'r')
   all_names = f.readlines()
   name = all_names[0]
   name = re.sub('\n','',name)
   f.close()
#   lines = re.split("\n+", file)
   f = open('./data/nick_seeds_%s.txt'%current_nick.lower(), 'w')
   f.write( "".join(all_names[1:]) )
   f.close()
   printResult(True)
   
   return name


def createAccount(baseNames=baseN):
   
   endNames = []
   endEmails = []
   endPasswords = []
   
   f = open('new_accounts.txt', 'w')
   e = open('new_emails.txt', 'w')
   
   f.write('{')
   e.write('{')
   
   for i in baseNames:
      
      name = i
      print(i)
      
      randNums = ''.join(np.random.uniform(9, size=int(np.random.uniform(0, 3))).astype(int).astype('str'))
      randABC = ''.join([ABC[0][j] for j in np.random.uniform(0, 26, size=int(np.random.uniform(3))).astype(int)])
      randAbc = ''.join([abc[0][j] for j in np.random.uniform(0, 26, size=int(np.random.uniform(3))).astype(int)])
      
      tmp = [i, randNums, randABC, randAbc]
      tmp2 = [randNums, randABC, randAbc]
      password = ''.join([tmp[j] for j in np.random.uniform(0, 4, size=4).astype(int)])
      email = i + ''.join([tmp2[j] for j in np.random.uniform(0, 3, size=4).astype(int)]) + '@' + emails[int(np.random.uniform(4))]
      name = i + randABC + randAbc + randNums

      f.write("\'%s\':\'%s\',\n" % (name, password))
      e.write("\'%s\':\'%s\',\n" % (name, email))
   
   f.write('}')
   e.write('}')
   
def createNewFakeAccount(referral=""):
      
   name_base  = getBaseName()
   email_base = getBaseName().lower()
   
   old_dir = os.getcwd()
      
   # Set new Android ID and start WoH
   setAndroidId(name_base,newAndroidId())
   unlock_phone()
   clearMarvelCache()
   launch_marvel()
   
   printAction("Searching for login screen...")
   login_screen = locateTemplate('login_screen.png', threshold=0.95, retries=25, interval=1)
   printResult(login_screen)
   
   if login_screen:
      
      randNums = ''.join(np.random.uniform(9, size=int(np.random.uniform(2, 4))).astype(int).astype('str'))
      email = email_base + randNums + '@' + emails[int(np.random.uniform(0,len(emails)-1e-9))]
      
#       randABC = ''.join([ABC[0][j] for j in np.random.uniform(0, 26, size=int(np.random.uniform(3))).astype(int)])
#       randAbc = ''.join([abc[0][j] for j in np.random.uniform(0, 26, size=int(np.random.uniform(3))).astype(int)])
      
      tmp = ['0123456789', ABC, abc]
      tmp2 = ''.join(i for i in tmp)
      password = ''.join([tmp2[j] for j in np.random.uniform(0, len(tmp2)-1e-9, size=int(np.random.uniform(8,14))).astype(int)])
      
      c = np.array(login_screen)
   
      if device.getInfo('screenDensity') != 160:
         print("ERROR: Not implemented")
         return 2
         
      left_click((140, 160) + c) # Login Mobage
      left_click((206, 160) + c) # Login button
      
      
      printAction("Searching for sign up screen...")
      signup_screen = locateTemplate('login_signup.png', threshold=0.95, retries=5, interval=2)
      printResult(signup_screen)
      
      if not signup_screen:
         return 1

      success = False
      c = np.array(signup_screen)
      for i in range(10):
         
         if i!=0:              
            printAction("Wiping both fields...")
            # Wipe both fields:
            left_click((244, 73) + c) # Email field
            if i!=0:
               for i in range(50): backspace()
            left_click((244, 118) + c) # Password field
            if i!=0:
               for i in range(50): backspace()   
         printAction("Trying with email:")
         print(email)
         left_click((244, 73) + c) # Email field
         enter_text(email)
         backspace()
         printAction("Entering password:")
         print(password)
         left_click((244, 118) + c) # Password field
         
         # Like usual Youwave has problems here...
         enter_text('a')
         for i in range(len(email)):
            right_arrow()
         for i in range(len(email) + 2):
            backspace()
         enter_text(password)
         backspace()
         left_click((205, 159) + c) # Signup button
         
         printAction("Searching for \"Last Step\" screen...")
         signup_last_screen = locateTemplate('login_signup_last.png', threshold=0.95, retries=20, interval=1)
         printResult(signup_last_screen)
         
         if signup_last_screen:
            success = True
            break
         
      left_click((20,140) + c) # Uncheck "Get Mobage news and updates" button
            
      # Now we must handle the fact that the nick may be invalid
      success = False
      printAction("Waiting for tutorial start...")
      for i in range(10):
         
         left_click((232,105)+c) # Nick field         

         if i==0:
            enter_text('a')
            for i in range(len(email_base+randNums)+2):
               right_arrow()            

            for i in range(len(email_base+randNums)+2+len(password)):
               backspace()
            enter_text(name_base)
            backspace()
         else:
            enter_text(tmp2[int(np.random.uniform(0, len(tmp2)-1e-9))])
            backspace()            
         
         left_click((142,172) + c) # Save and Play button
         
#          invalid_nick  = locateTemplate('login_signup_invalid_nick.png', threshold=0.95)
         time.sleep(5)
         login_box     = locateTemplate('login_signup_part.png', threshold=0.95)
         
#          if invalid_nick:
#             left_click((232,105)+c) # Nick field
#             enter_text(tmp2[np.random.uniform(0, len(tmp2)-1e-9)])
            
         if not login_box:
            success = True
            break
         
      if not success:
         printResult(False)
         print("ERROR: Unable to enter valid nick")
         return 1

      printResult(True)

      printAction("Running through the tutorial like mad... (!!!)", newline=True)
      OK = [0]*10
      for i in range(200):
         time.sleep(1)
         take_screenshot_adb()
         if   not OK[0] and locateTemplate('mobage_ad.png',               offset=(85,14),  click=True, reuse_last_screenshot=True): OK[0] = 1
         elif not OK[1] and locateTemplate('tutorial_understood.png',     offset=(132,7),  click=True, reuse_last_screenshot=True): OK[1] = 1
         elif not OK[2] and locateTemplate('tutorial_skip.png',           offset=(49,11),  click=True, reuse_last_screenshot=True): OK[2] = 1
         elif not OK[3] and locateTemplate('tutorial_another_card.png',   offset=(132,8),  click=True, reuse_last_screenshot=True): OK[3] = 1
         elif not OK[4] and locateTemplate('tutorial_all_right.png',      offset=(127,10), click=True, reuse_last_screenshot=True): OK[4] = 1
         elif not OK[5] and locateTemplate('tutorial_wreck_villains.png', offset=(123,10), click=True, reuse_last_screenshot=True): OK[5] = 1
         elif not OK[6] and locateTemplate('tutorial_battle.png',         offset=(23,11),  click=True, reuse_last_screenshot=True): OK[6] = 1
         elif not OK[7] and locateTemplate('tutorial_got_this_one.png',   offset=(123,9),  click=True, reuse_last_screenshot=True): OK[7] = 1
         elif not OK[8] and locateTemplate('tutorial_i_will.png',         offset=(128,10), click=True, reuse_last_screenshot=True): OK[8] = 1
         elif not OK[9] and locateTemplate('tutorial_referral.png',       offset=(124,13), click=True, reuse_last_screenshot=True):
            OK[9] = 1
            break
         left_click((240,150))
      printResult(True)
      printAction("Time for referral service BABY!!!", newline=True)
      
      ok = locateTemplate('tutorial_ok.png', offset=(29,11), retries=5, interval=1)
      if not ok:
         printResult(False)
         print("ERROR: Could not find referral \"OK\" button")
         return 2 # If the service gets this far without working, it's probably best to call it off.
      printResult(True)
      printAction("Entering the referral code...", newline=True)
      text_field = ok + np.array((0,-33))
      left_click(text_field)
      
      enter_text('a')
      for i in range(len(name_base)+10):
         right_arrow()            
      for i in range(len(name_base)+5):
         backspace()
      enter_text(referral)
      backspace()
      
      left_click(ok)
      ok2 = locateTemplate('tutorial_almost_finished_ok.png', offset=(92,15), click=True, retries=5, interval=1)
      
      if not ok2:
         print("ERROR: Could not find referral \"OK\" button")
         return 2 # If the service gets this far without working, it's probably best to call it off.
      
      for i in range(5):
         time.sleep(2)
         left_click((240,150))
      
      printAction("Registering device...")
      register_device = locateTemplate('tutorial_register_device.png', offset=(124,11), click=True, retries=5)
      
      if not register_device:
         printResult(False)
         print("ERROR: Unable to find register device button!")
         return 2 # If the service gets this far without working, it's probably best to call it off.
      
      agree = locateTemplate('tutorial_agree.png', offset=(124,11), click=True, retries=5)
      
      if not agree:
         printResult(False)
         print("ERROR: Unable to find register device button!")
         return 2 # If the service gets this far without working, it's probably best to call it off.
      
      locateTemplate('tutorial_mypage.png', offset=(45,8), click=True, retries=3)
      
      printResult(True)
      printAction("FINISHED!!!", newline=True)
      return 0
      
      
def createMultipleNewFakeAccounts(iterations, interval=(3,15), referral=""):
   
   for i in range(iterations):
      
      print("")
      print("REFERRAL SERVICE: Iteration %d"%i)
      
      retcode = createNewFakeAccount(referral=referral)
      printAction("",newline=True)
      printAction("SUMMARY",newline=True)
      if retcode == 2:
         printAction("Referral script asked to abort. Investigate!",newline=True)
         break

      elif retcode == 1:
         printAction("Referral script failed but asked to keep going!",newline=True)
         
      elif retcode == 0:  
         printAction("All good! Ready for more action!",newline=True)
         
      else:
         printAction("WARNING: This return code is unknown",newline=True)
      
      printAction("",newline=True)
      wait_time = np.random.uniform(interval[0]*60,interval[1]*60)
      
      printAction("Waiting for roughly %d minutes and %d seconds..."%(wait_time/60,wait_time%60),newline=True)
      
      time.sleep(wait_time)
      
      
#       for i in range(10):
#          
# 
#    
#    enter_text(user)      
#    
#    if YOUWAVE:
#       backspace()
#       
#    if info.getAdbInfo('screenDensity') == 240:
#       left_click((76, 174) + c) # Mobage password field
#    else:
#       left_click((142, 114) + c) # Mobage password field
#    if YOUWAVE: # Youwave screws this up. Need to insert text, then erase it once
#       enter_text('a')
#       
#       for i in range(len(user)):
#          right_arrow()
# #         time.sleep(0.1)
#          
#       for i in range(len(user) + 2):
#          backspace()
# #         time.sleep(0.1)
#    
#    if password:
#       enter_text(password)
#    else:
#       enter_text(info.accounts[user])
#       
#    if YOUWAVE:
#       backspace()
#       
#    if info.getAdbInfo('screenDensity') == 240:
#       left_click((313, 237) + c) # Login button
#    else:
#       left_click((207, 157) + c) # Login button
#       
#       
# 
#       
#      adb_login(login_screen_coords, user, password)            
      
#      printAction("Searching for home screen...")
#      login_success = False
#      for i in range(35):
#         time.sleep(1)
#         home_screen = locateTemplate('home_screen.png', threshold=0.95)
#            
#         if home_screen:
#            if enable_cache and NEW_USER:
#               os.mkdir('./users/%s' % user)
#               os.mkdir('./users/%s/files' % user)
#               os.mkdir('./users/%s/shared_prefs' % user)
#               
#               print(
#               Popen("adb %s shell \
#                     \" rm -r /sdcard/pull_tmp;\
#                        mkdir /sdcard/pull_tmp;\
#                        mkdir /sdcard/pull_tmp/files;\
#                        mkdir /sdcard/pull_tmp/shared_prefs\";\
#                        %s \
#                     adb %s pull /sdcard/pull_tmp ./users/%s\
#                     " % (ADB_ACTIVE_DEVICE, adb_copy_to_sdcard_cmd, ADB_ACTIVE_DEVICE, user),
#                     stdout=PIPE, shell=True).stdout.read())
#
#            time.sleep(1)
#            ad  = locateTemplate('home_screen_ad.png', offset=(90, 20), threshold=0.95)
#            ad2 = locateTemplate('home_screen_ad2.png', offset=(90, 20), threshold=0.95, reuse_last_screenshot=True)
#            if ad or ad2:
#               if ad:
#                  left_click(ad) # kills ads
#               if ad2:
#                  left_click(ad2) # kills ads
#               time.sleep(1)
#            
##            left_click((346,551)) # kills ads
#            login_success = True
#            break
#   
#   
#   
#   
#   
#   
#   startMarvel(user, password=password)
#   playNewestMission()
#   exitMarvel()
#   time.sleep(60)

#def createAccounts(baseNames=baseN):
#   
#   endNames = []
#   endEmails = []
#   endPasswords = []
#   
#   f = open('new_accounts.txt', 'w')
#   e = open('new_emails.txt', 'w')
#   
#   f.write('{')
#   e.write('{')
#   
#   for i in baseNames:
#      
#      name = i
#      print(i)
#      
#      randNums = ''.join(np.random.uniform(9, size=int(np.random.uniform(0, 3))).astype(int).astype('str'))
#      randABC = ''.join([ABC[0][j] for j in np.random.uniform(0, 26, size=int(np.random.uniform(3))).astype(int)])
#      randAbc = ''.join([abc[0][j] for j in np.random.uniform(0, 26, size=int(np.random.uniform(3))).astype(int)])
#      
#      tmp = [i, randNums, randABC, randAbc]
#      tmp2 = [randNums, randABC, randAbc]
#      password = ''.join([tmp[j] for j in np.random.uniform(0, 4, size=4).astype(int)])
#      email = i + ''.join([tmp2[j] for j in np.random.uniform(0, 3, size=4).astype(int)]) + '@' + emails[int(np.random.uniform(4))]
#      name = i + randABC + randAbc + randNums
#
#      f.write("\'%s\':\'%s\',\n" % (name, password))
#      e.write("\'%s\':\'%s\',\n" % (name, email))
#   
#   f.write('}')
#   e.write('}')

def adbConnect(device):
   
   print("Connecting to: %s..."%device)
   
   output = Popen("adb connect %s"%device, stdout=PIPE, shell=True).stdout.read()

   if re.search("unable|error",output):
      print("ERROR: Unable to connect to: %s"%device)
      return False
   else:
      setActiveDevice(device)
      return True

def adbDevices():

#    devices_string = Popen("adb devices", stdout=PIPE, shell=True)
   
#    time.sleep(3)
#    re.search(r'[0-9]*', old_ids[0]).group(0)
#    cards_in_roster_numbers = re.findall(r'\d+', cards_in_roster_string)
#    cards_in_roster = tuple(map(int, cards_in_roster_numbers))
   
   #devices_string = Popen("adb devices | grep -w device | sed s/device//", stdout=PIPE, shell=True).stdout.read()
   devices_string = Popen("adb devices", stdout=PIPE, shell=True).stdout.read()
   
   devices = re.findall("\n[a-zA-Z0-9\.:]+",devices_string)

#   devices = re.sub("\tdevice\r", '', devices[0])
#   lines = re.split("\n+", devices)
   
   device_list = []
   for device in devices:
      device_list.append(re.sub("\n", '', device))
#      if l != '':
#         device_list.append(l)
         
   return device_list


def setActiveDevice(device_id):
   global ACTIVE_DEVICE
   global ADB_ACTIVE_DEVICE
   global YOUWAVE
   
   if device_id != None:
      windows_friendly_device = re.sub(r':','.',device_id)
      ACTIVE_DEVICE = windows_friendly_device
      ADB_ACTIVE_DEVICE = "-s " + device_id
      
   device.updateInfo()
   

def notify():
   
#   Popen("mplayer audio/ringtones/BentleyDubs.ogg >/dev/null 2>&1", stdout=PIPE, shell=True).stdout.read()
   
   Popen("adb %s shell echo 'echo 100 > /sys/devices/virtual/timed_output/vibrator/enable' \| su" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
   time.sleep(.2)
   Popen("adb %s shell echo 'echo 100 > /sys/devices/virtual/timed_output/vibrator/enable' \| su" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
   time.sleep(.2)
   Popen("adb %s shell echo 'echo 100 > /sys/devices/virtual/timed_output/vibrator/enable' \| su" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
   time.sleep(.2)
   Popen("adb %s shell echo 'echo 100 > /sys/devices/virtual/timed_output/vibrator/enable' \| su" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()

def notifyWork():
   Popen("ssh me@$(curl -L work.joinge.net) \"mplayer /home/me/macro/audio/ringtones/CanisMajor.ogg\" >/dev/null 2>&1", stdout=PIPE, shell=True).stdout.read()
   
###########
# YOUWAVE #
###########

def newAndroidId():
   printAction("Creating new Android ID...", newline=True)
   return ''.join(np.random.uniform(10, size=int(np.random.uniform(15, 18))).astype(int).astype('str'))
   
def setAndroidId(user=None, newid='0' * 15):
   
   printAction("Setting Android ID...")
   out = Popen("adb %s shell \
               \"cat /data/youwave_id;\
                 cat /sdcard/Id\"" % ADB_ACTIVE_DEVICE,
               stdout=PIPE, shell=True).stdout.read()
#    print(out)
   old_ids = out.split('\n')
   if not old_ids[0] == old_ids[1]:
      print("WARNING: IDs in /data (%s) and /sdcard (%s) do not match!!!" % (old_ids[0], old_ids[1]))
      
   old_id = re.search(r'[0-9]*', old_ids[0]).group(0) #15-18
   
   if not user == None:

      try:
         if old_id == newid:
            print('WARNING: saveAndroidId() - Ids are already the same.')
         else:
            if newid == '0' * 15:
               newid = info.fakeID[user]
               
            print("Old ID: %s, New ID: %s"%(old_id,newid))
            Popen('adb %s shell echo "echo %s > /data/youwave_id" %s| su' % (ADB_ACTIVE_DEVICE, newid, ESC), stdout=PIPE, shell=True).stdout.read()
            Popen('adb %s shell echo "echo %s > /sdcard/Id" %s| su' % (ADB_ACTIVE_DEVICE, newid, ESC), stdout=PIPE, shell=True).stdout.read()
            
            info.fakeID[user] = newid

            info.write()
      except:
         print("ERROR: User %s does not seem to exist!" % user)

   else:
      print("Old ID: %s, New ID: %s"%(old_id,newid))
      Popen("adb %s shell echo 'echo %s > /data/youwave_id' %s| su" % (ADB_ACTIVE_DEVICE, newid, ESC), stdout=PIPE, shell=True).stdout.read()
      Popen("adb %s shell echo 'echo %s > /sdcard/Id' %s| su" % (ADB_ACTIVE_DEVICE, newid, ESC), stdout=PIPE, shell=True).stdout.read()


def getAndroidId(user=None):
   
   out = Popen("adb %s shell \
               \"cat /data/youwave_id;\
                 cat /sdcard/Id\"" % ADB_ACTIVE_DEVICE,
               stdout=PIPE, shell=True).stdout.read()
   print(out)
   id = out.split('\n')
   if id[0] == id[1]:
      id_clean = re.search(r'[0-9]*', id[0]).group(0) #15-18
      
      if not user == None:
         info.fakeAccounts[user] = id_clean
         info.write()
      else:
         print(id_clean)
   else:
      print("WARNING: IDs in /data and /sdcard do not match!!!")
#   out.communicate()



def exitMarvel():
   check_if_vnc_error()
   
   Popen("adb %s shell am force-stop com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()

def printResult(res):
      
   if res:
      sys.stdout.write(":)")
   else:
      sys.stdout.write(":s")
      
   sys.stdout.flush()
   sys.stdout.write("\n")

def printAction(str, res=None, newline=False):
   string = "   %s" % str
      
   if newline:
      sys.stdout.write(string.ljust(PAD, ' '))
      sys.stdout.flush()
      sys.stdout.write("\n")
   else:
      sys.stdout.write(string.ljust(PAD, ' '))
      sys.stdout.flush()
   if res:
      printResult(res)
      
def printNotify(message, timeout=30):
   print("NOTIFICATION: " + message)
   notify()
   print("Type Enter to continue (will do so anyways in 30s)")
   
   select.select([sys.stdin], [], [], timeout)
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
   
   if Popen("adb devices | grep %s" % ip, stdout=PIPE, shell=True).returncode == None:
      macro_output = Popen("adb connect %s" % ip, stdout=PIPE, shell=True).stdout.read()
      if macro_output == None:
         return False
      else:
         return True
   else:
      return True
   #if macro_output == None:
   #   raise Exception("Unable to connect adb to wifi")  
   
      
def clearMarvelCache():
   printAction("Clearing Marvel cache...", newline=True)
   macro_output = Popen("adb %s shell pm clear com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android 2>>error.log" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
   time.sleep(3)

   #if macro_output == None:
   #   raise Exception("Unable to clear Marvel cache")

def launch_marvel():
   macro_output = Popen("adb %s shell am start -n com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android/.SplashActivity 2>>error.log" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
   #if macro_output == None:
   #   raise Exception("Unable to start Marvel")

#def adb_shell(strings):
#
#   for string in strings:
      

def adb_input(text):
   macro_output = Popen("adb %s shell input text %s 2>>error.log" % (ADB_ACTIVE_DEVICE, text), stdout=PIPE, shell=True).stdout.read()

def adb_event_batch(events):
   
   sendevent_string = ''
   for i, event in enumerate(events):
      if i != 0:
         sendevent_string += '; '
         
      sendevent_string += "sendevent /dev/input/event%d %d %d %d" % event
        
   Popen("adb %s shell \"%s\" 2>>error.log" % (ADB_ACTIVE_DEVICE, sendevent_string), stdout=PIPE, shell=True).stdout.read()
      
#   print( "adb shell %s"%sendevent_string )
      

def adb_event(event_no=2, a=None, b=None , c=None):
   """Event number: 1 - hardware key (home?)
                    2 - touch
                        0003 2f - ABS_MT_SLOT           : value 0, min 0, max 9, fuzz 0, flat 0, resolution 0
                        0003 30 - ABS_MT_TOUCH_MAJOR    : value 0, min 0, max 255, fuzz 0, flat 0, resolution 0
                        0003 35 - ABS_MT_POSITION_X     : value 0, min 0, max 479, fuzz 0, flat 0, resolution 0
                        0003 36 - ABS_MT_POSITION_Y     : value 0, min 0, max 799, fuzz 0, flat 0, resolution 0
                        0003 39 - ABS_MT_TRACKING_ID    : value 0, min 0, max 65535, fuzz 0, flat 0, resolution 0
                        0003 3a - ABS_MT_PRESSURE       : value 0, min 0, max 30, fuzz 0, flat 0, resolution 0
   """
   
   macro_output = Popen("adb %s shell sendevent /dev/input/event%d %d %d %d" % (ADB_ACTIVE_DEVICE, event_no, a, b, c), stdout=PIPE, shell=True).stdout.read()
#   time.sleep(0.5)  
   #adbSend("/dev/input/event2",3,48,10);
   
def left_click(loc):
    
   global YOUWAVE
#   adb_event( 2, 0x0003, 0x0039, 0x00000d45 )
#   adb_event( 2, 0x0003, 0x0035, loc[0] )
#   adb_event( 2, 0x0003, 0x0036, loc[1] )
#   adb_event( 2, 0x0003, 0x0030, 0x00000032 )
#   adb_event( 2, 0x0003, 0x003a, 0x00000002 )
#   adb_event( 2, 0x0000, 0x0000, 0x00000000 )
#   adb_event( 2, 0x0003, 0x0039, 0xffffffff )
#   adb_event( 2, 0x0000, 0x0000, 0x00000000 )

   # TODO: use input tap x y
   
   
   if not YOUWAVE:
      adb_event_batch([
         (2, 0x0003, 0x0039, 0x00000d45),
         (2, 0x0003, 0x0035, loc[0]),
         (2, 0x0003, 0x0036, loc[1]),
         (2, 0x0003, 0x0030, 0x00000032),
         (2, 0x0003, 0x003a, 0x00000002),
         (2, 0x0000, 0x0000, 0x00000000),
         (2, 0x0003, 0x0039, 0xffffffff),
         (2, 0x0000, 0x0000, 0x00000000)
         ])
   
   else:
      
      if device.getInfo('eventTablet'):
         event_no = device.eventTablet
      else:
         event_no = 3
                 
  
      adb_event_batch([
         (event_no, 0x0004, 0x0004, 0x00090001),
         (event_no, 0x0001, 0x0110, 0x00000001),
         (event_no, 0x0003, 0x0000, int(loc[0] * 2 ** 15 / 480.0)),
         (event_no, 0x0003, 0x0001, int(loc[1] * 2 ** 15 / 640.0)),
         (event_no, 0x0000, 0x0000, 0x00000000),
         (event_no, 0x0004, 0x0004, 0x00090001),
         (event_no, 0x0001, 0x0110, 0x00000000),
         (event_no, 0x0000, 0x0000, 0x00000000)
         ])
      time.sleep(0.2)

def backspace():
   

   if YOUWAVE:
      if device.getInfo('eventKeyboard'):
         event_no = device.eventKeyboard
      else:
         event_no = 2
      
      adb_event_batch([
         (event_no, 0x0004, 0x0004, 0x0000000e),
         (event_no, 0x0001, 0x000e, 0x00000001),
         (event_no, 0x0000, 0x0000, 0x00000000),
         (event_no, 0x0004, 0x0004, 0x0000000e),
         (event_no, 0x0001, 0x000e, 0x00000000),
         (event_no, 0x0000, 0x0000, 0x00000000)
         ])     

   else:
      print("ERROR: backspace() is not implemented for regular phones")     
     
def right_arrow():

   if YOUWAVE:
      if device.getInfo('eventKeyboard'):
         event_no = device.eventKeyboard
      else:
         event_no = 2
      
      adb_event_batch([
         (event_no, 0x0004, 0x0004, 0x000000cd),
         (event_no, 0x0001, 0x006a, 0x00000001),
         (event_no, 0x0000, 0x0000, 0x00000000),
         (event_no, 0x0004, 0x0004, 0x000000cd),
         (event_no, 0x0001, 0x006a, 0x00000000),
         (event_no, 0x0000, 0x0000, 0x00000000)
         ])     

   else:
      print("ERROR: right_arrow() is not implemented for regular phones")   
       
   
def enter_text(text):
   adb_input(text)
  

def adb_login(login_screen_coords, user, password=None):
   
   c = np.array(login_screen_coords)
   
   if device.getInfo('screenDensity') == 240:
      left_click((205, 254) + c) # Login Mobage
      left_click((106, 255) + c) # Login button
      left_click((76, 108) + c) # Mobage name field
   else:
      left_click((140, 160) + c) # Login Mobage
      left_click((74, 160) + c) # Login button
      left_click((144, 71) + c) # Mobage name field
   
   enter_text(user)      
   
   if YOUWAVE:
      backspace()
      
   if device.getInfo('screenDensity') == 240:
      left_click((76, 174) + c) # Mobage password field
   else:
      left_click((142, 114) + c) # Mobage password field
   if YOUWAVE: # Youwave screws this up. Need to insert text, then erase it once
      enter_text('a')
      
      for i in range(len(user)):
         right_arrow()
#         time.sleep(0.1)
         
      for i in range(len(user) + 2):
         backspace()
#         time.sleep(0.1)
   
   if password:
      enter_text(password)
   else:
      enter_text(info.accounts[user])
      
   if YOUWAVE:
      backspace()
      
   if device.getInfo('screenDensity') == 240:
      left_click((313, 237) + c) # Login button
   else:
      left_click((207, 157) + c) # Login button
#   
def home_key():
   
   adb_event(1, 0x0001, 0x0066, 0x00000001)
   adb_event(1, 0x0000, 0x0000, 0x00000000)
   adb_event(1, 0x0001, 0x0066, 0x00000000)
   adb_event(1, 0x0000, 0x0000, 0x00000000)

def power_key():
   
   adb_event(1, 0x0001, 0x0074, 0x00000001)
   adb_event(1, 0x0000, 0x0000, 0x00000000)
   adb_event(1, 0x0001, 0x0074, 0x00000000)
   adb_event(1, 0x0000, 0x0000, 0x00000000)
   
   
def back_key():
   
   Popen("adb %s shell input keyevent 4" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
   
   
   
def swipe(start, stop):

   if not YOUWAVE:
      Popen("adb %s shell input swipe %d %d %d %d" % (ADB_ACTIVE_DEVICE, start[0], start[1], stop[0], stop[1]), stdout=PIPE, shell=True).stdout.read()
   else:
      linear_swipe(start, stop, steps=5)
   
def linear_swipe(start, stop, steps=1):
   
   if not YOUWAVE:
      xloc = np.linspace(start[0], stop[0], steps + 1)
      yloc = np.linspace(start[1], stop[1], steps + 1)
   
      
      adb_event(2, 0x0003, 0x0039, 0x00000eb0)
      adb_event(2, 0x0003, 0x0035, xloc[0])
      adb_event(2, 0x0003, 0x0036, yloc[0])
      adb_event(2, 0x0003, 0x0030, 0x00000053)
      adb_event(2, 0x0003, 0x003a, 0x00000005)
      adb_event(2, 0x0000, 0x0000, 0x00000000)
      
      for i in range(steps):
         adb_event(2, 0x0003, 0x0035, xloc[i + 1])
         adb_event(2, 0x0003, 0x0036, yloc[i + 1])
         adb_event(2, 0x0003, 0x0030, 0x00000042)
         adb_event(2, 0x0003, 0x003a, 0x00000005)
         adb_event(2, 0x0000, 0x0000, 0x00000000)
         
      adb_event(2, 0x0003, 0x0039, 0xffffffff)
      adb_event(2, 0x0000, 0x0000, 0x00000000)
   
   else:
      xloc = np.linspace(int(start[0] * 2 ** 15 / 480.0), int(stop[0] * 2 ** 15 / 480.0), steps + 1)
      yloc = np.linspace(int(start[1] * 2 ** 15 / 640.0), int(stop[1] * 2 ** 15 / 640.0), steps + 1)

      adb_event_batch([
         (3, 0x0004, 0x0004, 0x00090001),
         (3, 0x0001, 0x0110, 0x00000001),
         (3, 0x0000, 0x0000, 0x00000000),
         (3, 0x0003, 0x0000, xloc[0]),
         (3, 0x0003, 0x0001, yloc[0]),
         (3, 0x0000, 0x0000, 0x00000000)
         ])
      
      for i in range(steps):
         adb_event_batch([
            (3, 0x0003, 0x0000, xloc[i + 1]),
            (3, 0x0003, 0x0001, yloc[i + 1]),
            (3, 0x0000, 0x0000, 0x00000000)
            ])
#         time.sleep(1.0/steps)
         
      adb_event_batch([         
         (3, 0x0004, 0x0004, 0x00090001),
         (3, 0x0001, 0x0110, 0x00000000),
         (3, 0x0000, 0x0000, 0x00000000)
         ])


def scroll(dx, dy):
   
   if not YOUWAVE:
      Popen("adb %s shell input trackball roll %d %d" % (ADB_ACTIVE_DEVICE, dx, dy), stdout=PIPE, shell=True).stdout.read()
   else:
#      xint = 200.0
      yint = 200.0
            
      numy = dy / yint
      for i in range(int(numy) + 1):
         if dy > 0:
            linear_swipe((5, 400), (5, 400 - yint), steps=5)
         else:
            linear_swipe((5, 200), (5, 200 + yint), steps=5)
         
   
def unlock_phone():
   
   power_key()
   time.sleep(1)
   home_key()
   time.sleep(.5)
   linear_swipe((187, 616), (340, 616))


def lock_phone():
   
   power_key()


def take_screenshot_adb():

#   Popen("adb shell /system/bin/screencap -p /sdcard/screenshot.png > error.log 2>&1;\
#          adb pull  /sdcard/screenshot.png screenshot.png >error.log 2>&1", stdout=PIPE, shell=True).stdout.read()
          
#   Popen("adb shell screencap -p | sed 's/\r$//' > screenshot.png", stdout=PIPE, shell=True).stdout.read()

#   Popen("adb shell screencap | sed 's/\r$//' > img.raw;\
#          dd bs=800 count=1920 if=img.raw of=img.tmp >/dev/null 2>&1;\
#          ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i img.tmp screenshot.png >/dev/null 2>&1",
#          stdout=PIPE, shell=True).stdout.read()
      
   ################
   # CURRENT BEST #
   ################
       
#   Popen("adb %s shell screencap | sed 's/\r$//' > img.raw"%ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
   if not YOUWAVE:
      Popen("adb %s shell /system/bin/screencap /sdcard/img.raw >/dev/null 2>&1;\
             adb %s pull  /sdcard/img.raw %s/img_%s.raw >/dev/null 2>&1"
             % (ADB_ACTIVE_DEVICE, ADB_ACTIVE_DEVICE, TEMP_PATH, ACTIVE_DEVICE),
            stdout=PIPE, shell=True).stdout.read()
      
      f = open(TEMP_PATH+'/img_%s.raw' % ACTIVE_DEVICE, 'rb')
      f1 = open(TEMP_PATH+'/img_%s1.raw' % ACTIVE_DEVICE, 'w')
      f.read(12) # ignore 3 first pixels (otherwise the image gets offset)
      rest = f.read() # read rest
      f1.write(rest)
    
      Popen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x800 -i img_%s1.raw %s/screenshot_%s.png >/dev/null 2>&1"
            % (ACTIVE_DEVICE, TEMP_PATH, ACTIVE_DEVICE), stdout=PIPE, shell=True).stdout.read()

   else:
#      Popen("ffmpeg -vframes 1 -vcodec rawvideo -f rawvideo -pix_fmt bgr32 -s 480x640 -i img_%s1.raw screenshot_%s.png >/dev/null 2>&1"%(ACTIVE_DEVICE,ACTIVE_DEVICE), stdout=PIPE, shell=True).stdout.read()
   
      cmd1 = 'adb %s shell /system/bin/screencap -p /sdcard/screenshot.png' % ADB_ACTIVE_DEVICE
      cmd2 = 'adb %s pull  /sdcard/screenshot.png "%s/screenshot_%s.png"' % (ADB_ACTIVE_DEVICE, TEMP_PATH, ACTIVE_DEVICE)
    
      Popen(cmd1, stdout=devnull, shell=True).wait()
      Popen(cmd2, stdout=devnull, stderr=devnull, shell=True).wait()
      
   
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
         return image[ybounds[0]:ybounds[1], :]
   else:
      if not ybounds:
         return image[:, xbounds[0]:xbounds[1]].copy()
      else:
         return image[ybounds[0]:ybounds[1], xbounds[0]:xbounds[1]].copy()
      
      
def swipeReference(template, destination=(0, 0), threshold=0.96, print_coeff=False, xbounds=None, ybounds=None, reuse_last_screenshot=False):
   
   ref = locateTemplate(template, threshold=threshold, retries=2, print_coeff=print_coeff, xbounds=xbounds, ybounds=ybounds, reuse_last_screenshot=reuse_last_screenshot)
   
   if not ref:
      printAction("Unable to navigate to swipe reference...", newline=True)
      return None
   
   if not xbounds:
      xbounds = (0, 480)
   if not ybounds:
      ybounds = (0, 800)
      
   diff = np.array(destination) - (ref + np.array([xbounds[0], ybounds[0]]))
   
   swipe(ref, map(int, ref + 0.613 * diff))
   time.sleep(.3)
   swipe(ref, map(int, ref + 0.613 * diff))
   time.sleep(.5)
   return ref
   

def locateTemplate(template, threshold=0.96, offset=(0, 0), retries=1, interval=0, print_coeff=True, xbounds=None, ybounds=None, reuse_last_screenshot=False,
                   recurse=None, click=False, scroll_size=[], swipe_size=[], swipe_ref=['', (0, 0)]):

   DEBUG=False
   import pylab as pl
   
   for i in range(retries):
      if not reuse_last_screenshot:
         take_screenshot_adb()
      
      time.sleep(.1)
      try:
         if device.getInfo('screenDensity') == 240:
            img_path = SCREEN_PATH
         else:
            img_path = SCREEN_PATH + '/dpi160'
            
         
         image_screen = readImage(TEMP_PATH+"/screenshot_%s.png" %ACTIVE_DEVICE, xbounds, ybounds)
#         image_screen   = readImage("test.png", xbounds, ybounds)
      except:
         print("ERROR: Unable to load screenshot_%s.png. This is bad, and weird!!!" % ACTIVE_DEVICE)
         return False
      
      result = np.array(0)
      match_found = False
      template = re.sub(r'-[0-9]*\.', '.', template)
      for j in range(5):
                  
         if YOUWAVE:
            name, ext = os.path.splitext(template)
            template_youwave = name + "_youwave" + ext
            if os.path.exists(img_path+'/'+template_youwave):
               template = template_youwave
      
         if os.path.exists(img_path+'/'+template):
            image_template = cv2.imread(img_path+'/'+template)

            if DEBUG:
               pl.imshow(image_template)
               pl.show()
               
            result = cv2.matchTemplate(image_screen, image_template, cv2.TM_CCOEFF_NORMED)
            
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
#          print("ERROR: Unable to match template \"%s\" with screenshot!!!" % template)
#          return False
      
      if print_coeff:
         sys.stdout.write("%.2f " % result.max())
         sys.stdout.flush()
#         print( " %.2f"%result.max(), end='' )
         
      if match_found:
         template_coords = np.unravel_index(result.argmax(), result.shape)
         template_coords = np.array([template_coords[1], template_coords[0]])
         object_coords = tuple(template_coords + np.array(offset))
         if click:
            left_click(object_coords)
            time.sleep(3)
         if print_coeff:
            sys.stdout.write("(%d,%d) " % (object_coords[0], object_coords[1]))
            sys.stdout.flush()
#         print(" (%d,%d)"%(object_coords[0],object_coords[1]),end=' ')
         return object_coords
      
      else:
         # See if the cause can be an Android error:
         if recurse:
            return None
         
         image_error = locateTemplate("android_error.png", recurse=True, threshold=0.9, offset=(65,31), reuse_last_screenshot=True)
         
         if image_error:
            print(' ')
            printAction("Android error detected and will (hopefully) be dealt with.", newline=True)
            left_click(image_error)
            time.sleep(10) # In case we hit a "wait" button
            retries = retries + 1

      if retries > 1:
         if swipe_ref[0] != '':
            swipeReference(swipe_ref[0], destination=swipe_ref[1], reuse_last_screenshot=False)
         if swipe_size:
            swipe(swipe_size[0], swipe_size[1])
            if interval < 1:
               time.sleep(1)
            else:
               time.sleep(interval)
         if scroll_size:
            scroll(scroll_size[0], scroll_size[1])
            if interval < 1:
               time.sleep(3)
         
         time.sleep(interval)
      
   return None
      
   
def check_if_vnc_error():
#   printAction( "Verifying VNC sanity..." )
#   ok_button = locateTemplate('vnc_error.png', correlation_threshold=0.992, offset=(318,124))
#   printResult(not ok_button)
#   if ok_button:
#      replay_macro("left_click",offset=ok_button)
   pass
      
def abort_if_vnc_died():
#   titlebar_coords = locateTemplate('titlebar.png', correlation_threshold=0.6)
#   titlebar_black_coords = locateTemplate('titlebar_black.png', correlation_threshold=0.6)
#   if titlebar_coords == None and titlebar_black_coords == None:
#      raise Exception("VNC appears to have died. Aborting.")
   pass

def preOCR(image_name, color_mask=(1, 1, 1), threshold=180, invert=True, xbounds=None, ybounds=None):
   
   import scipy.interpolate as interpolate
   import pylab as pl
   
   DEBUG = False

   image = readImage(image_name, xbounds, ybounds)
#   image = readImage(image_name)
   
   # Adjust color information
   image[:, :, 0] = image[:, :, 0] * color_mask[0]
   image[:, :, 1] = image[:, :, 1] * color_mask[1]
   image[:, :, 2] = image[:, :, 2] * color_mask[2]
   
   if DEBUG:
      pl.imshow(image)
      pl.show()
   
   # Convert to grey scale
   image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   
   if DEBUG:
      pl.imshow(image, cmap=pl.cm.Greys_r)
      pl.show()
   
   # Normalize
   img_min, img_max = image.min(), image.max()
   image = 255 * (image - float(img_min)) / (float(img_max) - img_min)
   
   if DEBUG:
      pl.imshow(image, cmap=pl.cm.Greys_r)
      pl.show()
   
   #Upinterpolate
   M, N = image.shape
   m_idx = np.linspace(0, 1, M)
   n_idx = np.linspace(0, 1, N)
   
   K = 2 # Upsampling factor
   m_up_idx = np.linspace(0, 1, M * K)
   n_up_idx = np.linspace(0, 1, N * K)
      
   image = interpolate.RectBivariateSpline(m_idx, n_idx, image, kx=4, ky=4)(m_up_idx, n_up_idx)
      
   #Inversion
   if invert:
      image = 255 - image
      
   if DEBUG:
      pl.imshow(image, cmap=pl.cm.Greys_r)
      pl.show()
      
   # Thresholding
   img = image ** 20
   image = 255 * img / (img + float(threshold) ** 20)
#   image = 255/(1+(float(threshold)/image)**20)
   
#   image[image>=threshold] = 255
#   image[image< threshold] = 0

   # Reverting to int8
   image = image.astype('uint8')
   
   cv2.imwrite(image_name.strip('.png') + '_processed.png', image)
   
   return image
   

def runOCR(image, mode='', lang='eng'):
   
   if mode == 'line':
      psm = '-psm 7'
   elif mode == '':
      psm = ''
   else:
      print("ERROR: runOCR() - Mode %s is not supported")
      return ''
   
   if lang == 'event_enemy':
      language = 'non'
   else:
      language = 'eng'
   
   cv2.imwrite('tmp.png', image)
   Popen("echo '' > text.txt" , shell=True, stdout=PIPE).stdout.read()
   Popen("tesseract tmp.png text %s -l %s >/dev/null 2>&1" % (psm, language), shell=True, stdout=PIPE).stdout.read()
   
   if os.path.getsize('text.txt') == 1:
      print("ERROR: runOCR() returned no output")
      return ''
   
   # TODO make sure file is not empty!!!
   text = open('text.txt', 'r').read()
#   text  = re.sub(r'\s', '', text) # Remove whitespaces
#   text  = re.sub(r',', '', text) # Remove commas
   text = re.sub(r'\n', '', text) # Remove newlines
   
   return text

def gotoMyPage():
   
   printAction("Clicking MyPage button...")
   mypage_button = locateTemplate("mypage_button.png", offset=(56, 21), retries=5)
   printResult(mypage_button)
   
   if not mypage_button:
      printAction("Huh? Unable to find MyPage button!!! That is bad.", newline=True)
      return False
   
   left_click(mypage_button)
   time.sleep(1)
   return True

def getMyPageStatus():
   
   info = {'roster':[]}
   
   print("Get MyPage info...")
   
   entered_mypage = False
   for i in range(2):
      gotoMyPage()
      time.sleep(1)
      printAction("Locating status screen...")
      swipe((240, 600), (240, 200))
      time.sleep(1)
      
      mypage_status_corner = swipeReference("mypage_status_upper_left_corner.png", destination=(0, 80))

      
#      mypage_status_corner = locateTemplate("mypage_status_upper_left_corner.png")
      printResult(mypage_status_corner)
      
      if mypage_status_corner:
         entered_mypage = True
         break
      
      else:
         left_click((200, 200)) # Possibly daily reward screen
         time.sleep(5)
#         printNotify('Unable to read MyPage. Daily reward?', 60)
                  
   if not entered_mypage:
      printAction("Adjust scrolling, this isn't working.", newline=True)
      return False

   printAction("Running OCR to figure out cards in roster...")
   take_screenshot_adb()
   cards_in_roster_image = preOCR("screenshot_%s.png" % ACTIVE_DEVICE, color_mask=(0, 1, 0), xbounds=(92, 185), ybounds=(195, 241))
   cards_in_roster_string = runOCR(cards_in_roster_image, mode='line')

   cards_in_roster_numbers = re.findall(r'\d+', cards_in_roster_string)
   cards_in_roster = tuple(map(int, cards_in_roster_numbers))
   
   try:
      print("Cards: %d/%d" % cards_in_roster)
      info['roster'] = cards_in_roster
      if cards_in_roster[1] - cards_in_roster[0] < 15:
         print("WARNING: Roster is soon full!!!")

   except:
      printAction("Unable to determine roster size.", newline=True)
      info['roster'] = [30, 70]
      cv2.imwrite('tmp_last_error.png', cards_in_roster_image)
      
   printAction("Running OCR to figure out amount of silver...")
   silver_image = preOCR("screenshot_%s.png" % ACTIVE_DEVICE, color_mask=(1, 1, 0), xbounds=(332, 446), ybounds=(272, 312))
   silver_string = runOCR(silver_image, mode='line', lang='event_enemy')
#   silver_numbers = re.search(r'[0-9,]+', silver_string).group(0)
#   silver_numbers = re.sub(r',', '', silver_numbers)
   
   try:
      silver_numbers = re.search(r'.+[,\.][0-9]{1,3}', silver_string).group(0)
      silver_numbers = re.sub(r'\s', '', silver_numbers)
      silver_numbers = re.sub(r',', '', silver_numbers)
      silver_numbers = re.sub(r'\.', '', silver_numbers)


      silver = int(silver_numbers)
      print("Silver: %d" % silver)
      info['silver'] = silver
   
   except:
      printAction("Unable to determine silver amount.", newline=True)
      cv2.imwrite('tmp_last_error.png', silver_image)
   
   return info

def gotoEventHome():
   
   gotoMyPage()
         
   printAction("Clicking event info button...")
   swipe((20, 600), (20, 200))
   time.sleep(1)
   event_button = locateTemplate("event_info_button.png", offset=(56, 21), retries=5, click=True, swipe_size=[(20, 600), (20, 100)])
   printResult(event_button)
   
   if not event_button:
      printAction("Huh? Unable to find event button!!! That is bad.", newline=True)
      return False
   
#   left_click(event_fantastic4)
   return True

   
def eventPlayMission(repeat=1):

   print("Playing event mission...")
   
   swipe((240, 100), (240, 750))
   swipe((240, 100), (240, 750))
   swipe((240, 100), (240, 750))
   swipe((240, 100), (240, 750))
   time.sleep(1)
   
   for i in range(repeat + 1):     
      
      printAction("Searching for event mission \"Proceed\" button...")
      proceed = locateTemplate("proceed_button.png", threshold=0.95, offset=(109, 23))
      printResult(proceed)
      
      if not proceed:
      
         # Double check that the return from mission actually was registered.
         mission_started = locateTemplate('mission_bar.png', print_coeff=False, reuse_last_screenshot=True)
         event_mission_button = locateTemplate("event_mission_button.png", threshold=0.95, offset=(109, 23), print_coeff=False, reuse_last_screenshot=True)
         go_to_boss = locateTemplate("event_mission_go_to_boss.png", offset=(130, 16), click=True, print_coeff=False, reuse_last_screenshot=True)
         if mission_started:
            printAction("Seems we failed to return from mission. Retrying.", newline=True)
            back_key()
            time.sleep(1)
         
         elif event_mission_button:
            printAction("Searching for event mission button...")
            left_click(event_mission_button)
            printResult(event_mission_button)
            time.sleep(3)
            scroll(0, 1000)
            time.sleep(1)
            
            repeat = repeat + 1
            
         elif go_to_boss:
            printAction("Raid boss detected. Playing the boss...", newline=True)
            
#            face_the_enemy = locateTemplate("face_the_enemy_button.png",
#                                             offset=(130,16), retries=8, click=True, ybounds=(0,600), swipe_size=[(20,600),(20,295)])
#            if not face_the_enemy:
#               printAction("Unable to find \"face the enemy\" button...", newline=True)
#               return False
#   
#            fight_enemy =  locateTemplate("event_mission_boss_fight_button.png", threshold=0.9,
#                                             offset=(85,24), retries=5, click=True)
#            if not fight_enemy:
#               printAction("Unable to find \"FIGHT\" button...", newline=True)
#               return False
            
            confirm = locateTemplate("event_mission_boss_confirm_button.png", threshold=0.9,
                                             offset=(85, 24), retries=10, click=True)
            if not confirm:
               printAction("Unable to find \"FIGHT\" button...", newline=True)
               return False
            
            repeat = repeat + 1
            
         else:

            gotoEventHome()
                       
            printAction("Searching for event mission button...")
            event_mission_button = locateTemplate("event_mission_button.png", threshold=0.95,
                                                   offset=(109, 23), retries=5, swipe_size=[(240, 600), (240, 295)])
            printResult(event_mission_button)
                  
            if event_mission_button:
               left_click(event_mission_button)
               time.sleep(3)
               scroll(0, 1000)
               time.sleep(1)
            else:
               print("Could not find event mission button!")
                  
            repeat = repeat + 1
                             
         
      else:
         
         left_click(proceed)
      
         printAction("Avaiting event mission screen...")
         mission_success = False
         
         for i in range(60):
            time.sleep(3)
            
#            mission_boss  = locateTemplate('event_mission_boss_screen.png', print_coeff=False)
            out_of_energy = locateTemplate('out_of_energy.png', print_coeff=False)
            #printResult(out_of_energy)
            
            mission_started = locateTemplate('mission_bar.png', reuse_last_screenshot=True)
            #printResult(mission_started)

            if out_of_energy:
               print('')
               printAction("No energy left! Exiting.", newline=True)
               back_key()
               time.sleep(1)
               return True
               
            if mission_started:
               print('')
               printAction("Mission started. Returning.", newline=True)
               back_key()
               time.sleep(1)
               mission_success = True
               break   

         if not mission_success:
            printAction("Timeout when waiting for mission screen", newline=True)
            return True


def eventFindEnemy(find_enraged=False, watchdog=10):
   
   printAction("Searching for a decent foe...")
   info = {'is_enraged':False}
   keep_assessing = True
   swipe((10, 600), (10, 200))
   take_screenshot_adb()
   while keep_assessing and watchdog > 0:
      keep_assessing = False
      is_enraged = False
      for j in range(10):
         ref = swipeReference("event_enemy_info_frame.png", threshold=0.85, destination=(0, 80), ybounds=(150, 500), reuse_last_screenshot=True)
         if not ref:
            return info
         time.sleep(1)
         event_enemy_corner = locateTemplate("event_enemy_info.png", threshold=.80, ybounds=(0, 400), reuse_last_screenshot=False)
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
         increased_raid_rating = locateTemplate("event_3_times_raid_rating.png", threshold=.85, retries=3, ybounds=(0, 450))
         printResult(increased_raid_rating)
         if increased_raid_rating:
            is_enraged = True
         else:
            keep_assessing = True
            watchdog = watchdog - 1
            
      
      printAction("Running OCR to figure out badass name and level...")
   #   printAction("Preprocessing image")

      badguy_image = preOCR("screenshot_%s.png" % ACTIVE_DEVICE, xbounds=(110, 370), ybounds=(84, 114)) #(99,126)
      badguy_string = runOCR(badguy_image, mode='line')
   
      badguy_name = re.sub(r' Lv.+', '', badguy_string)
      badguy_level = re.sub(r'.+Lv\.', '', badguy_string)
   #   badguy_level= tuple(map(int, badguy_string))
      
      print("%s at level %s" % (badguy_name, badguy_level))
            
      printAction("Running OCR to figure out enemy info...")
      e = event_enemy_corner
      enemy_image = preOCR("screenshot_%s.png" % ACTIVE_DEVICE, color_mask=(0, 1, 0), xbounds=(e[0], 470), ybounds=(e[1], e[1] + 144)) #old x: e[0]+250
      enemy_info = runOCR(enemy_image, mode='', lang='event_enemy')
   
      enemy_health = re.findall(r'\d+', enemy_info)
      try:
         enemy_health = tuple(map(int, enemy_health))
         print("Health: %d / %d" %(enemy_health[0],enemy_health[1]))
      except:
         print('WARNING: Unable to convert enemy health to int.')
         enemy_health = (1000,1000)
      
      print(enemy_health)
      print("Health: %d / %d" %(enemy_health[0],enemy_health[1]))
#      try:
#         if int(badguy_level) < 50  or (int(badguy_level) > 85 and not find_enraged):
#            printAction("Villain has a level outside [50,85]. Moving on...", newline=True)
#            keep_assessing = True
#            watchdog = watchdog - 1
#            swipe((10,400),(10,350))
#      except:
#         pass
      
      info['badguy_name'] = badguy_name
      info['badguy_level'] = badguy_level
      info['badguy_health'] = enemy_health
      info['is_enraged'] = is_enraged
      
   return info
      
def eventKillEnemies(find_enraged=False):
   
   printAction("Locating the \"face enemy\" button...")
   event_face_enemy = locateTemplate("event_enemies_in_area.png",
                                     offset=(240, 25), threshold=0.92, retries=2, reuse_last_screenshot=False, click=True)
   printResult(event_face_enemy)
   if not event_face_enemy:
      printAction("Unable to locate \"face enemy\" button...")
      return False
   
#   swipe((10,500),(10,300))
   time.sleep(1)
   
   for i in range(1):
      take_screenshot_adb()
#      if not i:
#         swipeReference("event_enemy_info_frame.png", destination=(0,80), reuse_last_screenshot=False)
      enemy_found = False
      for j in range(5):
         info = eventFindEnemy(find_enraged=find_enraged)
         
         try:
            if info['is_enraged'] or (info['badguy_name'] and not find_enraged):
               enemy_found = True
               break
         except:
            pass
#        scroll(0,-1000)
         printAction('Unable to find enemy. Retrying in 30 sec (%d/5)...' % (j + 1), newline=True)
         time.sleep(30)
  
         gotoEventHome()
         event_enemies_in_area = locateTemplate("event_enemies_in_area.png",
            offset=(154, 89), retries=5, ybounds=(0, 400), swipe_size=[(240, 600), (240, 295)])
         if not event_enemies_in_area:
            return False
#         event_face_enemy = locateTemplate("event_mission_button.png",
#            offset=(240,-54), threshold=0.92, retries=2, reuse_last_screenshot=False, click=True)
#         if not event_face_enemy:
#            return False
         take_screenshot_adb()
         
      if not enemy_found:
         return False
      
      time.sleep(2)
      printAction("Searching for \"go support\" or \"attack\" button...")
      support = locateTemplate("event_go_support_button.png", threshold=0.92, reuse_last_screenshot=True, click=True)
      attack_villain = locateTemplate("event_attack_button.png", threshold=0.92, reuse_last_screenshot=True, click=True)
      printResult(bool(support or attack_villain))
      if not attack_villain and not support:
         printAction("Unable to find an enemy to attack!", newline=True)
         return False
#      left_click(event_enemy_corner+np.array((66,164)))
#      left_click(event_enemy_corner+np.array((66,164)))
#      time.sleep(1)
#      swipe((20, 400), (20, 200))
      time.sleep(3)
#      printAction("Searching for deck select button...")
#      for j in range(5):
#         swipe((10,400),(10,200))
#         select_deck = locateTemplate("select_deck_button.png", threshold=.96, offset=(-144,17), ybounds=(0,600), click=True)
#         if select_deck:
#            break
#      printResult(select_deck)
#         
#      printAction("Selecting raider deck...")
#      raider_deck = locateTemplate("select_deck_raider.png", offset=(205,35), click=True)
#      printResult(raider_deck)
#      if not raider_deck:
#         return False
#   
#      printAction("Hitting select button...")
#      select_button = locateTemplate("select_button.png", offset=(60,16), click=True)
#      printResult(select_button)
#      if not select_button:
#         return False
                  
      # Assess the timer structure. It will basically count number of swipes, shitty.
#      weird_bool = True
#      watchdog = 15
#      while watchdog > 0:
#      for j in range(10):
#         if weird_bool:
      
      
      attack_blitz = locateTemplate("event_attack_blitz.png", threshold=0.99, offset=(74, 24))   
      attack_normal = locateTemplate("event_attack_normal.png", threshold=0.99, offset=(74, 24), reuse_last_screenshot=True)  
      attack_light = locateTemplate("event_attack_light.png", threshold=0.99, offset=(74, 24), reuse_last_screenshot=True)
            
      rds6 = False
      base_attack = 200000
      if info['badguy_health'][0] < base_attack and attack_light:
         printResult(True)
         printAction("Attacking with the 1 RDS option...", newline=True)
         left_click(attack_light)
         time.sleep(2)
         left_click(attack_light)
      elif info['badguy_health'][0] < 4*base_attack and attack_normal:
         printResult(True)
         printAction("Attacking with the 3 RDS option...", newline=True)
         left_click(attack_normal)
         time.sleep(2)
         left_click(attack_normal)
      elif attack_blitz:
         printResult(True)
         printAction("Attacking with the 6 RDS option...", newline=True)
         left_click(attack_blitz)
         time.sleep(2)
         left_click(attack_blitz)
         rds6 = True
      else:
         printAction("No attack power left. Quitting...", newline=True)
         printResult(False)
         return False
                           
      printAction("Confirming that enemy is taken down...")
      confirmed = False
      taken_out = False
      for i in range(15):
         left_click((200, 200))
         final_blow     = locateTemplate("event_final_blow_button.png", threshold=0.85, offset=(74, 24), click=True)
         confirm        = locateTemplate("event_mission_boss_confirm_button.png", offset=(74, 24), click=True, reuse_last_screenshot=True)
         decor          = locateTemplate("mission_top_decor.png", reuse_last_screenshot=True)
         battle_results = locateTemplate("event_battle_results.png", offset=(74, 24), reuse_last_screenshot=True)
         time.sleep(1)     
         
         if battle_results or decor:
            confirmed = True
            printResult(True)
            break
         
      if not confirmed:
         printResult(False)
      
#         if final_blow:
#            taken_out = True
#      
#         if confirm:
#            confirmed = True
#            break
#      
#      confirmed = True
#      taken_out = True
#      
#      if not confirmed:
#         return False
      
#      time.sleep(2)
#      if taken_out:
#         printAction("Villain taken down. Collecting reward...")
#         swipe((20,600),(20,200))
#         time.sleep(1)
#         reward    = locateTemplate("event_get_your_reward_button.png",  offset=(115,14), click=True, reuse_last_screenshot=True)
#         printResult(reward)
#      
#      
      
#            out_of_power = locateTemplate('event_out_of_power.png', threshold=0.985, print_coeff=False, reuse_last_screenshot=True)
#            if out_of_power:
#               print( '' )
#               printAction("No attack power left! Exiting.", newline=True)
#               return False
#            
#            end_of_battle = locateTemplate('event_battle_results.png', reuse_last_screenshot=True)
#            if end_of_battle:
#               print( '' )
#               printAction("Villain taken down. Returning.", newline=True)
#               return True
#            
##            time.sleep(3)
#            swipe((240,400),(240,200)) # This sometimes cause trouble with the face the enemy button
#            time.sleep(1)
#            weird_bool = False
#            watchdog = watchdog - 1
#            if not watchdog:
#               printResult(False)
#               printAction("Timeout when hoping for low-power termination ..", newline=True)
#               return True

      printAction("Checking if \"ask for support\" or \"collect reward\" is available...")
      success = False
      for i in range(6):
         ask_for_support = locateTemplate("event_ask_for_support_button.png", offset=(112, 15), swipe_size=[])
         reward = locateTemplate("event_get_your_reward_button.png", offset=(115, 14), reuse_last_screenshot=True)
         
         if not ask_for_support and not reward:
            swipe((240, 600), (240, 295))
            time.sleep(1)
            
         elif ask_for_support:
            printResult(True)
            success = True
            printAction("Found \"ask for support\" button. Clicking it...", newline=True)
            left_click(ask_for_support)
            return True and not rds6
            
         elif reward:
            printResult(True)
            success = True
            printAction("Found \"reward\" button. Clicking it...", newline=True)
            left_click(reward)
            return True and not rds6
         
      if not success:
         printResult(False)
      time.sleep(3)
      return False
#         left_click(face_the_enemy)
#         time.sleep(3)
#         
#         printAction( "Avaiting mission screen..." )
#
#         mission_success = False
#         for i in range(10):
#            time.sleep(1)
#            
##            out_of_power    = locateTemplate('event_out_of_power.png',   threshold=0.985, print_coeff=False)
#            mission_started = locateTemplate('event_fight_screen.png',   reuse_last_screenshot=True)
#            end_of_battle   = locateTemplate('event_battle_results.png', reuse_last_screenshot=True)
#            #printResult(mission_started)
#               
##            if out_of_power:
##               print( '' )
##               printAction("No attack power left! Exiting.", newline=True)
###                  back_key()
##               return False
#            
#            if end_of_battle:
#               print( '' )
#               printAction("Villain taken down. Returning.", newline=True)
#               return True
#               
##            if mission_started:
##               print( '' )
##               printAction("Mission started. Returning.", newline=True)
##               back_key()
##               time.sleep(int(uniform(1,2)))
##               mission_success = True
##               weird_bool = True
##               break
#            
#            # Sometimes one end up at the same screen too. Handle this.
#            
#         
#         weird_bool = True
#         if not mission_success:
#            printResult(False)
#            printAction("Timeout when waiting for mission screen. Defeated?", newline=True)
#            return True        
        
         
         
#   badguy_name  = re.sub(r' Lv.+', '', badguy_string)
#   badguy_level = re.sub(r'.+Lv\.', '', badguy_string)
#   badguy_level= tuple(map(int, badguy_string))
   
#   print( badguy_level )
   

      
   
def eventPlay(find_enraged=False):
      
   print("PLAYING EVENT")
   
   N = 6
   Nmax = 16
   keepalive = 0
   i = 0
   while (i < N or keepalive > 0) and i < Nmax:
#    for i in range(N):
      
      gotoEventHome()
  
      printAction("Checking if enemies are present in the area...")
      event_enemies_in_area = locateTemplate("event_enemies_in_area.png",
         offset=(154, 89), retries=5, ybounds=(0, 400), swipe_size=[(240, 600), (240, 295)])
      printResult(event_enemies_in_area)
      
      success = True
      if event_enemies_in_area:
         success = eventKillEnemies(find_enraged=find_enraged)
         # Continue as long as we get success
         if success and i > N-3:
            keepalive = 3

      else:
         dummy = eventPlayMission()
         for i in range(1):
            dummy = eventPlayMission()
      
      if not success:
         return False   
      
      time.sleep(2)
      i = i + 1
      keepalive = keepalive - 1

   
   return True
      
      
   
def listSortAlignment(alignment_type):
   
   printAction("Making sure alignment is set to \"%s\"..." % alignment_type)
   alignment_button = locateTemplate("alignment_button_%s.png" % alignment_type, threshold=0.95, offset=(56, 22))
   alignment_button_highlighted = locateTemplate("alignment_button_%s_highlighted.png" % alignment_type, threshold=0.95, offset=(56, 22))
   printResult(alignment_button or alignment_button_highlighted)
      
   if not alignment_button_highlighted:
      
      if not alignment_button:
         printAction("Unable to find alignment \"%s\" button!." % alignment_type, newline=True)
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
   swipe((1, 630), (479, 100))
   time.sleep(.5)
#   swipe((1,630),(479,400))
#   time.sleep(.5)
#   clicked_cards = []
   number_of_cards_selected = 0
   
#   card_coords = locateTemplate("card_%s.png"%card_name, correlation_threshold=0.95, offset=(214,86),
#                                ybounds=(0,600), swipe_ref=['list_select_button_area',()])

   # Cards with stapled lines are skipped (base card)
   top = locateTemplate("list_top_separator.png")
   if not top:
      printResult(False)
      printAction("Could not find the top of list? Weird.", newline=True)
      return False
   
   swipeReference("list_top_separator.png", destination=(20, 90), print_coeff=True, reuse_last_screenshot=True)
   
   for i in range(15):
      card_coords = locateTemplate("card_%s.png" % card_name, threshold=0.95, offset=(214, 86), ybounds=(0, 550))
      select_bar = locateTemplate("list_select_button_area.png", offset=(18, 26), ybounds=(150, 550), reuse_last_screenshot=True)
      if card_coords and select_bar:
         left_click([select_bar[0], select_bar[1] + 150])
         number_of_cards_selected += 1
         time.sleep(.5)
         break
      
#      swipe((1,600),(479,500))
#      time.sleep(1)
      line_separator = swipeReference("list_line_separator.png", destination=(20, 90), ybounds=(150, 600), threshold=0.85, print_coeff=True, reuse_last_screenshot=True)
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
   swipe((240, 630), (240, 220))
   time.sleep(.3)
#   clicked_cards = []
   number_of_cards_selected = 0
   
   for i in range(15):
      take_screenshot_adb()
      for card in cards_list:
         card_coords = locateTemplate("card_%s.png" % card, threshold=0.95, offset=(214, 86), ybounds=(300, 800), reuse_last_screenshot=True)
         
         if card_coords:
            left_click([card_coords[0], card_coords[1] + 300])
            number_of_cards_selected += 1
            stats.add(card, 1)
            time.sleep(.5)
            break
            
      
      swipe((240, 600), (240, 295)) # scroll one card at a time
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
      print("%s " % card, end='')
   print('')
   
   stats = Stats()
      
   printAction("Clicking roster button...")
   menu_button = locateTemplate("menu_button.png", offset=(56, 12))
   
   if not menu_button:
      printAction("Huh? Unable to find menu button!!! That is bad.", newline=True)
      printResult(False)
      return False
   
   left_click(menu_button)
   time.sleep(int(uniform(.5, 1)))
   
   roster_button = locateTemplate("main_menu.png", offset=(317, 189), retries=3)
   
   if not roster_button:
      printAction("Unable to find main menu!.", newline=True)
      printResult(False)
      return False
   
   printResult(True)
   left_click(roster_button)
   time.sleep(int(uniform(1, 2)))
   
   printAction("Searching for \"Sell Cards\" button...")
   sell_cards_button = locateTemplate("sell_cards_button.png", offset=(107, 23), retries=3)
   printResult(sell_cards_button)
   
   if not sell_cards_button:
      printAction("Unable to find \"Sell Cards\" button!.", newline=True)
      return False

   left_click(sell_cards_button)
   time.sleep(1)
   
   cards_found = markCards(cards_list, alignment='all')
   printResult(cards_found)
   if not cards_found:
      printAction("No cards were found. Returning.", newline=True)
      return False
   
   printAction("Clicking \"Sell Selected\" button...")
#   scroll(0,500)
   sell_selected_button = locateTemplate("sell_selected_button.png", offset=(92, 17), retries=2)
   printResult(sell_selected_button)
   
   if not sell_selected_button:
      printAction("Unable to find \"Sell Selected\" button", newline=True)
      return False

   left_click(sell_selected_button)
   time.sleep(3)
   
   scroll(0, 1000)
   sell_button = locateTemplate("sell_button.png", offset=(49, 19), retries=4)
   
   if not sell_button:
      printAction("Unable to find \"Sell\" button", newline=True)
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
   printAction("Boosting card: %s" % card_name, newline=True)
      
   printAction("Clicking \"boost\" button...")
   
   scroll(0, 1000)
   time.sleep(2)
   boost_from_fuse = locateTemplate("boost_from_fuse_button.png", offset=(193, 19), retries=4)
   printResult(boost_from_fuse)
   
   if not boost_from_fuse:
      printAction("Huh? Unable to find boost button!!! That is bad.", newline=True)
      return False
   
   left_click(boost_from_fuse)
   time.sleep(4)
   
   swipe((240, 650), (240, 100))
   time.sleep(1)
     
   listSortAlignment(alignment)
   
   printAction("Checking that multiple cards are selected...")
   multiple_cards_link = locateTemplate("list_multiple_cards_link.png", offset=(54, 33))
   printResult(multiple_cards_link)
   
   if multiple_cards_link:
      left_click(multiple_cards_link)
      time.sleep(3)
      swipe((240, 650), (240, 100))
      time.sleep(1)
   
   ########
   # TODO # Sort mechanism
   ########
      
   printAction("Locating and marking the mentioned cards...")
#   swipe((240,630),(240,198))
#   time.sleep(.3)
#   swipe((240,630),(240,198))
   scroll(0, -1000)
   time.sleep(1)
   swipe((240, 600), (240, 100))
   time.sleep(1)
   swipe((240, 600), (240, 100))
   time.sleep(1)
   swipe((240, 600), (240, 100))
   time.sleep(1)
#   clicked_cards = []
   number_of_cards_selected = 0
   
   for i in range(11):
      take_screenshot_adb()
      for card in cards_list:
         card_coords = locateTemplate("card_%s.png" % card, threshold=0.95, offset=(214, 86), ybounds=(300, 800), reuse_last_screenshot=True)
         
         if card_coords:
            left_click([card_coords[0], card_coords[1] + 300])
            number_of_cards_selected += 1
            time.sleep(.5)
            break
            
      swipe((240, 600), (240, 295)) # scroll one card at a time
      time.sleep(1)
      
   if number_of_cards_selected == 0:
      printResult(False)
      printAction("Could not find any of the specified cards...", newline=True)
      return False
   
   printResult(True)
   printAction("Clicking \"Boost\" button...")
#   scroll(0,500)
   boost_now = locateTemplate("boost_green_button.png", offset=(58, 17), retries=2)
   printResult(boost_now)
   
   if not boost_now:
      printAction("Unable to find \"Boost\" button", newline=True)
      return True

   left_click(boost_now)
   time.sleep(3)
   
   printAction("Clicking \"Boost\" button (second time)...")
   scroll(0, 1000)
   time.sleep(2)
   boost_now = locateTemplate("boost_green_button.png", offset=(58, 17), retries=2)
   printResult(boost_now)
   
   if not boost_now:
      printAction("Unable to find \"Boost\" button", newline=True)
      return True
   
   left_click(boost_now)
   
   printAction("Waiting for boost finished screen...")
   time.sleep(5)
   boost_finished = locateTemplate("boost_finished.png", offset=(58, 17), retries=15)
   printResult(boost_finished)
   
   if not boost_finished:
      printAction("Unable to find \"Boost\" button", newline=True)
      return True
   
   time.sleep(10)
   left_click((200, 200))
   time.sleep(3)
   left_click((200, 200))
   time.sleep(4)
      
   return True

def fuseCard(card_type, alignment='all'):
      
   print("FUSION")
   
   stats = Stats()
   
   printAction("Clicking fusion button...")
   fusion_button_coords = locateTemplate("fusion_button.png", offset=(60, 26), retries=2)
   fusion_button2_coords = locateTemplate("fusion_button2.png", offset=(60, 26))
   printResult(fusion_button_coords or fusion_button2_coords)
   
   if not fusion_button_coords and not fusion_button2_coords:
      printAction("Huh? Unable to find fusion button!!! That is bad.", newline=True)
      return
   
   if fusion_button_coords:
      left_click(fusion_button_coords)
   else:
      left_click(fusion_button2_coords)
      
   time.sleep(int(uniform(.5, 1)))
   
   printAction("Checking if more cards are available...")
   fuse_no_cards_left = locateTemplate("fuse_no_cards_left.png", offset=(195, 14))
   printResult(not fuse_no_cards_left)
   
   if fuse_no_cards_left:
      return False

   printAction("Checking if a base card is already selected...")
   for i in range(3):
      change_base_card_coords = locateTemplate("fusion_change_base_card_button.png", offset=(144, 15))
      base_card_menu = locateTemplate("fusion_select_base_card.png", offset=(100, 14))
            
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
      printAction("Unable to find a base card.", newline=True)
      return False
         
   time.sleep(2)
   printAction("Searching for a fuser card...", newline=True)
#   swipe((240,600),(240,100))
   success = selectCard(card_type, alignment='none')
   if not success:
      printAction("Unable to find the fuser. This is strange and should not happen.", newline=True)
      return False
            
   printAction("Clicking \"fuse this card\" button...")
   fuse_this_card_button_coords = locateTemplate("fusion_fuse_this_card_button.png", offset=(106, 16), retries=5)
   printResult(fuse_this_card_button_coords)
   
   if not fuse_this_card_button_coords:
      return False
   
   time.sleep(1)
   left_click(fuse_this_card_button_coords)
   time.sleep(4) # The fusion thing takes some time.
   
   printAction("Waiting for first fusion screen...")
   rarity_upgraded = locateTemplate("fusion_rarity_upgraded.png", threshold=0.98, offset=(243, 70), retries=10)
   
#   if not ironman_fused_screen1:
#      return False
#   
#   for i in range(10):
#      time.sleep(int(uniform(1,2)))
#      ironman_fused_screen1 = locateTemplate("fusion_ironman_fused1.png", offset=(155,200), retries=5)
#            
#      if ironman_fused_screen1:
#         left_click(ironman_fused_screen1)
#         break
   
   printResult(rarity_upgraded) 
   if not rarity_upgraded:
      printAction("First fusion screen did not appear. Buggy game?", newline=True)
      return False
   
   time.sleep(1)
   stats.add(card_type, 2)
   left_click(rarity_upgraded)
   time.sleep(1)
   
   printAction("Waiting for fusion finished screen...")
   for i in range(10):
      time.sleep(int(uniform(1, 2)))
      left_click(rarity_upgraded)
      fusion_finished = locateTemplate("fusion_finished.png", offset=(240, 110), retries=3)
            
      if fusion_finished:
         printResult(fusion_finished) 
         printAction("Fusion successful!", newline=True)
         return True
   
   printResult(fusion_finished) 
   return False
      
      
def tradeCards(receiver='joinge', cards_list=['rare_ironman'], alignment='all'):
      
   print("TRADING")
   printAction("Trading the following cards to %s: " % receiver)
   for card in cards_list:
      print("%s " % card, end='')
   print('')
   
#   stats = Stats()
      
   printAction("Searching for recevier...")
   menu_button = locateTemplate("menu_button.png", offset=(56, 12))
   
   if not menu_button:
      printAction("Huh? Unable to find menu button!!! That is bad.", newline=True)
      printResult(False)
      return False
   
   left_click(menu_button)
   time.sleep(1)
   
   player_search_button = locateTemplate("main_menu.png", offset=(107, 340), retries=3)
   
   if not player_search_button:
      printAction("Unable to find main menu!.", newline=True)
      printResult(False)
      return False
   
   printResult(True)
   left_click(player_search_button)
   time.sleep(2)
   
   printAction("Entering receiver name...")
   text_field = locateTemplate("text_box.png", offset=(68, 22), retries=3)
   printResult(text_field)
   
   if not text_field:
      printAction("Unable to find text field to enter receiver!.", newline=True)
      return False

   left_click(text_field)
   time.sleep(1)
   enter_text(receiver)
   time.sleep(1)
   search = locateTemplate("player_search_button.png", offset=(57, 17), print_coeff=False, reuse_last_screenshot=True)
   time.sleep(1)
   left_click(search) # Mobage password field
   time.sleep(3)
   printAction("Clicking receiver name...")
   left_click((345, 672))
   time.sleep(3)
   
   trade = locateTemplate("player_info_trade_button.png", offset=(55, 14), retries=3)
   printResult(trade)
   
   if not trade:
      printAction("Unable to find trade button on player info page!.", newline=True)
      return False

   left_click(trade)
   time.sleep(2)
   
   one_or_more_card_found = False
   for card in cards_list:
      printAction("Adding another card for trade...")
      trade_card = locateTemplate("trade_card_button.png", offset=(59, 17), retries=3, ybounds=((450, 800)))
      trade_card = tuple(np.array(trade_card) + (0, 450))
         
      if not trade_card:
         printAction("Unable to find card trade button!.", newline=True)
         return False
      
      time.sleep(1)
      left_click(trade_card)
      time.sleep(3)
      printResult(trade_card)
      
      cards_found = selectCard(card, alignment=alignment)
      printResult(cards_found)
      if cards_found:
         one_or_more_card_found = True
      else:
         printAction("Can't find this card, returning to trade page.", newline=True)
         scroll(0, 1000)
         time.sleep(2)
         back = locateTemplate("trade_back_to_trade_button.png", offset=(190, 19), retries=2, click=True)
         if not back:
            printAction("Unable to return from trade page. This should not happen.", newline=True)
         break
      
   if not one_or_more_card_found:
      printAction("No cards were found. Returning.", newline=True)
      return False
   
   printAction("Trading for 1 silver...")
   trade_silver = locateTemplate("trade_silver_button.png", offset=(59, 17), retries=2, ybounds=((0, 550)))
      
   if not trade_silver:
      printAction("Unable to find card trade button!.", newline=True)
      return False
   
   time.sleep(1)
   left_click(trade_silver)
   time.sleep(3)
   printResult(trade_silver)
   
   printAction("Entering 1 silver...")
   text_field = locateTemplate("text_box.png", offset=(68, 22), retries=3)
   printResult(text_field)
   
   if not text_field:
      printAction("Unable to silver text field!.", newline=True)
      return False
   
   left_click(text_field)
   time.sleep(1)
   enter_text("1")
   time.sleep(1)
   left_click((453, 757))
#   add = locateTemplate("add_button.png", offset=(46,17), reuse_last_screenshot=True)
#   time.sleep(1)
#   left_click(add) # Mobage password field
   time.sleep(3)
   
   scroll(0, 1000)
   time.sleep(.5)
   swipe((10, 100), (10, 600))
   time.sleep(.5)
   
   printAction("Clicking \"Offer Trade\" button...")
   offer_trade = locateTemplate("trade_offer_button.png", offset=(86, 15))
   printResult(offer_trade)
   
   if not offer_trade:
      printAction("Huh? Unable to find \"Offer Trade\" button!!! That is bad.", newline=True)
      return False
   
   left_click(offer_trade)
   time.sleep(3)

   return True
      
def play_mission(mission_number=(3, 2), repeat=50, statistics=True):
      
   stats = Stats()
   
   if statistics:
      stats.silverStart("mission_%d-%d" % mission_number)
            
   print("Playing mission %d-%d..." % mission_number)

   initial_run = True
   for i in range(repeat + 1):
      check_if_vnc_error()
      printAction("Searching for mission %d-%d button..." % mission_number)
      mission_button_coords = locateTemplate("mission_%d_%d.png" % mission_number, threshold=0.992, offset=(215, 170), retries=3)
      printResult(mission_button_coords)
      if not mission_button_coords:
         
         # Double check that the return from mission actually was registered.
         mission_started = locateTemplate('mission_bar.png', print_coeff=False, reuse_last_screenshot=True)
         top_mission_list = locateTemplate('mission_top_decor.png', print_coeff=False, reuse_last_screenshot=True)
         if mission_started and not initial_run:
            printAction("Seems we failed to return from mission. Retrying.", newline=True)
            back_key()
            time.sleep(1)
            repeat = repeat + 1
            
         # Are we simply at the top of the missions list?
         elif top_mission_list and not initial_run:
            printAction("Top of mission screen detected. Realigning...", newline=True)
            scroll(0, 1000)
            time.sleep(.3)
            swipe((10, 100), (10, 350))
            time.sleep(.3)
            
            for i in range(mission_number[1] - 1):
               swipe((10, 100), (10, 690))
               
            time.sleep(1)
            repeat = repeat + 1
            
         else:
            printAction("Navigating to missions list...", newline=True)
            initial_run = False
            left_click((181, 774)) # mission button
            time.sleep(3)
            scroll(0, 1000)
   #         swipe((250,390),(250,80))
            printAction("Searching for \"operations\" button...")
            operations_button = locateTemplate("operations_button.png", offset=(50, 15), retries=6, click=True)
            printResult(operations_button)
            
            if not operations_button:
               return True
            #time.sleep(2)
            #left_click((240,602)) #operations button
            
            time.sleep(3)
            printAction("Locating mission %d button..." % mission_number[0])
            mission_button_coords = locateTemplate('mission_list_%d.png' % mission_number[0], retries=5, threshold=0.92, offset=(170, 10))
            printResult(mission_button_coords)
            if not mission_button_coords:
   #            time.sleep(1)
               printAction("Locating mission %d button..." % mission_number[0])
               swipe((20, 600), (20, 80))
               time.sleep(int(uniform(1, 2)))
               mission_button_coords = locateTemplate('mission_list_%d.png' % mission_number[0], threshold=0.92)
               printResult(mission_button_coords)
               
            if not mission_button_coords:
               print("Unable to locate mission buttion. This shouldn't happen. Dammit!")
               
               if statistics:
                  stats.silverEnd("mission_%d-%d" % mission_number)
               
               return True # Retry
            
            left_click(mission_button_coords)
            time.sleep(int(uniform(1, 2)))
            #printAction( "Navigating to mission %d-%d..."%mission_number, newline=True )
            scroll(0, 1000)
            time.sleep(.3)
            swipe((10, 100), (10, 350))
            time.sleep(.3)
            
            for i in range(mission_number[1] - 1):
               swipe((10, 100), (10, 690))
               
            time.sleep(1)
            
            repeat = repeat + 1
            
            
            #if repeat > 30:
               #print( "30 mission iterations. Assuming error and exiting." )
               #return False
         
      else:
         initial_run = False
         left_click(mission_button_coords)
         printAction("Avaiting mission screen...")
         mission_success = False
         for i in range(10):
            time.sleep(int(uniform(1, 2)))
            
            out_of_energy = locateTemplate('out_of_energy.png', threshold=0.985, print_coeff=False)
            #printResult(out_of_energy)
            
            mission_started = locateTemplate('mission_bar.png', threshold=0.985)
            #printResult(mission_started)
               
            if out_of_energy:
               print('')
               printAction("No energy left! Exiting.", newline=True)
               back_key()
               
               if statistics:
                  stats.silverEnd("mission_%d-%d" % mission_number)
               
               return True
               
            if mission_started:
               print('')
               printAction("Mission started. Returning.", newline=True)
               time.sleep(1)
               back_key()
               time.sleep(int(uniform(1, 2)))
               mission_success = True
               
               if statistics:
                  stats.add("mission_%d-%d" % mission_number, 1)
                  
               break
         
         if not mission_success:
            printAction("Timeout when waiting for mission screen", newline=True)
            if statistics:
               stats.silverEnd("mission_%d-%d" % mission_number)
            return False
                                  
   if statistics:
      stats.silverEnd("mission_%d-%d" % mission_number)
          
          
def playNewestMission(repeat=50):

   print("MISSION: Newest...")

   for i in range(repeat + 1):
      printAction("Searching for newest mission button...")
      mission_newest_button  = locateTemplate("mission_newest_button.png", threshold=0.95,
                                             offset=(193, 14))
                  
      if not mission_newest_button:
         
         # Double check that the return from mission actually was registered.
         mission_started = locateTemplate('mission_bar.png', print_coeff=False, reuse_last_screenshot=True)
         mission_boss_encounter = locateTemplate("mission_boss_encounter.png", offset=(130, 16), print_coeff=False, reuse_last_screenshot=True)

         if mission_started:
            printAction("Seems we failed to return from mission. Retrying.", newline=True)
            back_key()
            time.sleep(1)
         
         elif mission_boss_encounter:
            printAction("Raid boss detected. Playing the boss...", newline=True)
            
#            go_to_boss = locateTemplate("event_mission_go_to_boss.png",
#                                        offset=(130,16), retries=4, click=True, ybounds=(0,600), swipe_size=[(20,400),(20,295)])
#            if not go_to_boss:
#               printAction("Unable to find \"go to boss\" button...", newline=True)
#               return False
            
            face_the_enemy = locateTemplate("mission_face_the_super_villain_button.png",
                                             offset=(130, 16), retries=8, click=True, ybounds=(0, 600), swipe_size=[(20, 600), (20, 295)])
            if not face_the_enemy:
               printAction("Unable to find \"face the enemy\" button...", newline=True)
               return False
   
            fight_enemy = locateTemplate("event_mission_boss_fight_button.png", threshold=0.9,
                                             offset=(85, 24), retries=5, click=True)
            if not fight_enemy:
               printAction("Unable to find \"FIGHT\" button...", newline=True)
               return False
            
            confirm = locateTemplate("event_mission_boss_confirm_button.png", threshold=0.9,
                                             offset=(85, 24), retries=20, interval=1, click=True)
            if not confirm:
               printAction("Unable to find \"FIGHT\" button...", newline=True)
               return False
            
            repeat = repeat + 1
            
         else:

            mission_button = locateTemplate('mission_button.png', offset=(49, 13), print_coeff=False, reuse_last_screenshot=True)
            
            left_click(mission_button) # mission button
            time.sleep(3)
         
            printAction("Searching for newest mission button...")
            mission_newest_button = locateTemplate("mission_newest_button.png", threshold=0.95,
                                                   offset=(193, 14), retries=5, swipe_size=[(240, 500), (240, 295)])
            printResult(mission_newest_button)
            if not mission_newest_button:
               return False
               
            time.sleep(1)
            
            repeat = repeat + 1
                    
      else:
         left_click(mission_newest_button)
         printAction("Avaiting newest mission screen...")
         mission_success = False
         for i in range(30):
            time.sleep(int(uniform(1, 2)))
            
            mission_started = locateTemplate('mission_bar.png', threshold=0.985, print_coeff=False)
            out_of_energy = locateTemplate('out_of_energy.png', threshold=0.985, print_coeff=False, reuse_last_screenshot=True)
            mission_boss = locateTemplate("mission_boss_encounter.png", offset=(130, 16), click=True, print_coeff=False, reuse_last_screenshot=True)
                           
            if out_of_energy:
               print('')
               printAction("No energy left! Exiting.", newline=True)
               back_key()
               
#               if statistics:
#                  stats.silverEnd("mission_%d-%d"%mission_number)
               
               return True
            
            if mission_boss: #????
               
               printAction('', newline=True)
               printAction("Mission boss detected! Playing him...", newline=True)
               
               printAction("Attempting to find and click first \"face the enemy\" button...")
               face_the_enemy = locateTemplate("mission_face_the_super_villain_button.png",
                                                offset=(130, 16), retries=8, click=True, ybounds=(0, 600), swipe_size=[(20, 600), (20, 295)])
               printResult(face_the_enemy)
               if not face_the_enemy:
                  return False
               
               printAction("Attempting to find and click second \"face the enemy\" button...")
               face_the_enemy = locateTemplate("mission_face_the_super_villain_button.png",
                                                offset=(130, 16), retries=15, click=True, ybounds=(0, 600), swipe_size=[(20, 600), (20, 295)])
               printResult(face_the_enemy)
               if not face_the_enemy:
                  return False
      
               printAction("Attempting to find and click \"FIGHT\" button...")
               fight_enemy = locateTemplate("event_mission_boss_fight_button.png", threshold=0.9,
                                                offset=(85, 24), retries=10, click=True)
               printResult(fight_enemy)
               if not fight_enemy:
                  return False
               
               printAction("Attempting to find and click \"CONFIRM\" button...")
               confirm = locateTemplate("event_mission_boss_confirm_button.png", threshold=0.9,
                                                offset=(85, 24), retries=10, click=True)
               printResult(confirm)
               if not confirm:
                  return False
               
               repeat = repeat + 1
               break
               
            if mission_started:
               print('')
               printAction("Mission started. Returning.", newline=True)
               time.sleep(1)
               back_key()
               time.sleep(int(uniform(1, 2)))
               mission_success = True
               
#               if statistics:
#                  stats.add("mission_%d-%d"%mission_number, 1)
                  
               break
         
         if not mission_success:
            printAction("Timeout when waiting for mission screen", newline=True)
#            if statistics:
#               stats.silverEnd("mission_%d-%d"%mission_number)
            return False

def startMarvel(user, attempts=3, password=None, enable_cache=False):
   
   if YOUWAVE:
      print( "Macro is being run in YOUWAVE MODE" )
   
   id_files = [
      "databases/requests-journal",
      "databases/webview.db-journal",
      "databases/webviewCookiesChromium.db",
      "files/.flurryagent.22e4372b",
      "files/__MBG_CREDENTIALS",
      "shared_prefs/CookiePrefsFile.xml",
      "shared_prefs/Preference.xml" ]
      
   if enable_cache:
      adb_copy_to_sdcard_cmd = ''
      adb_copy_to_data_cmd = ''
      for i, f in enumerate(id_files):
         if i % 5 == 0:
            adb_copy_to_sdcard_cmd += "adb %s shell \"" % ADB_ACTIVE_DEVICE
            adb_copy_to_data_cmd += "adb %s shell \"" % ADB_ACTIVE_DEVICE
         adb_copy_to_sdcard_cmd += "echo 'cp /data/data/com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android/%s /sdcard/pull_tmp/%s' | su; " % (f, f)
         adb_copy_to_data_cmd += "echo 'cp /sdcard/push_tmp/%s /data/data/com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android/%s' | su; " % (f, f)
         if i % 5 == 4:
            adb_copy_to_sdcard_cmd += "\"; "
            adb_copy_to_data_cmd += "\"; "
      if (i - 1) % 5 != 4:
         adb_copy_to_sdcard_cmd += "\"; "
         adb_copy_to_data_cmd += "\"; "
   
#   adb_copy_to_sdcard_cmd = \
#      "adb %s shell \
#      \" rm -r /sdcard/pull_tmp;\
#         mkdir /sdcard/pull_tmp;\
#         mkdir /sdcard/pull_tmp/files;\
#         mkdir /sdcard/pull_tmp/shared_prefs\";\
#         adb %s shell \
#      \" %s \";\
#      adb %s pull /sdcard/pull_tmp ./users/%s\
#      "%(ADB_ACTIVE_DEVICE,ADB_ACTIVE_DEVICE,adb_copy_to_sdcard_cmd,ADB_ACTIVE_DEVICE,user)

   def attempt_start(user):
      unlock_phone()
      
      if not os.path.isdir('./users'):
         os.mkdir('./users')
         
#      NEW_USER = True
      NEW_USER = False
      if enable_cache and os.path.isdir('./users/%s' % user):
         exitMarvel(False)
         print(
         Popen("adb %s shell rm -r /sdcard/push_tmp;\
                adb push ./users/%s /sdcard/push_tmp;\
                %s \
                " % (ADB_ACTIVE_DEVICE, user, adb_copy_to_data_cmd),
               stdout=PIPE, shell=True).stdout.read())
         time.sleep(2)
         launch_marvel()
      
      else:
         NEW_USER = True
         clearMarvelCache()
         launch_marvel()
#         check_if_vnc_error()
         #printAction("Searching for
         printAction("Searching for login screen...")
         login_screen_coords = locateTemplate('login_screen.png', threshold=0.95, retries=25, interval=1)
         printResult(login_screen_coords)
         if login_screen_coords:
            adb_login(login_screen_coords, user, password)            
      
      printAction("Searching for home screen...")
      login_success = False
      for i in range(35):
         time.sleep(1)
         home_screen = locateTemplate('home_screen.png', threshold=0.95)
            
         if home_screen:
            if enable_cache and NEW_USER:
               os.mkdir('./users/%s' % user)
               os.mkdir('./users/%s/files' % user)
               os.mkdir('./users/%s/shared_prefs' % user)
               
               print(
               Popen("adb %s shell \
                     \" rm -r /sdcard/pull_tmp;\
                        mkdir /sdcard/pull_tmp;\
                        mkdir /sdcard/pull_tmp/files;\
                        mkdir /sdcard/pull_tmp/shared_prefs\";\
                        %s \
                     adb %s pull /sdcard/pull_tmp ./users/%s\
                     " % (ADB_ACTIVE_DEVICE, adb_copy_to_sdcard_cmd, ADB_ACTIVE_DEVICE, user),
                     stdout=PIPE, shell=True).stdout.read())

            time.sleep(1)
            ad  = locateTemplate('home_screen_ad.png', offset=(90, 20), threshold=0.95)
            ad2 = locateTemplate('home_screen_ad2.png', offset=(90, 20), threshold=0.95, reuse_last_screenshot=True)
            if ad or ad2:
               if ad:
                  left_click(ad) # kills ads
               if ad2:
                  left_click(ad2) # kills ads
               time.sleep(1)
            
#            left_click((346,551)) # kills ads
            login_success = True
            break
         
      if not login_success:
         if locateTemplate('home_screen_maintenance.png'):
            printAction("It appears server is under maintenance...", newline=True)
      
#      if login_success:
#         printAction( "Finished login success!!", newline=True)
#      else: 
#         printAction( "login FAILED!!!", newline=True)
#        
      printResult(login_success) 
      return login_success
      
         
   all_ok = False
   print('')
   print('')
   print("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
   print("    %s" %user)
   print("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
   
   for i in range(attempts):
      print('')
      print("Login attempt %d on account %s..." % (i, user))
      login_ok = attempt_start(user)
      if login_ok:
         all_ok = True
         break
      
   return all_ok
   # adb catlog
   
def start_marvel_joinge():
   return startMarvel('JoInge')
   
def start_marvel_jollyma():
   return startMarvel('JollyMa')
   
def start_marvel_jojanr():
   return startMarvel('JoJanR')
   
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
   
   success = True
   for i in range(10):
      if fuseCard(card_type=card_type, alignment=fuse_alignment):
         if success:
            success = boostCard(card_name=card_type, cards_list=cards_list, alignment=boost_alignment)
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

   play_mission((2, 4), 50)
      
   fuseAndBoost('uncommon_ironman',
                all_feeder_cards,
                fuse_alignment='tactics')
   
   try:
      info = getMyPageStatus()
      roster_count, roster_capacity = info['roster']
      
      if not roster_count or roster_count > 60:
         printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
         sellAllCards(all_feeder_cards)
   except:
      print("ERROR: Trouble when reading MyPage status or when reading roster count")
   
def farmMission24FuseAndSell():

   play_mission((2, 4), 50)
   
   fuseAllCards('uncommon_ironman', 'tactics')
      
   sellAllCards(all_feeder_cards)   
         
   try:
      info = getMyPageStatus()
      roster_count, roster_capacity = info['roster']
      
      if not roster_count or roster_count > 60:
         printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
   except:
      print("ERROR: Trouble when reading MyPage status or when reading roster count")
   
   printNotify("Done processing this player!!!")
#   info = getMyPageStatus()
#   roster_count, roster_capacity = info['roster']
#   
#   if not roster_count or roster_count > 50:
#      printAction("Roster exceeds 30 cards. Sell and fuse baby!!!", newline=True)
#      sellAllCards(all_feeder_cards)
#      fuseAllCards('uncommon_ironman', 'tactics')
      
def getSilver():
   
   play_mission((4, 3), 2 * 23)
   
   time.sleep(.5)
   info = getMyPageStatus()
   
   roster_count, roster_capacity = info['roster']
   
   if not roster_count or roster_count > 55:
      printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
      sellAllCards(['common_medusa', 'common_enchantress'])
      
def farmMission32():

   play_mission((3, 2), 40)
   
   fuseAndBoost('uncommon_ironman',
#                all_feeder_cards,
                fuse_alignment='tactics')
   
   try:
      info = getMyPageStatus()
      roster_count, roster_capacity = info['roster']
      
      if not roster_count or roster_count > 55:
         printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
         sellAllCards(['common_thing', 'common_blackcat', 'common_spiderwoman', 'common_sandman'])
   except:
      print("ERROR: Trouble when reading MyPage status or when reading roster count")
   
   printNotify("Done processing this player!!!")
   

def farmMission32FuseAndBoost():

   play_mission((3, 2), 50)
      
   fuseAndBoost('uncommon_ironman',
                all_feeder_cards,
                fuse_alignment='tactics')
   
   try:
      info = getMyPageStatus()
      roster_count, roster_capacity = info['roster']
      
      if not roster_count or roster_count > 60:
         printAction("Roster exceeds 30 cards. Sell, sell, sell!!!", newline=True)
         sellAllCards(['common_thing', 'common_blackcat', 'common_spiderwoman', 'common_sandman'])
   except:
      print("ERROR: Trouble when reading MyPage status or when reading roster count")
   
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
recently_launched = []
#
def getIndex(user):
   for i, usr in enumerate(info.accounts):
      if info.accounts.keys()[i] == user:
         return i
   return -1

def randomUserStart(user_list=None):
   
   global recently_launched
   
   if user_list == None:
      user_list = info.accounts.keys()
   
   if recently_launched == []:
      recently_launched = [0] * info.accounts.__len__()
   
   need_reset = True
   for user in user_list:
      if recently_launched[getIndex(user)] == 0:
         need_reset = False
         break
         
   if need_reset:
      for user in user_list:
         recently_launched[getIndex(user)] = 0
         
   while True:
      i = int(uniform(0, user_list.__len__() - 0.000001))
      if recently_launched[getIndex(user_list[i])] == 0:
         recently_launched[getIndex(user_list[i])] = 1
         return startMarvel(user_list[i])
   
# def startFakeAccounts():
#    
#    for user in fakeAccounts.keys():
#       startMarvel(user)
   
def runAll24():
   while True:
      for i in info.accounts.keys():
         try:
            if randomUserStart():
               farmMission24FuseAndBoost()
               exitMarvel()
         except:
            pass
         time.sleep(3 * 60)
      
def runAll32():
   while True:
      for i in info.accounts.keys():
         try:
            if randomUserStart():
               farmMission32()
               exitMarvel()
         except:
            pass
         time.sleep(3 * 60)
      #time.sleep(60*uniform(5,15))

               
         
def runAll43():
   while True:
      for i in info.accounts.keys():
         try:
            if randomUserStart():
               play_mission((4, 3), 2 * 23)
               exitMarvel()
         except:
            pass
         time.sleep(60 * uniform(1, 5))
         
      time.sleep(60 * uniform(35, 55))
   
      
def blockUntilQuit():
   
   print("Waiting until game is killed.")
   time.sleep(3)
   while True:
      if not re.findall('MARVEL', Popen('adb %s shell ps' % ADB_ACTIVE_DEVICE, shell=True, stdout=PIPE).stdout.read()):
         break
      time.sleep(3)
   print("Game was killed. Moving on...")
      
def startAndRestartWhenQuit():
   

   for i in info.accounts.keys():
      randomUserStart()
         
      while True:
         if not re.findall('MARVEL', Popen('adb %s shell ps' % ADB_ACTIVE_DEVICE, shell=True, stdout=PIPE).stdout.read()):
            break

         time.sleep(2)
         
def adjustBrightness(percent=10):
   
   Popen("adb %s shell echo 'echo %d > /sys/devices/platform/samsung-pd.2/s3cfb.0/spi_gpio.3/spi_master/spi3/spi3.0/backlight/panel/brightness' \| su" % (ADB_ACTIVE_DEVICE, percent), stdout=PIPE, shell=True).stdout.read()
   
         
def sleepToCharge(preferred=60):
   
   
   output = Popen("adb %s shell cat /sys/class/power_supply/battery/capacity" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()
   had_to_rest = False
   while int(output) < 50:
      if not had_to_rest:
#         lock_phone()
         print("BATTERY below 20\%. Need to sleep for a bit.")
         had_to_rest = True
         
      output = Popen("adb %s shell cat /sys/class/power_supply/battery/capacity" % ADB_ACTIVE_DEVICE, stdout=PIPE, shell=True).stdout.read()         
      time.sleep(60)

#   if had_to_rest:
#      unlock_phone()
      
   time.sleep(preferred)
   
def cyclePlayers():

   adjustBrightness()
   while True:
      for i in info.accounts.keys():
         try:
            if randomUserStart():
               notify()
               blockUntilQuit()
               exitMarvel()
         except:
            pass
         
         
def checkTraining():
   
   while(True):
      gotoMyPage()
      time.sleep(2)
      ref = locateTemplate('training_searching_text.png', threshold=0.95, interval=1)
      printResult(ref)
      
      if not ref:
         break
      
      time.sleep(1)
      
   notify()

def checkRaid(health_limit):
   
   def playEnemy():
      scroll(1000, 0)
      swipe((20, 200), (20, 400))
      
      info = eventFindEnemy(True)
      
      if info['is_enraged']:
         notify()
         return True
      elif info['badguy_health'][0] < health_limit:
         notify()
         return True
      else:
         return False
         
#      time.sleep(1)
#      printAction("Searching for \"go support\" button...")
#      support = locateTemplate("event_go_support_button.png", threshold=0.92, click=True)
#      printResult(bool(support))
#      if not support:
#         printAction("Unable to find an enemy to attack!", newline=True)
#         return False
#
#      time.sleep(1)
#      swipe((20, 400), (20, 200))
#      time.sleep(1)
#
#      printAction("Attacking with 1 RDS option...")
#         
#      attack_light = locateTemplate("event_attack_light.png", threshold=0.90, offset=(74, 24), click=True)
#               
#      if not attack_blitz and not attack_normal and not attack_light:
#         
#         printResult(False)
#         return False
#            
#      printResult(True)
#      printAction("Confirming that enemy is taken down...")
#      confirmed = False
#      taken_out = False
#      for i in range(10):
#         left_click((200, 200))
#         final_blow = locateTemplate("event_final_blow_button.png", threshold=0.85, offset=(74, 24), click=True)
#         confirm = locateTemplate("event_mission_boss_confirm_button.png", offset=(74, 24), click=True, reuse_last_screenshot=True)
#         decor = locateTemplate("mission_top_decor.png", reuse_last_screenshot=True)
#         time.sleep(1)
#         
#         battle_results = locateTemplate("event_battle_results.png", offset=(74, 24))
#         if battle_results or decor:
#            confirmed = True
#            printResult(True)
#            break
#         
#      if not confirmed:
#         printResult(False)
#      
#      printAction("Checking if \"ask for support\" or \"collect reward\" is available...")
#      success = False
#      for i in range(6):
#         ask_for_support = locateTemplate("event_ask_for_support_button.png", offset=(112, 15), swipe_size=[])
#         reward = locateTemplate("event_get_your_reward_button.png", offset=(115, 14), reuse_last_screenshot=True)
#         
#         if not ask_for_support and not reward:
#            swipe((240, 600), (240, 295))
#            time.sleep(1)
#            
#         elif ask_for_support:
#            printResult(True)
#            success = True
#            printAction("Found \"ask for support\" button. Clicking it...", newline=True)
#            left_click(ask_for_support)
#            break
#            
#         elif reward:
#            printResult(True)
#            success = True
#            printAction("Found \"reward\" button. Clicking it...", newline=True)
#            left_click(reward)
#            break
#         
#      if not success:
#         printResult(False)
#      time.sleep(3)
   
   while(True):
      gotoEventHome()
#      time.sleep(2)
      ref = locateTemplate('event_asked_for_raid_support.png', threshold=0.95,
                           offset=(130, 16), retries=2, click=True, ybounds=(0, 600), swipe_size=[(20, 600), (20, 100)])
      
      printResult(ref)
      
      if ref:
         printAction("Locating the \"face enemy\" button...")
         event_face_enemy = locateTemplate("event_enemies_in_area.png",
                                           offset=(240, 25), threshold=0.92, retries=2, reuse_last_screenshot=True, click=True)
         printResult(event_face_enemy)
         if not event_face_enemy:
            printAction("Unable to locate \"face enemy\" button...")

#         scroll(1000, 0)
#         swipe((200, 20), (400, 20))
         if playEnemy():
            break

      
   notify()


def eventStarkPresident():
   
   print("TONY PRESIDENT EVENT")
   
   for i in range(14):
      
      gotoEventHome()
      
      printAction("Checking all options...", newline=True)
      explore          = locateTemplate("stark_president/explore.png",
                                        offset=(78, 27), threshold=0.92, retries=2, click=True)
      explore_finished = locateTemplate("stark_president/explore_finished.png",
                                        offset=(78, 27), threshold=0.92, retries=2, reuse_last_screenshot=True, click=True)
      landed_search    = locateTemplate("stark_president/landed_search.png",
                                        offset=(78, 27), threshold=0.92, retries=2, reuse_last_screenshot=True, click=True)
      landed_opponent  = locateTemplate("stark_president/landed_opponent.png",
                                        offset=(78, 27), threshold=0.92, retries=2, reuse_last_screenshot=True, click=True)
      printResult(explore or explore_finished or landed_search or landed_opponent)
      
      if explore:
         
         printAction("Hitting \"explore\" button...", newline=True)
         time.sleep(5)
         back_key()
         
      elif explore_finished:
         
         printAction("Exploration finished...", newline=True)
         break
         
      elif landed_search:
         
         printAction("Landed on search spot...", newline=True)
         printAction("Hitting radar watch...")
         radar_watch = locateTemplate("stark_president/radar_watch.png",
                                      offset=(78, 27), threshold=0.92, retries=5, ybounds=(0, 600), swipe_size=[(20, 600), (20, 100)], click=True)
         printResult(radar_watch)
         
         if radar_watch:
            
            
            time.sleep(5)
            back_key()
            
      elif landed_opponent:
            
         printAction("Battle rival...")
         battle_rival = locateTemplate("stark_president/battle_rival.png",
                                       offset=(96, 12), retries=3, swipe_size=[(20, 500), (20, 200)], click=True)
         printResult(battle_rival)
         
         if battle_rival:
               
            printAction("Searching for deck select button...")
            select_deck = locateTemplate("select_deck_button.png", offset=(-144,17), click=True)
            printResult(select_deck)
               
            printAction("Selecting suggested deck...")
            suggested_deck = locateTemplate("stark_president/suggested_deck.png", offset=(150,25), click=True)
            printResult(suggested_deck)
            if suggested_deck:
         
               printAction("Hitting select button...")
               select_button = locateTemplate("select_button.png", offset=(60,16), click=True)
               printResult(select_button)
               if select_button:
                  
                  printAction("Starting battle...")
                  start_battle = locateTemplate("stark_president/start_battle.png",
                                                offset=(96, 17), retries=3, swipe_size=[(20, 500), (20, 200)], click=True)
                  printResult(start_battle)
                  
                  time.sleep(5)
                  back_key()
                  
      else:
         
         for i in range(15):
            notify()
            time.sleep(2)
         
class CycleTimeout(Exception):
   pass

import threading, multiprocessing

class Run( multiprocessing.Process ):
   def __init__(self, function, *args, **kwargs):
      multiprocessing.Process.__init__(self)
      self.function = function
      self.args = args
      self.kwargs = kwargs
           
   def run ( self ):
      self.function(*self.args,**self.kwargs)


class RunUntilTimeout( threading.Thread ):
   def __init__(self, function, timeout, *args, **kwargs):
      threading.Thread.__init__(self)
      self.function = function
      self.timeout = timeout
      self.args = args
      self.kwargs = kwargs      
      
   def run ( self ):
      
      process = Run(self.function, *self.args, **self.kwargs)
#      process.daemon = True
      process.start()
      
      process.join(float(self.timeout))
           
      if process.exitcode == None:
         print("")
         print("*************")
         print("** TIMEOUT **")
         print("*************")
         print("")
         process.terminate()
         
   def exit(self):
      sys.exit()
      

def timeout(function, timeout, *args, **kwargs):
   
   while True:
      print("")
      print("***Starting cycle***")
      print("")
      thread = RunUntilTimeout(function,timeout,*args,**kwargs)
      thread.start()
      thread.join()
            
def custom1():
   
   i = 0
   while True:
           
      
      try:
         if start_marvel_jojanr():
            play_mission((3, 2), 2 * 23)
            exitMarvel()
      except:
         pass
      
      time.sleep(uniform(1, 5))
                
      try:
         if start_marvel_joinge():
            play_mission((3, 2), 2 * 23)
            exitMarvel()
      except:
         pass
      
      time.sleep(uniform(1, 5)) 
         
      try:
         if start_marvel_jollyma():
            play_mission((3, 2), 2 * 23)
            exitMarvel()
      except:
         pass
      
      time.sleep(60 * uniform(35, 55))
      
def custom2():
   
   i = 0
   while True:


      try:
         if start_marvel_joinge():
            play_mission((4, 3), 2 * 23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      

      time.sleep(60 * uniform(1, 3)) 

      try:
         if start_marvel_jojanr():
            play_mission((4, 3), 2 * 23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      

      time.sleep(60 * uniform(1, 3)) 
      
      try:
         if start_marvel_jollyma():
            play_mission((4, 3), 2 * 23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60 * uniform(1, 3))
      
def custom3():
   
   i = 0
   while True:

      try:
         if start_marvel_joinge():
            eventPlay()
            play_mission((3, 2), 2 * 23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60 * uniform(1, 3)) 

      try:
         if start_marvel_jollyma():
            eventPlay()
            play_mission((3, 2), 2 * 23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60 * uniform(1, 3)) 
      
      try:
         if start_marvel_jojanr():
            eventPlay()
            play_mission((3, 2), 2 * 23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60 * uniform(1, 10))

def custom4():
   
   i = 0
   while True:

      try:
         if start_marvel_joinge():
            play_mission((3, 2), 2 * 23)
            notify()
            blockUntilQuit()
      except:
         pass
      
      time.sleep(60 * uniform(1, 3)) 
      
      try:
         if start_marvel_jojanr():
            eventPlay()
            play_mission((3, 2), 2 * 23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60 * uniform(1, 3)) 
      
      try:
         if start_marvel_jollyma():
            eventPlay()
            play_mission((3, 2), 2 * 23)
#            getMyPageStatus()
            exitMarvel()
      except:
         pass
      
      time.sleep(60 * uniform(1, 3))
      
def custom5():

   adjustBrightness()
   while True:
      for i in info.accounts.keys():
         try:
            if startMarvel(i):
               farmMission24FuseAndBoost()
               exitMarvel()
         except:
            pass
         sleepToCharge(60)
         

def custom6():

   adjustBrightness()
   while True:
      for i in info.accounts.keys():
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     farmMission24FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  print("ERROR: Some exception occured when processing %s" % i)
                  print(e)
               sleepToCharge(60)
               
      for i in info.accounts.keys():
            if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
               try:
                  if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  print("ERROR: Some exception occured when processing %s" % i)
                  print(e)
               sleepToCharge(60)
      
      
def custom6b():

   adjustBrightness()
   while True:
      for i in info.accounts.keys():
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     farmMission24FuseAndBoost()
                     notify()
                     blockUntilQuit()
                     exitMarvel()
               except Exception, e:
                  print("ERROR: Some exception occured when processing %s" % i)
                  print(e)
               sleepToCharge(60)
               
      for i in info.accounts.keys():
            if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
               try:
                  if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                     farmMission32FuseAndBoost()
                     notify()
                     time.sleep(30)
#                     blockUntilQuit()
                     exitMarvel()
               except Exception, e:
                  print("ERROR: Some exception occured when processing %s" % i)
                  print(e)
               sleepToCharge(60)
      
def custom7(start_end=False):

   adjustBrightness()
   while True:
      if not start_end:
         for i in info.accounts.keys():
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     farmMission24FuseAndBoost()
                     
                     exitMarvel()
               except Exception, e:
                  print("ERROR: Some exception occured when processing %s" % i)
                  print(e)
               sleepToCharge(60)
      
      start_end = False
      for i in info.accounts.keys():
         if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
            try:
               if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                  farmMission24FuseAndSell()
                  exitMarvel()
            except Exception, e:
               print("ERROR: Some exception occured when processing %s" % i)
               print(e)
            sleepToCharge(60)

def custom8(start_end=False):

   adjustBrightness()
   while True:
      if not start_end:
         for i in info.accounts.keys():
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     farmMission24FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  print("ERROR: Some exception occured when processing %s" % i)
                  print(e)
               sleepToCharge(60)
           
      start_end = False 
      for i in info.accounts.keys():
         if i == 'l33tdump' or i == 'Rolfy86':
            try:
               if randomUserStart(['l33tdump', 'Rolfy86']):
                  farmMission24FuseAndBoost()
                  exitMarvel()
            except Exception, e:
               print("ERROR: Some exception occured when processing %s" % i)
               print(e)
            sleepToCharge(60)
               
      
      for i in info.accounts.keys():
         if i == 'kinemb86' or i == 'MonaBB86':
            try:
               if randomUserStart(['kinemb86', 'MonaBB86']):
                  farmMission24FuseAndBoost()
                  exitMarvel()
            except Exception, e:
               print("ERROR: Some exception occured when processing %s" % i)
               print(e)
               
            sleepToCharge(60)

            
def custom20():
   
   i = Info()
   
   fakeAccounts = { 'AjaxUF': 'UFAjax11',
                'AxelJp83': 'UJAxelUJ83',
                'Cadmus33': 'FFCadmusF',
                'CasonZoo': 'fdZCason',
                'CrazyJett09': 'slHJett09',
                'DamonMJ': 'Damon5lm',
                'DexterOwl': 'Dexter0999',
                'Gunner1972': 'MFGunnerMFMF',
                'HammerJax': 'wfJaxwfD',
                'HarleyQueenz': 'egegCeg9675'}
   
   while True:
      for user, password in fakeAccounts.iteritems():
         try:
            setAndroidId(user)
            startMarvel(user, password=password)
            playNewestMission()
            exitMarvel()
            time.sleep(60)
         except Exception, e:
            print("Failed to process user %s" % user)
            print(e)

def event20():
   
   i = Info()
   
   fakeAccounts = { 'AjaxUF': 'UFAjax11',
                'AxelJp83': 'UJAxelUJ83',
                'Cadmus33': 'FFCadmusF',
                'CasonZoo': 'fdZCason',
                'CrazyJett09': 'slHJett09',
                'DamonMJ': 'Damon5lm',
                'DexterOwl': 'Dexter0999',
                'Gunner1972': 'MFGunnerMFMF',
                'HammerJax': 'wfJaxwfD',
                'HarleyQueenz': 'egegCeg9675'}
   
   while True:
      for user, password in fakeAccounts.iteritems():
         try:
            setAndroidId(user)
            startMarvel(user, password=password)
            try:
               eventPlay()
            except Exception, e:
               print(e)
            playNewestMission()
            exitMarvel()
            time.sleep(60)
         except Exception, e:
            print("Failed to process user %s" % user)
            print(e)


def event1(start_end=False):

   adjustBrightness()
   while True:
      if not start_end:
         for i in info.accounts.keys():
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     farmMission32()                
                     exitMarvel()
               except:
                  pass
               sleepToCharge(60)
         
      for i in info.accounts.keys():
         if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
            try:
               if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
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
            printNotify('Complete trade and event.', 60 * 30)
#            tradeCards(receiver='jollyma', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
           
      try:
         if start_marvel_jollyma():
            printNotify('Complete trade and event.', 60 * 30)
            tradeCards(receiver='l33tdump', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      try:
         if startMarvel('l33tdump'):
            printNotify('Complete trade and event.', 60 * 30)
            tradeCards(receiver='Rolfy86', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      try:
         if startMarvel('Rolfy86'):
            printNotify('Complete trade and event.', 60 * 30)
            tradeCards(receiver='kinemb86', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      try:
         if startMarvel('kinemb86'):
            printNotify('Complete trade and event.', 60 * 30)
            tradeCards(receiver='MonaBB86', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      try:
         if startMarvel('MonaBB86'):
            printNotify('Complete trade and event.', 60 * 30)
            tradeCards(receiver='jojanr', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      try:
         if start_marvel_jojanr():
            printNotify('Complete trade and event.', 60 * 30)
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
            printNotify('Complete trade and event.', 60 * 30)
            tradeCards(receiver='jollyma', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
           
      try:
         if start_marvel_jollyma():
            printNotify('Complete trade and event.', 60 * 30)
            tradeCards(receiver='jojanr', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
           
      try:
         if start_marvel_jojanr():
            printNotify('Complete trade and event.', 60 * 30)
            tradeCards(receiver='joinge', cards_list=trade_list, alignment='all')
            exitMarvel()
      except:
         pass
      
      sleepToCharge(60)
      
      
def event6():

   adjustBrightness()
   while True:
#      notifyWork()
#      printNotify('Complete event for JoInge.', 60*10)
      try:
         startMarvel('JoInge')
         farmMission24FuseAndBoost()
         exitMarvel()
      except:
         pass
      for i in info.accounts.keys():
         if i == 'JollyMa' or i == 'JoJanR':
            try:
               if randomUserStart(['JollyMa', 'JoJanR']):
                  try:
                     eventPlay(find_enraged=True)
                  except:
                     pass
                  farmMission24FuseAndBoost()
                  exitMarvel()
            except:
               pass
            sleepToCharge(30)
               
      for i in info.accounts.keys():
            if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
               try:
                  if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                     try:
                        eventPlay(find_enraged=True)
                     except Exception, e:
                        print(e)
#                     playNewestMission()
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  print(e)
               sleepToCharge(30)


def event7(find_enraged=False):

   adjustBrightness()
   while True:
      for i in info.accounts.keys():
         if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
            try:
               if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                  try:
                     eventPlay(find_enraged=find_enraged)
                  except Exception, e:
                     print(e)
                  farmMission32FuseAndBoost()
                  exitMarvel()
            except Exception, e:
               print(e)
            sleepToCharge(30)
               
      for i in info.accounts.keys():
            if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
               try:
                  if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                     try:
                        eventPlay(find_enraged=find_enraged)
                     except Exception, e:
                        print(e)
#                     playNewestMission()
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  print(e)
               sleepToCharge(30)


      

def event8():

   def func():

      adjustBrightness()
      while True:
         try:
            if startMarvel('JoInge'):
               try:
                  eventStarkPresident()
                  farmMission32FuseAndBoost()
                  exitMarvel()
               except Exception, e:
                  print(e)
         except Exception, e:
            print(e)
         sleepToCharge(30)
         for i in info.accounts.keys():
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     eventStarkPresident()
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  print("ERROR: Some exception occured when processing %s" % i)
                  print(e)
               sleepToCharge(60)
              
         for i in info.accounts.keys():
            if i == 'l33tdump' or i == 'Rolfy86':
               try:
                  if randomUserStart(['l33tdump', 'Rolfy86']):
                     eventStarkPresident()
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  print("ERROR: Some exception occured when processing %s" % i)
                  print(e)
               sleepToCharge(60)
                  
         
         for i in info.accounts.keys():
            if i == 'kinemb86' or i == 'MonaBB86':
               try:
                  if randomUserStart(['kinemb86', 'MonaBB86']):
                     eventStarkPresident()
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  print("ERROR: Some exception occured when processing %s" % i)
                  print(e)
                  
               sleepToCharge(60)

   timeout(func,90*60)
      
      


def tradeToJollyMa():

   trade_list = ['rare+_ironman'] * 10
   adjustBrightness()
          
   for i in info.accounts.keys():
         if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
            try:
               if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                  tradeCards(receiver='JollyMa', cards_list=trade_list, alignment='tactics')
                  exitMarvel()
            except:
               pass
            sleepToCharge(30)
   notify()
      


def gimpScreenshot():
   
   Popen("gimp %s/screenshot_%s.png" %(TEMP_PATH, ACTIVE_DEVICE), stdout=PIPE, shell=True)

if __name__ == "__main__":

   i = Info()

#   setActiveDevice("10.42.0.52:5558",True)
#   custom20()
#   playNewestMission()
   
#   setAndroidId('AxelJp83','8583688437793838')
#   custom20()

   setActiveDevice("10.42.0.52:5558")
#   setActiveDevice("localhost:5558",True)
#    setActiveDevice("76.250.209.149:5558",True)
   
#    startMarvel('kinemb86')
#   setActiveDevice("10.42.0.52:5558", youwave=True)
#    setActiveDevice("localhost:5558",True)
   createNewFakeAccount(referral="test")
#    startMarvel('Account1')
#   createNewFakeAccount()
#    setActiveDevice("0123456789ABCDEF", youwave=False)
#    event7()
#   eventStarkPresident()
#    setActiveDevice("10.0.0.41:5555", youwave=False)
#    event8()
#   getMyPageStatus()
#    locateTemplate("mission_2_4.png")
#   setActiveDevice("00190e8364f46e", youwave=False)
#   event7(True)
#   take_screenshot_adb()
#   custom20()
#   checkRaid()
#    playNewestMission()
#   startFakeAccounts()
#   createAccounts()
#   startMarvel('JoInge')
#   import gui.gui as gui
#   gui.main()
#   boostCard( 'uncommon_ironman', all_feeder_cards, alignment='tactics' )
#   fuseAndBoost('uncommon_ironman',
#                all_feeder_cards,
#                fuse_alignment='tactics')
#   fuseCard('uncommon_ironman', alignment='tactics')
#   test()
#   tradeCards(receiver='jollyma', cards_list=['rare+_ironman'], alignment='all')
#   tradeCards(receiver='jollyma', cards_list=['ssr+_thing_stoneskin', 'sr+_spiderwoman_doublelife', 'sr+_spiderwoman_doublelife', 'sr+_spiderwoman_doublelife', 'sr+_spiderwoman_doublelife'], alignment='all')
#   tradeToJollyMa()
#   selectCard('rare+_ironman', alignment='all')
#   event1()
#   test()
#   custom6()
#   runAll32()
#   custom4()
#   play_mission((3,2))


#    play_mission((2,4))

#    eventPlay()
#   eventKillEnemies()
#   eventFindEnemy()
#   eventPlayMission()
#    eventPlay()
#    locateTemplate("android_error.png", threshold=0.9, offset=(65,31))
#   runAll()
#   startAndRestartWhenQuit()
#   getMyPageStatus()
#    farmMission24FuseAndBoost()
#   replay_all_macros()
#   getIMEI() 
#   replay_all_macros()
#   find_mission()
#   fuse_ironman()
   #pass
#   i = Info()
#   s = "Gunner1972"
##   setAndroidId(s)
##   startMarvel(s,password=i.fakeAccounts[s])
#   playNewestMission()

   
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
