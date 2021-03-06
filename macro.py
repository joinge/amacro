#cnee --record --events-to-record -1 --mouse --keyboard -o /tmp/xnee.xns -e /tmp/xnee.log -v

#cnee --record --seconds-to-record 150 --mouse --keyboard -o joinge.xns -e joinge.log -v
from __future__ import print_function
from Accounts import account
from Devices import device
from Users import user
from distutils import dir_util
from nothreads import myRun, myPopen
from printing import myPrint, printAction, printResult, printNotify, printQueue, \
   printLog
from random import uniform
from subprocess import Popen, PIPE, STDOUT
import ast
import cv2
from amacro import log
import multiprocessing
import numpy as np
import os
import re
import select
import shutil
import sys
import threading
import threads
import time
import urllib2

GLOBAL_DEBUG = False # Extremely verbose output

SCREEN_PATH          = './screens'
TEMP_PATH            = './tmp'
ANDROID_UTILS_PATH   = './contents/android' 
LOG_STDOUT           = 'log.log'
LOG_STDERR           = 'log.log'
WOH_NAME             = 'com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android'

# STDOUT_ALTERNATIVE = None
ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
abc = 'abcdefghijklmnopqrstuvwxyz'
num = '0123456789'
hex = num+'abcdef'

# sys.path.append("./local/win32")

try:    os.mkdir(TEMP_PATH)
except: pass

if os.name == "posix":
   ESC = "\\"
#   sys.path.append("./local/linux64/lib/python")
elif os.name == "nt":
   ESC = "^"
#   sys.path.append("./local/win32/Python27")
#    Popen('mode con: cols=140 lines=70', stdout=PIPE, adbShell=True).stdout.read()
#    Popen('cmd mode con: cols=140', stdout=PIPE, adbShell=True).stdout.read()
else:
   myPrint("WARNING: Unsupported OS")
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


# set up log to file - see previous section for more details
log.basicConfig(level=log.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=TEMP_PATH+'/macro.log',
                    filemode='a')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = log.StreamHandler()
console.setLevel(log.INFO)
# set a format which is simpler for console use
formatter = log.Formatter('%(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
log.getLogger('').addHandler(console)


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
         myPrint("ERROR: Unable to open stats.txt")
      
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
 

# The info object reads itself from the info folder!!! 
class Info():
   def __init__(self):
      self.initiated = False
   
   def get(self, key):
      
      self.updateInfo()
      
      try:
         if getattr(self, key):
            return getattr(self, key)
      except:
         return None
   
   def set(self, key, value, group=None):
      
      self.updateInfo()

      try:
         if group:
            setattr(getattr(self, group), key, value)
         else:
            setattr(self, key, value)
         self.write()
         return True
      except:
         return None
      
   def updateInfo(self):
      
      # Only want to run this once
      if self.initiated:
         return
      else:
         self.initiated = True
      
      try:
         files = os.listdir('info')
      except:
         os.mkdir('info')
      
      first_run = True
      for file in files:
         
         s = open('info/%s' % file, 'r')
         
         attr_name = re.sub('.txt', '', file)
   
         if first_run:
            myPrint("Reading Info attributes")
            first_run= False
            
         # Make these settings class variables
         setattr(self, attr_name, ast.literal_eval(s.read()))
         s.close()
      
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
         if not hasattr(self,attr_name) and first_run:
            myPrint("Reading Info attributes")
         # Make these settings class variables
         setattr(self, attr_name, ast.literal_eval(s.read()))
         s.close()
         first_run= False
      
#      if os.path.getsize('stats.txt') > 0:
#         s = open('stats.txt','a')

   def write(self):
      
      from pprint import pprint
            
      for key in self.__dict__.keys():
      
         s = open('info/%s.txt' % key, 'w')
         pprint(getattr(self, key), stream=s)
         s.close()

     
# IMEI = 358150 04 524460 6
# 35     - British Approvals Board of Telecommunications (all phones)
# 
# 524460 - Serial number
# 6      - Check digit

def getIMEI():
   output = device.adbShell('dumpsys iphonesubinfo | grep Device | sed s/".*= "//')
   myPrint(output)
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

  
emails = [
'gmail.com',
'yahoo.com',
'hotmail.com'
 ]

nick_list = []
def getBaseName():
   
# for i in {1..20}; do curl -L http://www.spinxo.com/ | sed -r -n "s/^\s+([a-zA-Z]+)<\/a><\/li>.*$/\1/p" >> data/nick_seeds_joey.txt; done
# cat info/nick_seeds.txt | sort -R > ./info/nick_seeds2.txt
   global nick_list
   
   printAction("Fetching nick seeds...", newline=True)
   
   # NEW APPROACH: Fetch nicks online whenever our nicks_list is empty   
   if len(nick_list) == 0:
      
      printAction("   Nick list is empty! Fetching a new one from http://www.spinxo.com...")
      
      try:
         # Fetch contents of the nick generator page spinxo.com
         nick_seed_page = urllib2.urlopen('http://www.spinxo.com/').read()
      
         # Parse is and retrieve the list of nicks between 4-10 characters long
         nick_list = re.findall('\s+([A-Z][a-zA-Z]{3,9})</a></li>', nick_seed_page)
         
         if len(nick_list) == 0:
            printResult(False)
            printAction('Unable to parse the internet page. Internet problem?', newline=True, msg_type='error')
            return None
         
         printResult(True)
         
      except:
         printResult(False)
         return None    
      
   name = nick_list.pop(int(np.random.uniform(0,len(nick_list)-1e-9)))
   
   printAction("   Selected nick:")
   myPrint(name)

#   # OLD APPROACH
#   current_nick = user.getCurrent()
#   f = open('./data/nick_seeds_%s.txt'%current_nick.lower(), 'r')
#   all_names = f.readlines()
#   name = all_names[0]
#
#   name = re.sub('\\n','',name)
#   name = re.sub('\\r','',name)
#   name = re.sub('\\t','',name)
#   f.close()
#
#   f = open('./data/nick_seeds_%s.txt'%current_nick.lower(), 'w')
#   f.write( "".join(all_names[1:]) )
#   f.close()
   
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
#       myPrint(i)
      
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
   
def rebuildAPK(newid="a00deadbeef"):
   
   # Got to the source folder
   os.chdir('woh')
   
   WORK_DIR       = 'build'
   WORK_OUTPUT    = WORK_DIR+'/output_current'
   WORK_UNPACKED  = WORK_DIR+'/unpacked'
   
   if not os.path.exists(WORK_DIR):
      os.mkdir(WORK_DIR)
   
   # Remove old work dir
   if os.path.exists(WORK_OUTPUT):
      shutil.rmtree(WORK_OUTPUT)

   printAction("   Copy prepatched code to work dir...", newline=True)
   # Step 1. Copy .smali ref code to work directoy
   shutil.copytree('output_ref', WORK_OUTPUT)
   
   if not os.path.exists(WORK_UNPACKED):
      shutil.copytree('unpacked', WORK_UNPACKED)
   
   printAction("   Find and replace Android IDs in the disassembled code...", newline=True)
   # Step 2. Replace all occurences of tag a00beadbeef with Android ID of choice 
   fileList = []
   for root, subFolders, files in os.walk(WORK_OUTPUT):
      for file in files:
         fileParts = file.split('.')
         if len(fileParts) > 1 and fileParts[1] == "smali":
            # Small files, handle in memory:
            with open(root+'/'+file, 'r') as smali_file:
               text_in  = smali_file.read()
            
            text_out = re.sub('a00beadbeef', newid, text_in)
            
            with open(root+'/'+file, 'w') as smali_file:
               smali_file.write(text_out)
             
   printAction("   Reassemble code back to bytecode...", newline=True)
   # Step 3: Assemble
   myPopen('java -jar ./lib/smali-2.0b2.jar -o %s/classes.dex %s'%(WORK_UNPACKED, WORK_OUTPUT))
   # Step 4: Remove signature, we will resign later (needed?)
   try:
      shutil.rmtree(WORK_UNPACKED+'/META-INF')
   except:
      pass
  
   printAction("   Zip the code into an APK...", newline=True)
   # Step 5: Zip up apk

   shutil.make_archive(WORK_DIR+'/woh_unaligned', 'zip', WORK_UNPACKED)
   try:
      os.remove(WORK_DIR+'/woh_unaligned.apk')
   except:
      pass
   os.rename(WORK_DIR+'/woh_unaligned.zip', WORK_DIR+'/woh_unaligned.apk')
#   else:   
#      os.chdir('unpacked')
#      myPopen('zip -r - . > ../WOHU.apk')
#      os.chdir('..')

   printAction("   Sign the APK...", newline=True)
   # Step 6: generate a keystore if one doesn't already exist
#    if not os.path.exists('./keystore'):
#       myPopen('keytool -genkey -v -keystore ./keystore -alias patch -keyalg RSA -keysize 2048 -validity 10000 -storepass changeme -keypass changeme')
   myPopen('jarsigner -verbose -sigalg MD5withRSA -digestalg SHA1 -keystore ./keystore -storepass changeme %s patch'%(WORK_DIR+'/woh_unaligned.apk'))

   printAction("   Zipalign the APK...", newline=True)
   myPopen('zipalign -f -v 4 %s/woh_unaligned.apk %s/woh_aligned.apk'%(WORK_DIR, WORK_DIR))

   printAction("   Reinstall the APK...", newline=True)
   os.chdir('..')
   device.adb('uninstall %s'%WOH_NAME)
   device.adb('install woh/%s/woh_aligned.apk'%WORK_DIR, stderr=STDOUT)
   
   printAction("   Finished. New ID:")
   myPrint(newid)
   
   
def createNewFakeAccount(referral="", draw_ucp=False):
      
   name_base  = getBaseName()
   email_base = getBaseName().lower()
   
   old_dir = os.getcwd()
      
   # Set new Android ID and start WoH
   new_android_id = newAndroidId()
   setAndroidId(name_base,new_android_id)
#   unlock_phone()
   if not device.isAndroidVM():
      clearMarvelCache()
   launch_marvel()
   
   printAction("Searching for login screen...")
   login_screen = locateTemplate('login_screen.png', threshold=0.95, retries=60, interval=1)
   printResult(login_screen)
   
   if login_screen:
      
      randNums = ''.join(np.random.uniform(9, size=int(np.random.uniform(2, 4))).astype(int).astype('str'))
      emailbase = email_base + randNums
      emailend = '@' + emails[int(np.random.uniform(0,len(emails)-1e-9))]
      
#       randABC = ''.join([ABC[0][j] for j in np.random.uniform(0, 26, size=int(np.random.uniform(3))).astype(int)])
#       randAbc = ''.join([abc[0][j] for j in np.random.uniform(0, 26, size=int(np.random.uniform(3))).astype(int)])
      
      tmp = ['0123456789', ABC, abc]
      tmp2 = ''.join(i for i in tmp)
      
      tmp = ['0123456789', abc]
      tmp3 = ''.join(i for i in tmp)
            
      c = np.array(login_screen)
   
      if device.getInfo('screen_density') != 160:
         myPrint("ERROR: Not implemented")
         return 2
         
      
      leftClick((140, 160) + c) # Login Mobage
      time.sleep(0.3)
      leftClick((206, 160) + c) # Login button
      
      
      printAction("Searching for sign up screen...")
      signup_screen = locateTemplate('login_signup.png', threshold=0.95, retries=5, interval=2)
      printResult(signup_screen)
      
      if not signup_screen:
         return 1

      success = False
      c = np.array(signup_screen)
      for i in range(3):
         
         if i!=0:         
            emailbase = emailbase + tmp3[int(np.random.uniform(0, len(tmp3)-1e-9))]    
            printAction("Wiping both fields...", newline=True)
            # Wipe both fields:
            leftClick((244, 73) + c) # Email field
            if i!=0:
               for i in range(50): backspace()
            leftClick((244, 118) + c) # Password field
            if i!=0:
               for i in range(50): backspace()  
               
         email = emailbase + emailend
         password = ''.join([tmp2[j] for j in np.random.uniform(0, len(tmp2)-1e-9, size=int(np.random.uniform(8,14))).astype(int)])
         
         printAction("Trying with email:")
         myPrint(email)
         leftClick((244, 73) + c) # Email field
         time.sleep(0.3)
         enterText(email)
         if device.isYouwave():
            backspace()
         
         printAction("Entering password:")
         myPrint(password)
         leftClick((244, 118) + c) # Password field
         time.sleep(0.3)
         
         # Like usual youwave has problems here...
         if device.isYouwave():
            enterText('a')
            for i in range(len(email)):
               right_arrow()
            for i in range(len(email) + 2):
               backspace()
         enterText(password)
         if device.isYouwave():
            backspace()
         leftClick((205, 159) + c) # Signup button
         
         printAction("Searching for \"Last Step\" screen...")
         signup_last_screen = locateTemplate('login_signup_last.png', threshold=0.95, retries=20, interval=1)
         printResult(signup_last_screen)
         
         if signup_last_screen:
            success = True
            break
         
      leftClick((20,140) + c) # Uncheck "Get Mobage news and updates" button
            
      # Now we must handle the fact that the nick may be invalid
      success = False
      printAction("Waiting for tutorial start...")
      username = ''
      for i in range(3):
         
         leftClick((232,105)+c) # Nick field         
         time.sleep(0.3)
         
         if i==0:
            if device.isYouwave():
               enterText('a')
               for i in range(len(email_base+randNums)+2):
                  right_arrow()            
   
               for i in range(len(email_base+randNums)+2+len(password)):
                  backspace()
            else:
               for i in range(len(email_base+randNums)+2):
                  backspace()
                  
            enterText(name_base)
            username = name_base
            if device.isYouwave():
               backspace()
         else:
            new_char = tmp2[int(np.random.uniform(0, len(tmp2)-1e-9))]
            enterText(new_char)
            username = username + new_char
            if device.isYouwave():
               backspace()            
         
         leftClick((142,172) + c) # Save and Play button
         
#          invalid_nick  = locateTemplate('login_signup_invalid_nick.png', threshold=0.95)
         time.sleep(5)
         login_box     = locateTemplate('login_signup_part.png', threshold=0.95)
         
#          if invalid_nick:
#             leftClick((232,105)+c) # Nick field
#             enterText(tmp2[np.random.uniform(0, len(tmp2)-1e-9)])
            
         if not login_box:
            success = True
            break
         
      if not success:
         printResult(False)
         myPrint("ERROR: Unable to enter valid nick")
         return 1

      printResult(True)
      
      current_time = time.strftime('%Y-%m-%d %H:%M:%S')
      account.add(username, password=password, email=email, type='bot', coins=0, refcode=referral,
                  android_id=new_android_id, owner='default', created=current_time, device='S3 (VM)')

      printAction("Running through the tutorial like mad!!!")
      for i in range(40):
         locateTemplate('mobage_ad.png',              offset=(85,14),  click=True)
         locateTemplate('tutorial_skip.png',          offset=(49,11),  click=True, reuse_last_screenshot=True)
         if locateTemplate('tutorial_understood.png', offset=(132,7),  click=True, reuse_last_screenshot=True):
            break
         leftClick((235, 110))
      
      if not locateTemplate('tutorial_another_card.png',   offset=(132,8),  click=True, retries=20):
         print("ERROR: Unable to find \"draw another card\" button")
         return 1
         
      success = False
      for i in range(20):
         if locateTemplate('tutorial_all_right.png',   offset=(127,10), click=True):
            success = True
            break
         leftClick((235, 110))
      if not success:       
         print("ERROR: Unable to find \"all right\" button")
         return 1
         
      def select_and_confirm():
         success = False
         for i in range(20):
            swipe((240, 500), (240, 100))
            if locateTemplate('tutorial_wreck_villains.png', offset=(123,10), click=True):
               success = True
               break
         if not success:
            print("ERROR: Unable to find \"wreck villains\"")
            return 1
         
         if not locateTemplate('tutorial_confirm_selection.png', offset=(123,10), retries=20, click=True):
            print("ERROR: Green Goblin FIGHT button not found")
            return 1
      
      select_and_confirm()
      
      for i in range(20):
         if locateTemplate('tutorial_battle_auto.png', offset=(40,13), click=True):
            if locateTemplate('tutorial_battle_end.png', offset=(61,15), click=True, retries=5):
               break
      
      success = False
      for i in range(20):
         if locateTemplate('tutorial_battle_green_goblin.png', offset=(110,10), click=True):
            success = True
            break
         leftClick((240,115))
      if not success:
         print("ERROR: Unable to battle Green Goblin")
         return 1         
      
      success = False
      for i in range(20):
         leftClick((240,110))
         if locateTemplate('tutorial_got_this_one.png',   offset=(123,9),  click=True):
            success = True
            break
      if not success:
         print("ERROR: Unable to find \"got this one\" button")
         return 1         
         
      select_and_confirm()
      
      if locateTemplate('tutorial_promotion_codes.png',offset=(128,10), click=True):
         printResult(True)
         printAction("Time for referral service BABY!!!")
      else:
         print("ERROR: Unable to locate promotion code button")
         return 1         
      
      printAction("Entering the referral code...")
      success = False
      for i in range(2):
#         locateTemplate('tutorial_referral.png', offset=(124,13), click=True, reuse_last_screenshot=True)
         
         ok = locateTemplate('tutorial_ok.png', offset=(29,11), retries=20, interval=.5, swipe_size=[(240, 550), (240, 150)])

         if ok:
            text_field = ok + np.array((30,-33))
            leftClick(text_field)
            time.sleep(1)
            
            if i!=0:         
               for i in range(10): backspace()

            enterText(referral)
            if device.isYouwave():
               backspace()
         
            leftClick(ok)
            time.sleep(4)
            back = locateTemplate('tutorial_back.png', offset=(118,16), click=True, retries=25, interval=.5, swipe_size=[(240, 550), (240, 150)])
            if back:
               success = True
               break
            
      printResult(success)
      if not success:
         myPrint("ERROR: Unable to process referral code")
         return 2 # If the service gets this far without working, it's probably best to call it off.

      lets_do_this = locateTemplate('tutorial_lets_do_this.png', offset=(137,11), click=True, retries=3)
      if not lets_do_this:
         myPrint("ERROR: Unable to process referral code", msg_type='error')
         return 2
         
      printAction("Registering device...")
      register_device = None
      for i in range(10):
         register_device = locateTemplate('tutorial_register_device.png', offset=(124,11), click=True)
         if register_device:
            break
         leftClick((240,150))

      if not register_device:
         printResult(False)
         myPrint("ERROR: Unable to find register device button!")
         return 2 # If the service gets this far without working, it's probably best to call it off.
      
      agree = locateTemplate('tutorial_agree.png', offset=(124,11), click=True, retries=5, interval=3)
      printResult(agree)

      if not agree:
         printResult(False)
         myPrint("ERROR: Unable to find register device button!")
         return 2 # If the service gets this far without working, it's probably best to call it off.

      printResult(True)
      if not draw_ucp:
         locateTemplate('tutorial_mypage.png', offset=(45,8), click=True, retries=3, interval=3)
         printAction("FINISHED!!!", newline=True)
         return 0
      
      printAction("Drawing UCP...")
      
      presents = locateTemplate('tutorial_presents.png', offset=(102,14), click=True, retries=5, interval=3)
      printResult(presents)

      if not presents:
         myPrint("ERROR: Unable to find presents button!")
         return 4

      claim_all = locateTemplate('presents_claim_all.png', offset=(44,10), click=True, retries=5, interval=3)
      printResult(claim_all)
      
      if not claim_all:
         myPrint("ERROR: Unable to find \"Claim All\" button!")
         return 4

      card_pack = locateTemplate('card_pack_button.png', offset=(45,18), click=True, retries=5, interval=3)
      printResult(card_pack)
      
      if not card_pack:
         myPrint("ERROR: Unable to find \"Card Pack\" button!")
         return 4

      basic_tab = locateTemplate('card_pack_basic_tab.png', offset=(45,12), click=True, retries=5, interval=1, swipe_size=[(240, 500), (240, 295)], xbounds=(0,400))
      printResult(basic_tab)
      
      if not basic_tab:
         myPrint("ERROR: Unable to find \"Basic\" tab!")
         return 4

      get_ucp = locateTemplate('card_pack_get_ucp.png', offset=(89,8), click=True, retries=7, interval=1, swipe_size=[(20, 500), (20, 295)])
      printResult(get_ucp)
      
      if not get_ucp:
         myPrint("ERROR: Unable to find \"Get Ultimate Card Pack\" button!")
         return 4

      if not locateTemplate('tutorial_skip.png',  offset=(49,11),  click=True, retries=5, interval=1):
         leftClick((150,150))
         
      time.sleep(7)      
      device.takeScreenshot(SCREEN_PATH+'/ucp_draws/'+user.getCurrent()+'/'+username+'.png')
      leftClick((150,150))

      printAction("FINISHED", newline=True)
      
      return 0
      
def createMultipleNewFakeAccounts(iterations, referral="", description="", interval=(0,0), never_abort=True, draw_ucp=False):
   
   def printSummary():
      printAction("",newline=True)
      printAction("SUMMARY",newline=True)
      if retcode == 4:
         printAction("UCP draw failed.",newline=True)
         if not never_abort:
            return False
         else:
            printAction("User asked to never abort. Will keep going...",newline=True)
      
      if retcode == 3:
         printAction("Referral script crashed! Bad bad bad!",newline=True)
         if not never_abort:
            return False
         else:
            printAction("User asked to never abort. Will keep going...")
      
      elif retcode == 2:
         printAction("Referral script asked to abort. Investigate!",newline=True)
         if not never_abort:
            return False
         else:
            printAction("User asked to never abort. Will keep going...")

      elif retcode == 1:
         printAction("Referral script failed but nothing serious. Will continue.",newline=True)
         
      elif retcode == 0:  
         printAction("All good! Ready for more action!",newline=True)
         
      else:
         printAction("WARNING: This return code is unknown",newline=True)
      
      for i in range(len(retcode_counts)):
         retcode_count = retcode_counts[i]
         printAction("",newline=True)
         
         if description == "":
            printAction("Refcode:       %s"%referral[i], newline=True)
         else:
            printAction("Refcode:       %s (%s)"%(referral[i],description[i]), newline=True)
            
         printAction("Total Summary: %d successes, %d soft errors, %d bad errors, %d crashes"%(retcode_count[0],retcode_count[1],retcode_count[2],retcode_count[3]), newline=True)
         printAction("Total Summary: %d referrals made successfully."%(retcode_count[0]+retcode_count[4]), newline=True)
      
      return True
   
   
   if type(iterations) == int and type(referral) == str:
      iterations = [iterations]
      referral   = [referral]
      
      
   retcode_counts = []
   for iteration, ref_code in zip(iterations, referral):
   
      retcode_counts.append([0,0,0,0,0])
      i=0
      watchdog = int(1.3*iteration)
      while iteration > 0 and watchdog > 0:
         i = i + 1
   #    for i in range(iterations):
         
         myPrint("")
         myPrint("REFERRAL SERVICE: Iteration %d"%i)
         
         ensureStealth()
         try:
#            if user.getCurrent() == 'Chris':
#               retcode = threads.myRun(createNewFakeAccount, timeout=10*60, referral=ref_code, draw_ucp=draw_ucp)
#            else:
            retcode = createNewFakeAccount(referral=ref_code, draw_ucp=draw_ucp)
         except Exception, e:
            printLog(e, msg_type='error')
            retcode = 3
         
#          retcode = myRun(createNewFakeAccount, timeout=3.5*60, referral=ref_code, draw_ucp=draw_ucp)
#          try:
#             retcode = createNewFakeAccount(referral=ref_code, draw_ucp=draw_ucp)
#          except:
#             retcode = 3
            
         if retcode == None:
            retcode = 3
            
         # Decrement iterations left the ref. was successful
         if retcode == 0 or retcode == 4:
            iteration = iteration - 1
         
         # Decrement watchdog regardless
         watchdog = watchdog - 1
         retcode_counts[-1][retcode] = retcode_counts[-1][retcode] + 1
         
         try:
            if not printSummary():
               break 
         except Exception, e:
            printLog(e, msg_type='error')
            printAction("ERROR: Unable to print summary")
            
         wait_time = np.random.uniform(interval[0]*60,interval[1]*60)
         
         printAction("Waiting for roughly %d minutes and %d seconds..."%(wait_time/60,wait_time%60),newline=True)
         
         time.sleep(wait_time)
         
def updateVPN():
   
   printAction('Starting VPN...')
   
   device.adbShell('am force-stop com.privateinternetaccess.android')
   
   device.adbShell('echo "am start -n com.privateinternetaccess.android/.LauncherActivity" \| su')
   
   locateTemplate('vpn_checkbox')
   
   time.sleep(8)
   
   homeKey()
   
   print("hello")
   
   
      # am start -n com.privateinternetaccess.com/.LauncherActivity
   # am force-close com.privateinternetaccess.com
   
   # In /data/data/com.privateinternetaccess.android/shared_prefs/com.privateinternetaccess.android_preferences.xml
      # <?xml version='1.0' encoding='utf-8' standalone='yes' ?>
      # <map>
      # <string name="lport"></string>
      # <boolean name="autoconnect" value="true" />
      # <string name="onBootProfile">4335cfe0-4069-40cb-9e19-a4a91016634d</string>
      # <string name="rport">auto</string>
      # <boolean name="autostart" value="true" />
      # <string name="selectedregion">germany</string>
      # </map>
      
   # MainActivity.xml
      # <?xml version='1.0' encoding='utf-8' standalone='yes' ?>
      # <map>
      # <string name="password">spzCg2PwVy</string>
      # <string name="login">p1526501</string>
      # </map>
      
def ensureStealth():
   
   printAction('Stealth check', newline=True)
   
   ensureValidIP()
   setVPNFirewall()
   
      
def ensureValidIP(recursing=False):
   
   host_ip = myPopen('wget http://www.joinge.net/getmyip.php -q -O -')
   printAction('   Host IP')
   print(host_ip)
   
   vm_ip = device.adbShell('"wget http://www.joinge.net/getmyip.php -q -O -"')
   printAction('   Android IP (%s)'%device.active_device)
   print(vm_ip)
   
   # This sanity check doesn't ensure valid IP range but should be sufficient
   filtered_vm_ip = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', vm_ip)
   
   if not filtered_vm_ip:
      printAction('   VM IP sanity check...', res=False)   
      print('FATAL ERROR: VM IP does not seem to be sane.')
      
      if recursing:
         print('Unable to recover. Aborting.')
         sys.exit()
      else:
         updateVPN()
         setVPNFirewall()
         ensureValidIP(True)
   
   else:
      printAction('   VM IP sanity check...', res=True)
   
   if host_ip == vm_ip:
      printAction('   IPs differ?', res=False)   
      print('FATAL ERROR: IPs are identical.')
      
      if recursing:
         print('Unable to recover. Aborting.')
         sys.exit()
      else:
         updateVPN()
         setVPNFirewall()
         ensureValidIP(True)
      
   else:
      printAction('   IPs differ?', res=True)
   

def setVPNFirewall(allow_only_current_vpn_server = True):
   
   printAction('   Setting up VPN firewall...')
   device_no = device.getInfo('deviceNo')
   
   try:
      os.mkdir(TEMP_PATH+'/pia%d'%device_no)
   except:
      pass

   curdir = os.getcwd()
   os.chdir(TEMP_PATH+'/pia%d'%device_no)
   #myPopen('rm *.ovpn *.crt *.vpn *.zip', stderr='devnull')
   myPopen('rm *', stderr='devnull')
#   myPopen('wget -q https://www.privateinternetaccess.com/openvpn/openvpn.zip')

   pia_ip_list = []

   if allow_only_current_vpn_server:
      vm_ip = device.adbShell('"wget http://www.joinge.net/getmyip.php -q -O -"')
   
      # This sanity check doesn't ensure valid IP range but should be sufficient
      filtered_vm_ip = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', vm_ip)
      
      if filtered_vm_ip:
         pia_ip_list = [vm_ip]
      else:
         print('ERROR: Unable to read current VPN IP')
         sys.exit()
      
   else:
      # Fetch and extract new data (if it was changed)
      myPopen('wget -q -O openvpn.zip https://www.privateinternetaccess.com/openvpn/openvpn.zip')
      myPopen('unzip -q openvpn.zip')
      
      # Perform DNS lookups to find each server's IPs
      pia_servers = myPopen('grep -h "remote " *ovpn | sort')
      
      for pia_server in re.findall('remote\s([a-z\.-]+)\s[0-9]+', pia_servers):
         dns_ip_string = myPopen('dig %s A +short | sort'%pia_server)
         dns_ips = re.split('\n',dns_ip_string)
         dns_ips.pop(-1)
         pia_ip_list.extend(dns_ips) 
         
      pia_ip_list.sort()

   # Start building iptables script - starts by overwriting old file
   iptables_file = open('iptables.vpn', 'w')
   
   print('iptables -F',                               file=iptables_file)
   print('iptables -A INPUT  -i tun+ -j ACCEPT',      file=iptables_file)
   print('iptables -A OUTPUT -o tun+ -j ACCEPT',      file=iptables_file)
   print('iptables -A INPUT  -s 127.0.0.1 -j ACCEPT', file=iptables_file)
   print('iptables -A OUTPUT -d 127.0.0.1 -j ACCEPT', file=iptables_file)
   
   for ip  in pia_ip_list:
      print('iptables -A INPUT  -s %s -j ACCEPT'%ip, file=iptables_file)
      print('iptables -A OUTPUT -d %s -j ACCEPT'%ip, file=iptables_file)

   # Add access for host-only network
   print('iptables -A INPUT  -s 192.168.1%d.1 -j ACCEPT'%device_no, file=iptables_file)
   print('iptables -A OUTPUT -d 192.168.1%d.1 -j ACCEPT'%device_no, file=iptables_file)

   # Stop anything not from PIA or internal or localhost
   print('iptables -A INPUT -j DROP', file=iptables_file)
   print('iptables -A OUTPUT -j DROP', file=iptables_file)

   iptables_file.close()
   
   device.adb('push iptables.vpn /sdcard/macro/', stdout='devnull', stderr='devnull', log=False)
   device.adbShell('echo "sh /sdcard/macro/iptables.vpn" \| su')

   os.chdir(curdir)

   printResult(True)
   
#       for i in range(10):
#          
# 
#    
#    enterText(user)      
#    
#    if YOUWAVE:
#       backspace()
#       
#    if info.getAdbInfo('screen_density') == 240:
#       leftClick((76, 174) + c) # Mobage password field
#    else:
#       leftClick((142, 114) + c) # Mobage password field
#    if YOUWAVE: # youwave screws this up. Need to insert text, then erase it once
#       enterText('a')
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
#       enterText(password)
#    else:
#       enterText(info.account[user])
#       
#    if YOUWAVE:
#       backspace()
#       
#    if info.getAdbInfo('screen_density') == 240:
#       leftClick((313, 237) + c) # Login button
#    else:
#       leftClick((207, 157) + c) # Login button
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
#               myPrint(
#               Popen("adb %s adbShell \
#                     \" rm -r /sdcard/pull_tmp;\
#                        mkdir /sdcard/pull_tmp;\
#                        mkdir /sdcard/pull_tmp/files;\
#                        mkdir /sdcard/pull_tmp/shared_prefs\";\
#                        %s \
#                     adb %s pull /sdcard/pull_tmp ./users/%s\
#                     " % (ADB_ACTIVE_DEVICE, adb_copy_to_sdcard_cmd, ADB_ACTIVE_DEVICE, user),
#                     stdout=PIPE, adbShell=True).stdout.read())
#
#            time.sleep(1)
#            ad  = locateTemplate('home_screen_ad.png', offset=(90, 20), threshold=0.95)
#            ad2 = locateTemplate('home_screen_ad2.png', offset=(90, 20), threshold=0.95, reuse_last_screenshot=True)
#            if ad or ad2:
#               if ad:
#                  leftClick(ad) # kills ads
#               if ad2:
#                  leftClick(ad2) # kills ads
#               time.sleep(1)
#            
##            leftClick((346,551)) # kills ads
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
#      myPrint(i)
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


def notify():
   
#   Popen("mplayer audio/ringtones/BentleyDubs.ogg >/dev/null 2>&1", stdout=PIPE, adbShell=True).stdout.read()

   device.adbShell("echo 'echo 100 > /sys/devices/virtual/timed_output/vibrator/enable' \| su")
   
   device.adbShell('echo "echo 100 > /sys/devices/virtual/timed_output/vibrator/enable" \| su')
   time.sleep(.2)
   device.adbShell('echo "echo 100 > /sys/devices/virtual/timed_output/vibrator/enable" \| su')
   time.sleep(.2)
   device.adbShell('echo "echo 100 > /sys/devices/virtual/timed_output/vibrator/enable" \| su')
   time.sleep(.2)
   device.adbShell('echo "echo 100 > /sys/devices/virtual/timed_output/vibrator/enable" \| su')

def notifyWork():
   myPopen("ssh me@$(curl -L work.joinge.net) \"mplayer /home/me/macro/audio/ringtones/CanisMajor.ogg\" >/dev/null 2>&1")
   
###########
# YOUWAVE #
###########

def newAndroidId():
   printAction("Creating new Android ID...", newline=True)
   if device.isAndroidVM():
      return ''.join(hex[i] for i in np.random.uniform(0,16-1e-9, size=int(np.random.uniform(8, 11))).astype(int))
   elif device.isYouwave():
      return ''.join(np.random.uniform(0,10-1e-9, size=int(np.random.uniform(15, 18))).astype(int).astype('str'))
   
   else:
      myPrint("Android ID creation for this device type is not supported!!!", msg_type='error')
      return None
def setAndroidId(user=None, newid='0' * 15):
   
   printAction("Setting Android ID...")
   
   if device.isAndroidVM():
      printAction("Android VM detected. Rebuilding APK with a new Android ID", newline=True)
      rebuildAPK(newid)
      return
   
   out = device.adbShell("\"cat /data/youwave_id;\
                         cat /sdcard/Id\"")
#    myPrint(out)
   old_ids = out.split('\n')
   if not old_ids[0] == old_ids[1]:
      myPrint("WARNING: IDs in /data (%s) and /sdcard (%s) do not match!!!" % (old_ids[0], old_ids[1]))
      
   old_id = re.search(r'[0-9]*', old_ids[0]).group(0) #15-18
   
   if not user == None:

      try:
         if old_id == newid:
            myPrint('WARNING: saveAndroidId() - Ids are already the same.')
         else:
            if newid == '0' * 15:
               newid = account.getAndroidId(user)
               
            myPrint("Old ID: %s, New ID: %s"%(old_id,newid))
            device.adbShell('echo "echo %s > /data/youwave_id" %s| su' % (newid, ESC))
            device.adbShell('echo "echo %s > /sdcard/Id" %s| su' % (newid, ESC))
            
            account.edit(user, android_id=newid)

      except Exception, e:
         printLog(e, msg_type='error')
         myPrint("ERROR: User %s does not seem to exist!" % user)

   else:
      myPrint("Old ID: %s, New ID: %s"%(old_id,newid))
      device.adbShell('echo "echo %s > /data/youwave_id" %s| su' % (newid, ESC))
      device.adbShell('echo "echo %s > /sdcard/Id" %s| su' % (newid, ESC))


def getAndroidId(user=None):
   
   out = device.adbShell('"cat /data/youwave_id;\
                        cat /sdcard/Id"')
   myPrint(out)
   id = out.split('\n')
   if id[0] == id[1]:
      id_clean = re.search(r'[0-9]*', id[0]).group(0) #15-18
      
      if not user == None:
         
         account.edit(user, android_id=id_clean)
      else:
         myPrint(id_clean)
   else:
      myPrint("WARNING: IDs in /data and /sdcard do not match!!!")
#   out.communicate()



def exitMarvel():
   check_if_vnc_error()
   
   device.adbShell('am force-stop com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android')


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
#   macro_output = Popen("cnee --stop-key 0 --record --mouse --keyboard -o rec/%s.xns -e rec/%s.log -v"%(cmd,cmd), stdout=PIPE, adbShell=True).stdout.read()
#   #if macro_output == None:
#      #raise Exception("Unable to record macro: %s"%cmd)
#
#def replay_macro(cmd, replay_offset=(0,0)):
#   #macro_output = Popen("cnee --replay -f rec/%s.xns -v -e rec/%s.log --synchronised-replay"%(cmd,cmd), stdout=PIPE, adbShell=True).stdout.read()
#   macro_output = Popen("cnee --replay -f rec/%s.xns -v -e rec/%s.log -ns -ro %d,%d --stop-key 0 2>error.log"\
#                        %(cmd,cmd,replay_offset[0],replay_offset[1]), stdout=PIPE, adbShell=True).stdout.read()
#                        

#######
# ADB #
#######

def connect_adb_wifi():
   
   if Popen("adb devices | grep %s" % ip, stdout=PIPE, adbShell=True).returncode == None:
      macro_output = Popen("adb connect %s" % ip, stdout=PIPE, adbShell=True).stdout.read()
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
   macro_output = device.adbShell('pm clear com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android')
   time.sleep(1)

   #if macro_output == None:
   #   raise Exception("Unable to clear Marvel cache")

def launch_marvel():
   macro_output = device.adbShell('am start -n com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android/.SplashActivity')
#   SplashActivity
#   macro_output = device.adbShell('am start -n com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android/.WebGameFrameworkActivity')
   #if macro_output == None:
   #   raise Exception("Unable to start Marvel")

#def adb_shell(strings):
#
#   for string in strings:
      

def adb_input(text):
   macro_output = device.adbShell('input text %s' %(text))

def adb_event_batch(events):
   
   sendevent_string = ''
   for i, event in enumerate(events):
      if i != 0:
         sendevent_string += '; '
         
      sendevent_string += "sendevent /dev/input/event%d %d %d %d" % event
        
   device.adbShell('"%s"' % (sendevent_string))
      
#   print( "adb adbShell %s"%sendevent_string )
      

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
   
   macro_output = device.adbShell('sendevent /dev/input/event%d %d %d %d' % (event_no, a, b, c))
#   time.sleep(0.5)  
   #adbSend("/dev/input/event2",3,48,10);
   
def leftClick(loc):
    
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
      
      device.adbShell('input tap %d %d'%(loc[0],loc[1]))
      
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
#       time.sleep(0.2)

def backspace():
   

   if device.isYouwave() or device.isAndroidVM():
      event_no = device.getInfo('event_keyboard')
      if not event_no:
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
      myPrint("ERROR: backspace() is not implemented for regular phones")     
     
def right_arrow():

   if device.isYouwave() or device.isAndroidVM():
      event_no = device.getInfo('event_keyboard')
      if not event_no:
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
      myPrint("ERROR: right_arrow() is not implemented for regular phones")   
       
   
def enterText(text):
   adb_input(text)
  

def adb_login(login_screen_coords, user, password=None):
   
   c = np.array(login_screen_coords)
   
   if device.getInfo('screen_density') == 240:
      leftClick((205, 254) + c) # Login Mobage
      leftClick((106, 255) + c) # Login button
      leftClick((76, 108) + c) # Mobage name field
   else:
      leftClick((140, 160) + c) # Login Mobage
      leftClick((74, 160) + c) # Login button
      leftClick((144, 71) + c) # Mobage name field
   
   enterText(user)      
   
   if YOUWAVE:
      backspace()
      
   if device.getInfo('screen_density') == 240:
      leftClick((76, 174) + c) # Mobage password field
   else:
      leftClick((142, 114) + c) # Mobage password field
   if YOUWAVE: # youwave screws this up. Need to insert text, then erase it once
      enterText('a')
      
      for i in range(len(user)):
         right_arrow()
#         time.sleep(0.1)
         
      for i in range(len(user) + 2):
         backspace()
#         time.sleep(0.1)
   
   if password:
      enterText(password)
   else:
      enterText(account.getPassword(user))
      
   if YOUWAVE:
      backspace()
      
   if device.getInfo('screen_density') == 240:
      leftClick((313, 237) + c) # Login button
   else:
      leftClick((207, 157) + c) # Login button
#   
def homeKey():
   
   if device.isYouwave():
      adb_event(1, 0x0001, 0x0066, 0x00000001)
      adb_event(1, 0x0000, 0x0000, 0x00000000)
      adb_event(1, 0x0001, 0x0066, 0x00000000)
      adb_event(1, 0x0000, 0x0000, 0x00000000)
   else:
      device.adbShell('input keyevent 4')

def powerKey():
   
   adb_event(1, 0x0001, 0x0074, 0x00000001)
   adb_event(1, 0x0000, 0x0000, 0x00000000)
   adb_event(1, 0x0001, 0x0074, 0x00000000)
   adb_event(1, 0x0000, 0x0000, 0x00000000)
   
   
def backKey():
   
   device.adbShell('input keyevent 4')
   
   
   
def swipe(start, stop):

   if not YOUWAVE:
      device.adbShell('input swipe %d %d %d %d' % (start[0], start[1], stop[0], stop[1]))
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
      device.adbShell('input trackball roll %d %d' % (dx, dy))
   else:
#      xint = 200.0
      yint = 200.0
            
      numy = dy / yint
      for i in range(int(numy) + 1):
         if dy > 0:
            linear_swipe((5, 400), (5, 400 - yint), steps=5)
         else:
            linear_swipe((5, 200), (5, 200 + yint), steps=5)
         
   

   

def locateTemplate(template, threshold=0.96, offset=(0,0), retries=1, interval=0, print_coeff=False, ybounds=None, xbounds=None, reuse_last_screenshot=False,
                   recurse=None, click=False, scroll_size=[], swipe_size=[], swipe_ref=['', (0, 0)]):

   DEBUG=False
   import pylab as pl
   
   for i in range(retries):
      if not reuse_last_screenshot:
         device.takeScreenshot()
      
      time.sleep(.1)
      try:
         if device.getInfo('screen_density') == 240:
            img_path = SCREEN_PATH
         else:
            img_path = SCREEN_PATH + '/dpi160'
            
         image_screen = readImage(TEMP_PATH+"/screenshot_%s.png" %device.active_device, ybounds, xbounds)
#         image_screen   = readImage("test_img_raw.png", ybounds, xbounds)
      except:
         myPrint("ERROR: Unable to load screenshot_%s.png. This is bad, and weird!!!" % device.active_device)
         return False
      
      result = np.array(0)
      match_found = False
      template = re.sub(r'-[0-9]*\.', '.', template)
      for j in range(5):
                  
         name, ext = os.path.splitext(template)
         if ext == '':
            ext = '.png'
         
         if YOUWAVE:
            template_youwave = name + "_youwave" + ext
            if os.path.exists(img_path+'/'+template_youwave):
               template = template_youwave
      
         if os.path.exists(img_path+'/'+name+ext):
            image_template = myRun(cv2.imread, img_path+'/'+name+ext)

            if DEBUG:
               pl.imshow(image_template)
               pl.show()
               
            if offset == 'center':
               image_size = np.array([image_template.shape(0),image_template.shape(1)])
               offset = tuple(int(image_size/2.0))
               
            try:
               result = myRun(cv2.matchTemplate, image_screen, image_template, cv2.TM_CCOEFF_NORMED)
            except Exception, e:
               print(e)
               myPrint("Unable to match screenshot with template %s"%template)
               
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
         object_coords = tuple(template_coords + np.array(offset))
         if click:
            leftClick(object_coords)
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
         if recurse:
            return None
         
         image_error = locateTemplate("android_error.png", recurse=True, threshold=0.9, offset=(65,31), reuse_last_screenshot=True)
         
         if image_error:
            myPrint(' ')
            printAction("Android error detected and will (hopefully) be dealt with.", newline=True)
            leftClick(image_error)
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
      

def clickTemplate():
   
   if locateTemplate('tutorial_promotion_codes.png', offset='center', click=True):
      printResult(True)
      printAction("Time for referral service BABY!!!")
   else:
      print("ERROR: Unable to locate promotion code button")
      return 1     

      
   
def check_if_vnc_error():
#   printAction( "Verifying VNC sanity..." )
#   ok_button = locateTemplate('vnc_error.png', correlation_threshold=0.992, offset=(318,124))
#   printResult(not ok_button)
#   if ok_button:
#      replay_macro("leftClick",offset=ok_button)
   pass
      
def abort_if_vnc_died():
#   titlebar_coords = locateTemplate('titlebar.png', correlation_threshold=0.6)
#   titlebar_black_coords = locateTemplate('titlebar_black.png', correlation_threshold=0.6)
#   if titlebar_coords == None and titlebar_black_coords == None:
#      raise Exception("VNC appears to have died. Aborting.")
   pass

def preOCR(image_name, color_mask=(1, 1, 1), threshold=180, invert=True, xbounds=None, ybounds_old=None):
   
   import scipy.interpolate as interpolate
   import pylab as pl
   
   DEBUG = False

   image = readImage(image_name, xbounds, ybounds_old)
#   image = readImage(image_name)
   
   # Adjust color information
   image[:, :, 0] = image[:, :, 0] * color_mask[0]
   image[:, :, 1] = image[:, :, 1] * color_mask[1]
   image[:, :, 2] = image[:, :, 2] * color_mask[2]
   
   if DEBUG:
      pl.imshow(image)
      pl.show()
   
   # Convert to grey scale
   image = myRun(cv2.cvtColor, image, cv2.COLOR_BGR2GRAY)
   
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
   
   myRun(cv2.imwrite, image_name.strip('.png') + '_processed.png', image)
   
   return image
   

def runOCR(image, mode='', lang='eng'):
   
   if mode == 'line':
      psm = '-psm 7'
   elif mode == '':
      psm = ''
   else:
      myPrint("ERROR: runOCR() - Mode %s is not supported")
      return ''
   
   if lang == 'event_enemy':
      language = 'non'
   else:
      language = 'eng'
   
   myRun(cv2.imwrite, 'tmp.png', image)
   myPopen("echo '' > text.txt")
   myPopen("tesseract tmp.png text %s -l %s >/dev/null 2>&1" % (psm, language))
   
   if os.path.getsize('text.txt') == 1:
      myPrint("ERROR: runOCR() returned no output")
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
   
   leftClick(mypage_button)
   time.sleep(1)
   return True

def getMyPageStatus():
   
   info = {'roster':[]}
   
   myPrint("Get MyPage info...")
   
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
         leftClick((200, 200)) # Possibly daily reward screen
         time.sleep(5)
#         printNotify('Unable to read MyPage. Daily reward?', 60)
                  
   if not entered_mypage:
      printAction("Adjust scrolling, this isn't working.", newline=True)
      return False

   printAction("Running OCR to figure out cards in roster...")
   device.takeScreenshot()
   cards_in_roster_image = preOCR("screenshot_%s.png" % device.active_device, color_mask=(0, 1, 0), xbounds=(92, 185), ybounds_old=(195, 241))
   cards_in_roster_string = runOCR(cards_in_roster_image, mode='line')

   cards_in_roster_numbers = re.findall(r'\d+', cards_in_roster_string)
   cards_in_roster = tuple(map(int, cards_in_roster_numbers))
   
   try:
      myPrint("Cards: %d/%d" % cards_in_roster)
      info['roster'] = cards_in_roster
      if cards_in_roster[1] - cards_in_roster[0] < 15:
         myPrint("WARNING: Roster is soon full!!!")

   except:
      printAction("Unable to determine roster size.", newline=True)
      info['roster'] = [30, 70]
      myRun(cv2.imwrite, 'tmp_last_error.png', cards_in_roster_image)
      
   printAction("Running OCR to figure out amount of silver...")
   silver_image = preOCR("screenshot_%s.png" % device.active_device, color_mask=(1, 1, 0), xbounds=(332, 446), ybounds_old=(272, 312))
   silver_string = runOCR(silver_image, mode='line', lang='event_enemy')
#   silver_numbers = re.search(r'[0-9,]+', silver_string).group(0)
#   silver_numbers = re.sub(r',', '', silver_numbers)
   
   try:
      silver_numbers = re.search(r'.+[,\.][0-9]{1,3}', silver_string).group(0)
      silver_numbers = re.sub(r'\s', '', silver_numbers)
      silver_numbers = re.sub(r',', '', silver_numbers)
      silver_numbers = re.sub(r'\.', '', silver_numbers)


      silver = int(silver_numbers)
      myPrint("Silver: %d" % silver)
      info['silver'] = silver
   
   except:
      printAction("Unable to determine silver amount.", newline=True)
      myRun(cv2.imwrite, 'tmp_last_error.png', silver_image)
   
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
   
#   leftClick(event_fantastic4)
   return True

   
def eventPlayMission(repeat=1):

   myPrint("Playing event mission...")
   
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
            backKey()
            time.sleep(1)
         
         elif event_mission_button:
            printAction("Searching for event mission button...")
            leftClick(event_mission_button)
            printResult(event_mission_button)
            time.sleep(3)
            scroll(0, 1000)
            time.sleep(1)
            
            repeat = repeat + 1
            
         elif go_to_boss:
            printAction("Raid boss detected. Playing the boss...", newline=True)
            
#            face_the_enemy = locateTemplate("face_the_enemy_button.png",
#                                             offset=(130,16), retries=8, click=True, ybounds_old=(0,600), swipe_size=[(20,600),(20,295)])
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
               leftClick(event_mission_button)
               time.sleep(3)
               scroll(0, 1000)
               time.sleep(1)
            else:
               myPrint("Could not find event mission button!")
                  
            repeat = repeat + 1
                             
         
      else:
         
         leftClick(proceed)
      
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
               myPrint('')
               printAction("No energy left! Exiting.", newline=True)
               backKey()
               time.sleep(1)
               return True
               
            if mission_started:
               myPrint('')
               printAction("Mission started. Returning.", newline=True)
               backKey()
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
   device.takeScreenshot()
   while keep_assessing and watchdog > 0:
      keep_assessing = False
      is_enraged = False
      for j in range(10):
         ref = swipeReference("event_enemy_info_frame.png", threshold=0.85, destination=(0, 80), ybounds_old=(150, 500), reuse_last_screenshot=True)
         if not ref:
            return info
         time.sleep(1)
         event_enemy_corner = locateTemplate("event_enemy_info.png", threshold=.80, xbounds=(0, 400), reuse_last_screenshot=False)
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
         increased_raid_rating = locateTemplate("event_3_times_raid_rating.png", threshold=.85, retries=3, xbounds=(0, 450))
         printResult(increased_raid_rating)
         if increased_raid_rating:
            is_enraged = True
         else:
            keep_assessing = True
            watchdog = watchdog - 1
            
      
      printAction("Running OCR to figure out badass name and level...")
   #   printAction("Preprocessing image")

      badguy_image = preOCR("screenshot_%s.png" % device.active_device, xbounds=(110, 370), ybounds_old=(84, 114)) #(99,126)
      badguy_string = runOCR(badguy_image, mode='line')
   
      badguy_name = re.sub(r' Lv.+', '', badguy_string)
      badguy_level = re.sub(r'.+Lv\.', '', badguy_string)
   #   badguy_level= tuple(map(int, badguy_string))
      
      myPrint("%s at level %s" % (badguy_name, badguy_level))
            
      printAction("Running OCR to figure out enemy info...")
      e = event_enemy_corner
      enemy_image = preOCR("screenshot_%s.png" % device.active_device, color_mask=(0, 1, 0), xbounds=(e[0], 470), ybounds_old=(e[1], e[1] + 144)) #old x: e[0]+250
      enemy_info = runOCR(enemy_image, mode='', lang='event_enemy')
   
      enemy_health = re.findall(r'\d+', enemy_info)
      try:
         enemy_health = tuple(map(int, enemy_health))
         myPrint("Health: %d / %d" %(enemy_health[0],enemy_health[1]))
      except:
         myPrint('WARNING: Unable to convert enemy health to int.')
         enemy_health = (1000,1000)
      
      myPrint(enemy_health)
      myPrint("Health: %d / %d" %(enemy_health[0],enemy_health[1]))
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
      device.takeScreenshot()
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
            offset=(154, 89), retries=5, xbounds=(0, 400), swipe_size=[(240, 600), (240, 295)])
         if not event_enemies_in_area:
            return False
#         event_face_enemy = locateTemplate("event_mission_button.png",
#            offset=(240,-54), threshold=0.92, retries=2, reuse_last_screenshot=False, click=True)
#         if not event_face_enemy:
#            return False
         device.takeScreenshot()
         
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
#      leftClick(event_enemy_corner+np.array((66,164)))
#      leftClick(event_enemy_corner+np.array((66,164)))
#      time.sleep(1)
#      swipe((20, 400), (20, 200))
      time.sleep(3)
#      printAction("Searching for deck select button...")
#      for j in range(5):
#         swipe((10,400),(10,200))
#         select_deck = locateTemplate("select_deck_button.png", threshold=.96, offset=(-144,17), ybounds_old=(0,600), click=True)
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
         leftClick(attack_light)
         time.sleep(2)
         leftClick(attack_light)
      elif info['badguy_health'][0] < 4*base_attack and attack_normal:
         printResult(True)
         printAction("Attacking with the 3 RDS option...", newline=True)
         leftClick(attack_normal)
         time.sleep(2)
         leftClick(attack_normal)
      elif attack_blitz:
         printResult(True)
         printAction("Attacking with the 6 RDS option...", newline=True)
         leftClick(attack_blitz)
         time.sleep(2)
         leftClick(attack_blitz)
         rds6 = True
      else:
         printAction("No attack power left. Quitting...", newline=True)
         printResult(False)
         return False
                           
      printAction("Confirming that enemy is taken down...")
      confirmed = False
      taken_out = False
      for i in range(15):
         leftClick((200, 200))
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
#               myPrint( '' )
#               printAction("No attack power left! Exiting.", newline=True)
#               return False
#            
#            end_of_battle = locateTemplate('event_battle_results.png', reuse_last_screenshot=True)
#            if end_of_battle:
#               myPrint( '' )
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
            leftClick(ask_for_support)
            return True and not rds6
            
         elif reward:
            printResult(True)
            success = True
            printAction("Found \"reward\" button. Clicking it...", newline=True)
            leftClick(reward)
            return True and not rds6
         
      if not success:
         printResult(False)
      time.sleep(3)
      return False
#         leftClick(face_the_enemy)
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
##               myPrint( '' )
##               printAction("No attack power left! Exiting.", newline=True)
###                  backKey()
##               return False
#            
#            if end_of_battle:
#               myPrint( '' )
#               printAction("Villain taken down. Returning.", newline=True)
#               return True
#               
##            if mission_started:
##               myPrint( '' )
##               printAction("Mission started. Returning.", newline=True)
##               backKey()
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
   
#   myPrint( badguy_level )
   

      
   
def eventPlay(find_enraged=False):
      
   myPrint("PLAYING EVENT")
   
   N = 6
   Nmax = 16
   keepalive = 0
   i = 0
   while (i < N or keepalive > 0) and i < Nmax:
#    for i in range(N):
      
      gotoEventHome()
  
      printAction("Checking if enemies are present in the area...")
      event_enemies_in_area = locateTemplate("event_enemies_in_area.png",
         offset=(154, 89), retries=5, xbounds=(0, 400), swipe_size=[(240, 600), (240, 295)])
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
         
      leftClick(alignment_button)
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
#                                ybounds_old=(0,600), swipe_ref=['list_select_button_area',()])

   # Cards with stapled lines are skipped (base card)
   top = locateTemplate("list_top_separator.png")
   if not top:
      printResult(False)
      printAction("Could not find the top of list? Weird.", newline=True)
      return False
   
   swipeReference("list_top_separator.png", destination=(20, 90), print_coeff=True, reuse_last_screenshot=True)
   
   for i in range(15):
      card_coords = locateTemplate("card_%s.png" % card_name, threshold=0.95, offset=(214, 86), xbounds=(0, 550))
      select_bar = locateTemplate("list_select_button_area.png", offset=(18, 26), xbounds=(150, 550), reuse_last_screenshot=True)
      if card_coords and select_bar:
         leftClick([select_bar[0], select_bar[1] + 150])
         number_of_cards_selected += 1
         time.sleep(.5)
         break
      
#      swipe((1,600),(479,500))
#      time.sleep(1)
      line_separator = swipeReference("list_line_separator.png", destination=(20, 90), ybounds_old=(150, 600), threshold=0.85, print_coeff=True, reuse_last_screenshot=True)
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
      device.takeScreenshot()
      for card in cards_list:
         card_coords = locateTemplate("card_%s.png" % card, threshold=0.95, offset=(214, 86), xbounds=(300, 800), reuse_last_screenshot=True)
         
         if card_coords:
            leftClick([card_coords[0], card_coords[1] + 300])
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
      
   myPrint("SELLING")
   printAction("Selling cards: ")
   for card in cards_list:
      myPrint("%s " % card, end='')
   myPrint('')
   
   stats = Stats()
      
   printAction("Clicking roster button...")
   menu_button = locateTemplate("menu_button.png", offset=(56, 12))
   
   if not menu_button:
      printAction("Huh? Unable to find menu button!!! That is bad.", newline=True)
      printResult(False)
      return False
   
   leftClick(menu_button)
   time.sleep(int(uniform(.5, 1)))
   
   roster_button = locateTemplate("main_menu.png", offset=(317, 189), retries=3)
   
   if not roster_button:
      printAction("Unable to find main menu!.", newline=True)
      printResult(False)
      return False
   
   printResult(True)
   leftClick(roster_button)
   time.sleep(int(uniform(1, 2)))
   
   printAction("Searching for \"Sell Cards\" button...")
   sell_cards_button = locateTemplate("sell_cards_button.png", offset=(107, 23), retries=3)
   printResult(sell_cards_button)
   
   if not sell_cards_button:
      printAction("Unable to find \"Sell Cards\" button!.", newline=True)
      return False

   leftClick(sell_cards_button)
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

   leftClick(sell_selected_button)
   time.sleep(3)
   
   scroll(0, 1000)
   sell_button = locateTemplate("sell_button.png", offset=(49, 19), retries=4)
   
   if not sell_button:
      printAction("Unable to find \"Sell\" button", newline=True)
      return False
      
   leftClick(sell_button)
   printResult(True)
   time.sleep(3)

#   if number_of_cards_selected < 10:
#      return False
#   else:
      
   return True


   
def boostCard(card_name, cards_list, alignment='all'):
      
   myPrint("BOOSTING")
   printAction("Boosting card: %s" % card_name, newline=True)
      
   printAction("Clicking \"boost\" button...")
   
   scroll(0, 1000)
   time.sleep(2)
   boost_from_fuse = locateTemplate("boost_from_fuse_button.png", offset=(193, 19), retries=4)
   printResult(boost_from_fuse)
   
   if not boost_from_fuse:
      printAction("Huh? Unable to find boost button!!! That is bad.", newline=True)
      return False
   
   leftClick(boost_from_fuse)
   time.sleep(4)
   
   swipe((240, 650), (240, 100))
   time.sleep(1)
     
   listSortAlignment(alignment)
   
   printAction("Checking that multiple cards are selected...")
   multiple_cards_link = locateTemplate("list_multiple_cards_link.png", offset=(54, 33))
   printResult(multiple_cards_link)
   
   if multiple_cards_link:
      leftClick(multiple_cards_link)
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
      device.takeScreenshot()
      for card in cards_list:
         card_coords = locateTemplate("card_%s.png" % card, threshold=0.95, offset=(214, 86), xbounds=(300, 800), reuse_last_screenshot=True)
         
         if card_coords:
            leftClick([card_coords[0], card_coords[1] + 300])
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

   leftClick(boost_now)
   time.sleep(3)
   
   printAction("Clicking \"Boost\" button (second time)...")
   scroll(0, 1000)
   time.sleep(2)
   boost_now = locateTemplate("boost_green_button.png", offset=(58, 17), retries=2)
   printResult(boost_now)
   
   if not boost_now:
      printAction("Unable to find \"Boost\" button", newline=True)
      return True
   
   leftClick(boost_now)
   
   printAction("Waiting for boost finished screen...")
   time.sleep(5)
   boost_finished = locateTemplate("boost_finished.png", offset=(58, 17), retries=15)
   printResult(boost_finished)
   
   if not boost_finished:
      printAction("Unable to find \"Boost\" button", newline=True)
      return True
   
   time.sleep(10)
   leftClick((200, 200))
   time.sleep(3)
   leftClick((200, 200))
   time.sleep(4)
      
   return True

def fuseCard(card_type, alignment='all'):
      
   myPrint("FUSION")
   
   stats = Stats()
   
   printAction("Clicking fusion button...")
   fusion_button_coords = locateTemplate("fusion_button.png", offset=(60, 26), retries=2)
   fusion_button2_coords = locateTemplate("fusion_button2.png", offset=(60, 26))
   printResult(fusion_button_coords or fusion_button2_coords)
   
   if not fusion_button_coords and not fusion_button2_coords:
      printAction("Huh? Unable to find fusion button!!! That is bad.", newline=True)
      return
   
   if fusion_button_coords:
      leftClick(fusion_button_coords)
   else:
      leftClick(fusion_button2_coords)
      
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
         leftClick(change_base_card_coords)
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
   leftClick(fuse_this_card_button_coords)
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
#         leftClick(ironman_fused_screen1)
#         break
   
   printResult(rarity_upgraded) 
   if not rarity_upgraded:
      printAction("First fusion screen did not appear. Buggy game?", newline=True)
      return False
   
   time.sleep(1)
   stats.add(card_type, 2)
   leftClick(rarity_upgraded)
   time.sleep(1)
   
   printAction("Waiting for fusion finished screen...")
   for i in range(10):
      time.sleep(int(uniform(1, 2)))
      leftClick(rarity_upgraded)
      fusion_finished = locateTemplate("fusion_finished.png", offset=(240, 110), retries=3)
            
      if fusion_finished:
         printResult(fusion_finished) 
         printAction("Fusion successful!", newline=True)
         return True
   
   printResult(fusion_finished) 
   return False
      
      
def tradeCards(receiver='joinge', cards_list=['rare_ironman'], alignment='all'):
      
   myPrint("TRADING")
   printAction("Trading the following cards to %s: " % receiver)
   for card in cards_list:
      myPrint("%s " % card, end='')
   myPrint('')
   
#   stats = Stats()
      
   printAction("Searching for recevier...")
   menu_button = locateTemplate("menu_button.png", offset=(56, 12))
   
   if not menu_button:
      printAction("Huh? Unable to find menu button!!! That is bad.", newline=True)
      printResult(False)
      return False
   
   leftClick(menu_button)
   time.sleep(1)
   
   player_search_button = locateTemplate("main_menu.png", offset=(107, 340), retries=3)
   
   if not player_search_button:
      printAction("Unable to find main menu!.", newline=True)
      printResult(False)
      return False
   
   printResult(True)
   leftClick(player_search_button)
   time.sleep(2)
   
   printAction("Entering receiver name...")
   text_field = locateTemplate("text_box.png", offset=(68, 22), retries=3)
   printResult(text_field)
   
   if not text_field:
      printAction("Unable to find text field to enter receiver!.", newline=True)
      return False

   leftClick(text_field)
   time.sleep(1)
   enterText(receiver)
   time.sleep(1)
   search = locateTemplate("player_search_button.png", offset=(57, 17), print_coeff=False, reuse_last_screenshot=True)
   time.sleep(1)
   leftClick(search) # Mobage password field
   time.sleep(3)
   printAction("Clicking receiver name...")
   leftClick((345, 672))
   time.sleep(3)
   
   trade = locateTemplate("player_info_trade_button.png", offset=(55, 14), retries=3)
   printResult(trade)
   
   if not trade:
      printAction("Unable to find trade button on player info page!.", newline=True)
      return False

   leftClick(trade)
   time.sleep(2)
   
   one_or_more_card_found = False
   for card in cards_list:
      printAction("Adding another card for trade...")
      trade_card = locateTemplate("trade_card_button.png", offset=(59, 17), retries=3, xbounds=((450, 800)))
      trade_card = tuple(np.array(trade_card) + (0, 450))
         
      if not trade_card:
         printAction("Unable to find card trade button!.", newline=True)
         return False
      
      time.sleep(1)
      leftClick(trade_card)
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
   trade_silver = locateTemplate("trade_silver_button.png", offset=(59, 17), retries=2, xbounds=((0, 550)))
      
   if not trade_silver:
      printAction("Unable to find card trade button!.", newline=True)
      return False
   
   time.sleep(1)
   leftClick(trade_silver)
   time.sleep(3)
   printResult(trade_silver)
   
   printAction("Entering 1 silver...")
   text_field = locateTemplate("text_box.png", offset=(68, 22), retries=3)
   printResult(text_field)
   
   if not text_field:
      printAction("Unable to silver text field!.", newline=True)
      return False
   
   leftClick(text_field)
   time.sleep(1)
   enterText("1")
   time.sleep(1)
   leftClick((453, 757))
#   add = locateTemplate("add_button.png", offset=(46,17), reuse_last_screenshot=True)
#   time.sleep(1)
#   leftClick(add) # Mobage password field
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
   
   leftClick(offer_trade)
   time.sleep(3)

   return True
      
def play_mission(mission_number=(3, 2), repeat=50, statistics=True):
      
   stats = Stats()
   
   if statistics:
      stats.silverStart("mission_%d-%d" % mission_number)
            
   myPrint("Playing mission %d-%d..." % mission_number)

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
            backKey()
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
            leftClick((181, 774)) # mission button
            time.sleep(3)
            scroll(0, 1000)
   #         swipe((250,390),(250,80))
            printAction("Searching for \"operations\" button...")
            operations_button = locateTemplate("operations_button.png", offset=(50, 15), retries=6, click=True)
            printResult(operations_button)
            
            if not operations_button:
               return True
            #time.sleep(2)
            #leftClick((240,602)) #operations button
            
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
               myPrint("Unable to locate mission buttion. This shouldn't happen. Dammit!")
               
               if statistics:
                  stats.silverEnd("mission_%d-%d" % mission_number)
               
               return True # Retry
            
            leftClick(mission_button_coords)
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
               #myPrint( "30 mission iterations. Assuming error and exiting." )
               #return False
         
      else:
         initial_run = False
         leftClick(mission_button_coords)
         printAction("Avaiting mission screen...")
         mission_success = False
         for i in range(10):
            time.sleep(int(uniform(1, 2)))
            
            out_of_energy = locateTemplate('out_of_energy.png', threshold=0.985, print_coeff=False)
            #printResult(out_of_energy)
            
            mission_started = locateTemplate('mission_bar.png', threshold=0.985)
            #printResult(mission_started)
               
            if out_of_energy:
               myPrint('')
               printAction("No energy left! Exiting.", newline=True)
               backKey()
               
               if statistics:
                  stats.silverEnd("mission_%d-%d" % mission_number)
               
               return True
               
            if mission_started:
               myPrint('')
               printAction("Mission started. Returning.", newline=True)
               time.sleep(1)
               backKey()
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
          
          
def playNewestMission(repeat=50, use_ep=None):

   myPrint("MISSION: Newest...")
   ep_counter = 0
   
   mission_button = locateTemplate('mission_button.png', offset=(49,13), print_coeff=False)

   for i in range(repeat + 1):
      printAction("Searching for newest mission button...")
      mission_newest_button  = locateTemplate("mission_newest_button.png", threshold=0.95, retries=2, offset=(193, 14))
      printResult(mission_newest_button)
                  
      if not mission_newest_button:
         
         # Double check that the return from mission actually was registered.
         mission_started = locateTemplate('mission_bar.png', print_coeff=False, reuse_last_screenshot=True)
         mission_out_of_energy = locateTemplate("mission_out_of_energy.png", offset=(130, 16), print_coeff=False, reuse_last_screenshot=True)
         
         if mission_started:
            printAction("Seems we failed to return from mission. Retrying.", newline=True)
            backKey()
            time.sleep(1)
         
#            confirm = locateTemplate("event_mission_boss_confirm_button.png", threshold=0.9,
#                                             offset=(85, 24), retries=20, interval=1, click=True)
#            if not confirm:
#               printAction("Unable to find \"FIGHT\" button...", newline=True)
#               return False
            
            repeat = repeat + 1
            
         elif mission_out_of_energy and use_ep:
            
            printAction("Out of energy. Using an extra energy pack...")
            mission_use_energy_pack = locateTemplate("mission_use_energy_pack.png", offset=(43,134), retries=3, click=True, reuse_last_screenshot=True)
            printResult(mission_use_energy_pack)
            
            if not mission_use_energy_pack:
               return ep_counter
            
            printAction("Out of energy. Using an extra energy pack...")
            button_green_ok = locateTemplate("button_green_ok.png", offset=(28,9), retries=3, click=True)
            printResult(button_green_ok)
            
            if not button_green_ok:
               return ep_counter
            
            if mission_button:
               leftClick(mission_button)
            else:
               locateTemplate('mission_button.png', offset=(49, 13), print_coeff=False, click=True, reuse_last_screenshot=True)

         else:

            mission_button = locateTemplate('mission_button.png', offset=(49, 13), print_coeff=False, reuse_last_screenshot=True)
            
            if mission_button:
               leftClick(mission_button) # mission button
            else:
               if use_ep:
                  return ep_counter
               else:
                  return False
#            time.sleep(3)
         
            printAction("Searching for newest mission button...")
            mission_newest_button = locateTemplate("mission_newest_button.png", threshold=0.95,
                                                   offset=(193, 14), retries=5, swipe_size=[(240, 500), (240, 295)])
            printResult(mission_newest_button)
            if not mission_newest_button:
               if use_ep:
                  return ep_counter
               else:
                  return False
               
#            time.sleep(1)
            
            repeat = repeat + 1
                    
      else:
         leftClick(mission_newest_button)
         printAction("Avaiting newest mission screen...")
         mission_success = False
         for i in range(30):
#            time.sleep(int(uniform(1, 2)))
            
            mission_started = locateTemplate('mission_bar.png', threshold=0.985, print_coeff=False)
            out_of_energy = locateTemplate('mission_out_of_energy.png', threshold=0.985, print_coeff=False, reuse_last_screenshot=True)
            mission_boss_encounter = locateTemplate("mission_face_the_super_villain_button.png", offset=(130, 16), print_coeff=False, reuse_last_screenshot=True)
                           
            if out_of_energy:
               myPrint('')
               if use_ep:
                  
                  if ep_counter > use_ep:
                     return ep_counter
         
                  printAction("Out of energy. Using energy pack %d of %d..."%(ep_counter,use_ep))
                  mission_use_energy_pack = locateTemplate("mission_use_energy_pack.png", offset=(43,134), retries=3, click=True)
                   
                  if not mission_use_energy_pack:
                     printResult(False)
                     return ep_counter

                  
                  button_green_ok = locateTemplate("button_green_ok.png", offset=(28,9), retries=3, click=True)
                  
                  if not button_green_ok:
                     printResult(False)
                     return ep_counter

                  printResult(True)
                  ep_counter = ep_counter + 1
                  mission_success = True
                  locateTemplate('mission_button.png', offset=(49, 13), print_coeff=False, click=True, reuse_last_screenshot=True)
                  
                  repeat = repeat + 1
                  break
                  
               else:
                  printAction("No energy left! Exiting.", newline=True)
                  backKey()
               
#               if statistics:
#                  stats.silverEnd("mission_%d-%d"%mission_number)
               
#               return True

            elif mission_boss_encounter:
               
               printAction("Raid boss detected. Playing the boss...", newline=True)
               
               leftClick(mission_boss_encounter)
               
               printAction("Attempting to find and click second \"face the enemy\" button...")
               face_enemy = locateTemplate("mission_face_the_super_villain_button.png", offset=(130, 16), retries=4, click=True)
               printResult(face_enemy)
               if not face_enemy:
                  printAction("Unable to find \"face the enemy\" button...", newline=True)
                  return False
               
               leftClick(face_enemy)
               
               success = False
               for i in range(20):
                  if locateTemplate('mission_button.png', offset=(49, 13), click=True):
                     success = True
                     break
                  leftClick((240,115))
               if not success:
                  print("ERROR: Unable to battle raid boss")
                  return 1  
               
               start_mission = locateTemplate("mission_start.png", threshold=0.9,
                                                offset=(61, 9), retries=5, click=True)
               if not start_mission:
                  printAction("Unable to find \"start mission\" button...", newline=True)
                  return False

               time.sleep(5)
               backKey()              
               repeat = repeat + 1
               break
               
            if mission_started:
               myPrint('')
               printAction("Mission started. Returning.", newline=True)
#               time.sleep(1)
               backKey()
#               time.sleep(int(uniform(1, 2)))
               mission_success = True
               
#               if statistics:
#                  stats.add("mission_%d-%d"%mission_number, 1)
                  
               break
         
         if not mission_success:
            printAction("Timeout when waiting for mission screen", newline=True)
            if use_ep:
               return ep_counter
            else:
               return False
#            if statistics:
#               stats.silverEnd("mission_%d-%d"%mission_number)
#            return False


def skillUpAccount(repeat=99999, use_ep=3000):
   
   ep_counter = 0
   
   while ep_counter < use_ep:
      ensureStealth()
      
      ep_count = playNewestMission(repeat=repeat, use_ep=use_ep-ep_counter)
      
      if not ep_count:
         ep_count = 0
         
      ep_counter = ep_counter + ep_count
      
      if ep_counter < use_ep:
         printAction("A problem occured. Restarting WoH")
         exitMarvel()
         time.sleep(2)
         launch_marvel()
         time.sleep(10)
         started = locateTemplate('mission_button.png', offset=(49,13), print_coeff=False, retries=20)
         printResult(started)


def useReferrals():

   pass

#   printAction("Attempting to find and click second \"face the enemy\" button...")
#   face_enemy = locateTemplate("mission_face_the_super_villain_button.png", offset=(130, 16), retries=4, click=True)
#   printResult(face_enemy)
#   if not face_enemy:
#      printAction("Unable to find \"face the enemy\" button...", newline=True)
#      return False
#   
#   leftClick(face_enemy)
#   
#   success = False
#   for i in range(20):
#      if locateTemplate('mission_button.png', offset=(49, 13), click=True):
#         success = True
#         break
#      leftClick((240,115))
#   if not success:
#      print("ERROR: Unable to battle raid boss")
#      return 1  
#   

def startMarvel(user, attempts=3, password=None, enable_cache=False):
   
   if YOUWAVE:
      myPrint( "Macro is being run in YOUWAVE MODE" )
   
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
            adb_copy_to_sdcard_cmd += "adb %s adbShell \"" % device.adb_active_device
            adb_copy_to_data_cmd += "adb %s adbShell \"" % device.adb_active_device
         adb_copy_to_sdcard_cmd += "echo 'cp /data/data/com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android/%s /sdcard/pull_tmp/%s' | su; " % (f, f)
         adb_copy_to_data_cmd += "echo 'cp /sdcard/push_tmp/%s /data/data/com.mobage.ww.a956.MARVEL_Card_Battle_Heroes_Android/%s' | su; " % (f, f)
         if i % 5 == 4:
            adb_copy_to_sdcard_cmd += "\"; "
            adb_copy_to_data_cmd += "\"; "
      if (i - 1) % 5 != 4:
         adb_copy_to_sdcard_cmd += "\"; "
         adb_copy_to_data_cmd += "\"; "
   
#   adb_copy_to_sdcard_cmd = \
#      "adb %s adbShell \
#      \" rm -r /sdcard/pull_tmp;\
#         mkdir /sdcard/pull_tmp;\
#         mkdir /sdcard/pull_tmp/files;\
#         mkdir /sdcard/pull_tmp/shared_prefs\";\
#         adb %s adbShell \
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
         myPrint(
         device.adb('adbShell rm -r /sdcard/push_tmp;\
                     push ./users/%s /sdcard/push_tmp;'%user))
         
         myPrint(
         myPopen('%s'%(adb_copy_to_data_cmd)))
         
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
               
               myPrint(
               device.adb('adbShell \
                          " rm -r /sdcard/pull_tmp;\
                            mkdir /sdcard/pull_tmp;\
                            mkdir /sdcard/pull_tmp/files;\
                            mkdir /sdcard/pull_tmp/shared_prefs"'))
               myPrint(
               myPopen('%s'%adb_copy_to_sdcard_cmd))
               
               myPrint(
               device.adb('pull /sdcard/pull_tmp ./users/%s' %user))

            time.sleep(1)
            ad  = locateTemplate('home_screen_ad.png', offset=(90, 20), threshold=0.95)
            ad2 = locateTemplate('home_screen_ad2.png', offset=(90, 20), threshold=0.95, reuse_last_screenshot=True)
            if ad or ad2:
               if ad:
                  leftClick(ad) # kills ads
               if ad2:
                  leftClick(ad2) # kills ads
               time.sleep(1)
            
#            leftClick((346,551)) # kills ads
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
   myPrint('')
   myPrint('')
   myPrint("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
   myPrint("    %s" %user)
   myPrint("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
   
   for i in range(attempts):
      myPrint('')
      myPrint("Login attempt %d on account %s..." % (i, user))
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
   
   
#def test_img_raw():
#   info = getMyPageStatus()
#   roster_count, roster_capacity = info['roster']
#   
#   myPrint(roster_count)
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
      myPrint("ERROR: Trouble when reading MyPage status or when reading roster count")
   
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
      myPrint("ERROR: Trouble when reading MyPage status or when reading roster count")
   
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
      myPrint("ERROR: Trouble when reading MyPage status or when reading roster count")
   
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
      myPrint("ERROR: Trouble when reading MyPage status or when reading roster count")
   
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
   
   for i, name in enumerate(user.accounts):
      if user.accounts[i] == name:
         return i
   return -1

def randomUserStart(user_list=None):
   
   global recently_launched
   
   if user_list == None:
      user_list = user.accounts
   
   if recently_launched == []:
      recently_launched = [0] * user.accounts.__len__()
   
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
      for i in user.accounts:
         try:
            if randomUserStart():
               farmMission24FuseAndBoost()
               exitMarvel()
         except:
            pass
         time.sleep(3 * 60)
      
def runAll32():
   while True:
      for i in user.accounts:
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
      for i in user.accounts:
         try:
            if randomUserStart():
               play_mission((4, 3), 2 * 23)
               exitMarvel()
         except:
            pass
         time.sleep(60 * uniform(1, 5))
         
      time.sleep(60 * uniform(35, 55))
   
      
def blockUntilQuit():
   
   myPrint("Waiting until game is killed.")
   time.sleep(3)
   while True:
      if not re.findall('MARVEL', Popen('adb %s adbShell ps' % device.adb_active_device, adbShell=True, stdout=PIPE).stdout.read()):
         break
      time.sleep(3)
   myPrint("Game was killed. Moving on...")
      
def startAndRestartWhenQuit():
   

   for i in user.accounts:
      randomUserStart()
         
      while True:
         if not re.findall('MARVEL', Popen('adb %s adbShell ps' % device.adb_active_device, adbShell=True, stdout=PIPE).stdout.read()):
            break

         time.sleep(2)
                  
def sleepToCharge(preferred=60):
   
   
   output = device.adbShell('cat /sys/class/power_supply/battery/capacity')
   had_to_rest = False
   while int(output) < 50:
      if not had_to_rest:
#         lock_phone()
         myPrint("BATTERY below 20\%. Need to sleep for a bit.")
         had_to_rest = True
         
      output = device.adbShell('cat /sys/class/power_supply/battery/capacity')         
      time.sleep(60)

#   if had_to_rest:
#      unlock_phone()
      
   time.sleep(preferred)
   
def cyclePlayers():

   device.adjustBrightness()
   while True:
      for i in user.accounts:
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
#         leftClick((200, 200))
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
#            leftClick(ask_for_support)
#            break
#            
#         elif reward:
#            printResult(True)
#            success = True
#            printAction("Found \"reward\" button. Clicking it...", newline=True)
#            leftClick(reward)
#            break
#         
#      if not success:
#         printResult(False)
#      time.sleep(3)
   
   while(True):
      gotoEventHome()
#      time.sleep(2)
      ref = locateTemplate('event_asked_for_raid_support.png', threshold=0.95,
                           offset=(130, 16), retries=2, click=True, xbounds=(0, 600), swipe_size=[(20, 600), (20, 100)])
      
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
   
   myPrint("TONY PRESIDENT EVENT")
   
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
         backKey()
         
      elif explore_finished:
         
         printAction("Exploration finished...", newline=True)
         break
         
      elif landed_search:
         
         printAction("Landed on search spot...", newline=True)
         printAction("Hitting radar watch...")
         radar_watch = locateTemplate("stark_president/radar_watch.png",
                                      offset=(78, 27), threshold=0.92, retries=5, xbounds=(0, 600), swipe_size=[(20, 600), (20, 100)], click=True)
         printResult(radar_watch)
         
         if radar_watch:
            
            
            time.sleep(5)
            backKey()
            
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
                  backKey()
                  
      else:
         
         for i in range(15):
            notify()
            time.sleep(2)
         
class CycleTimeout(Exception):
   pass


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
         myPrint("")
         myPrint("*************")
         myPrint("** TIMEOUT **")
         myPrint("*************")
         myPrint("")
         process.terminate()
         
      return process
         
   def exit(self):
      sys.exit()
      

def timeout(function, timeout, *args, **kwargs):
   
   while True:
      myPrint("")
      myPrint("***Starting cycle***")
      myPrint("")
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

   device.adjustBrightness()
   while True:
      for i in user.accounts:
         try:
            if startMarvel(i):
               farmMission24FuseAndBoost()
               exitMarvel()
         except:
            pass
         sleepToCharge(60)
         

def custom6():

   device.adjustBrightness()
   while True:
      for i in user.accounts:
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     farmMission24FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  myPrint("ERROR: Some exception occured when processing %s" % i)
                  myPrint(e)
               sleepToCharge(60)
               
      for i in user.accounts:
            if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
               try:
                  if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  myPrint("ERROR: Some exception occured when processing %s" % i)
                  myPrint(e)
               sleepToCharge(60)
      
      
def custom6b():

   device.adjustBrightness()
   while True:
      for i in user.accounts:
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     farmMission24FuseAndBoost()
                     notify()
                     blockUntilQuit()
                     exitMarvel()
               except Exception, e:
                  myPrint("ERROR: Some exception occured when processing %s" % i)
                  myPrint(e)
               sleepToCharge(60)
               
      for i in user.accounts:
            if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
               try:
                  if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                     farmMission32FuseAndBoost()
                     notify()
                     time.sleep(30)
#                     blockUntilQuit()
                     exitMarvel()
               except Exception, e:
                  myPrint("ERROR: Some exception occured when processing %s" % i)
                  myPrint(e)
               sleepToCharge(60)
      
def custom7(start_end=False):

   device.adjustBrightness()
   while True:
      if not start_end:
         for i in user.accounts:
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     farmMission24FuseAndBoost()
                     
                     exitMarvel()
               except Exception, e:
                  myPrint("ERROR: Some exception occured when processing %s" % i)
                  myPrint(e)
               sleepToCharge(60)
      
      start_end = False
      for i in user.accounts:
         if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
            try:
               if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                  farmMission24FuseAndSell()
                  exitMarvel()
            except Exception, e:
               myPrint("ERROR: Some exception occured when processing %s" % i)
               myPrint(e)
            sleepToCharge(60)

def custom8(start_end=False):

   device.adjustBrightness()
   while True:
      if not start_end:
         for i in user.accounts:
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     farmMission24FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  myPrint("ERROR: Some exception occured when processing %s" % i)
                  myPrint(e)
               sleepToCharge(60)
           
      start_end = False 
      for i in user.accounts:
         if i == 'l33tdump' or i == 'Rolfy86':
            try:
               if randomUserStart(['l33tdump', 'Rolfy86']):
                  farmMission24FuseAndBoost()
                  exitMarvel()
            except Exception, e:
               myPrint("ERROR: Some exception occured when processing %s" % i)
               myPrint(e)
            sleepToCharge(60)
               
      
      for i in user.accounts:
         if i == 'kinemb86' or i == 'MonaBB86':
            try:
               if randomUserStart(['kinemb86', 'MonaBB86']):
                  farmMission24FuseAndBoost()
                  exitMarvel()
            except Exception, e:
               myPrint("ERROR: Some exception occured when processing %s" % i)
               myPrint(e)
               
            sleepToCharge(60)
            
def custom9(start_end=False):

   device.adjustBrightness()
   while True:
      unlock_phone()
#       try:
#             setAndroidId(user)
#             startMarvel(user, password=password)
      playNewestMission()
#             exitMarvel()
      time.sleep(60*80)
#       except Exception, e:
#          myPrint("Failed to process user %s" % user)
#          myPrint(e)

            
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
            myPrint("Failed to process user %s" % user)
            myPrint(e)

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
               myPrint(e)
            playNewestMission()
            exitMarvel()
            time.sleep(60)
         except Exception, e:
            myPrint("Failed to process user %s" % user)
            myPrint(e)


def event1(start_end=False):

   device.adjustBrightness()
   while True:
      if not start_end:
         for i in user.accounts:
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     farmMission32()                
                     exitMarvel()
               except:
                  pass
               sleepToCharge(60)
         
      for i in user.accounts:
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

   device.adjustBrightness()
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

   device.adjustBrightness()
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

   device.adjustBrightness()
   while True:
#      notifyWork()
#      printNotify('Complete event for JoInge.', 60*10)
      try:
         startMarvel('JoInge')
         farmMission24FuseAndBoost()
         exitMarvel()
      except:
         pass
      for i in user.accounts:
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
               
      for i in user.accounts:
            if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
               try:
                  if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                     try:
                        eventPlay(find_enraged=True)
                     except Exception, e:
                        myPrint(e)
#                     playNewestMission()
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  myPrint(e)
               sleepToCharge(30)


def event7(find_enraged=False):

   device.adjustBrightness()
   while True:
      for i in user.accounts:
         if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
            try:
               if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                  try:
                     eventPlay(find_enraged=find_enraged)
                  except Exception, e:
                     myPrint(e)
                  farmMission32FuseAndBoost()
                  exitMarvel()
            except Exception, e:
               myPrint(e)
            sleepToCharge(30)
               
      for i in user.accounts:
            if i == 'l33tdump' or i == 'Rolfy86' or i == 'kinemb86' or i == 'MonaBB86':
               try:
                  if randomUserStart(['l33tdump', 'Rolfy86', 'kinemb86', 'MonaBB86']):
                     try:
                        eventPlay(find_enraged=find_enraged)
                     except Exception, e:
                        myPrint(e)
#                     playNewestMission()
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  myPrint(e)
               sleepToCharge(30)


      

def event8():

   def func():

      device.adjustBrightness()
      while True:
         try:
            if startMarvel('JoInge'):
               try:
                  eventStarkPresident()
                  farmMission32FuseAndBoost()
                  exitMarvel()
               except Exception, e:
                  myPrint(e)
         except Exception, e:
            myPrint(e)
         sleepToCharge(30)
         for i in user.accounts:
            if i == 'JoInge' or i == 'JollyMa' or i == 'JoJanR':
               try:
                  if randomUserStart(['JoInge', 'JollyMa', 'JoJanR']):
                     eventStarkPresident()
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  myPrint("ERROR: Some exception occured when processing %s" % i)
                  myPrint(e)
               sleepToCharge(60)
              
         for i in user.accounts:
            if i == 'l33tdump' or i == 'Rolfy86':
               try:
                  if randomUserStart(['l33tdump', 'Rolfy86']):
                     eventStarkPresident()
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  myPrint("ERROR: Some exception occured when processing %s" % i)
                  myPrint(e)
               sleepToCharge(60)
                  
         
         for i in user.accounts:
            if i == 'kinemb86' or i == 'MonaBB86':
               try:
                  if randomUserStart(['kinemb86', 'MonaBB86']):
                     eventStarkPresident()
                     farmMission32FuseAndBoost()
                     exitMarvel()
               except Exception, e:
                  myPrint("ERROR: Some exception occured when processing %s" % i)
                  myPrint(e)
                  
               sleepToCharge(60)

   timeout(func,90*60)
      
      


def tradeToJollyMa():

   trade_list = ['rare+_ironman'] * 10
   device.adjustBrightness()
          
   for i in user.accounts:
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
   
   root_path = os.getcwd() 
   
   screenshot_tmp_path = '%s/%s'%(root_path,TEMP_PATH)
   screenshot_path = '%s/%s'%(root_path,SCREEN_PATH)
   if device.getInfo('screen_density') == 160:
      screenshot_path = screenshot_path + '/dpi160'
      
   screenshot_tmp = screenshot_tmp_path + '/screenshot_%s.png'%device.active_device
   screenshot_new = screenshot_path     + '/screenshot_%s.png'%device.active_device

   myPopen("cp %s %s" %(screenshot_tmp, screenshot_new))
   myPopen("gimp %s &"%screenshot_new )
   myPopen("sleep 5; rm %s"%screenshot_new )

if __name__ == "__main__":

   i = Info()
   from run import *
   run()
   
   # Abracho bfg376874
   # Andre   cen228772
   # Chris   ddf493943
   # Dented  zpj296305
   # Frankie rnj978078
   # JoInge  bsv991976
   # Mark    jcp405955
   
#   #        Krzy        Sky         Ducky        Mika         Cfd          Bad Milk     Skittle      Vince        Frank        Neil         Ducky        Papa
#   refs = ["jpm140046","tqr638335","gqz495105", "wek110915", "maq107823", "acs385098", "tsk990511", "rpn132038", "afs233616", "rqv405128", "ayk228815", "vrk754007"]
#   for i in range(100):
#      for ref in refs:
#         createMultipleNewFakeAccounts(1, interval=(0,0), referral=ref, never_abort=True, draw_ucp=False)
