#cnee --record --events-to-record -1 --mouse --keyboard -o /tmp/xnee.xns -e /tmp/xnee.log -v

#cnee --record --seconds-to-record 150 --mouse --keyboard -o joinge.xns -e joinge.log -v


from __future__ import print_function
from random import uniform
from subprocess import Popen, PIPE
import numpy as np
import re, time, os, sys


timeout = 90 # minutes
ip      = "10.0.0.15"

PAD = 50

def printResult(res):
   if res:
      print(":)")
   else:
      print(":s")

def printAction(str,res=None,newline=False):
   string = "   %s"%str
   if newline:
      print(string.ljust(PAD,' '))
   else:
      print(string.ljust(PAD,' '),end='')
   
   if res:
      printResult(res)
   


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
   enter_text( "Mdt9oFSV" )
   left_click(( 313, 237 )+c) # Login button
   
   
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

   Popen("adb shell /system/bin/screencap -p /sdcard/screenshot.png > error.log 2>&1", stdout=PIPE, shell=True).stdout.read()
   Popen("adb pull /sdcard/screenshot.png screens/screenshot.png >error.log 2>&1", stdout=PIPE, shell=True).stdout.read()
   
   
def take_screenshot_gtk():
   import gtk.gdk
   
   w = gtk.gdk.get_default_root_window()
   #sz = w.get_size()
   sz = (480,800+23)
   #print "The size of the window is %d x %d" % sz
   pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
   pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
   if (pb != None):
      pb.save("screens/screenshot.png","png")
      #print "Screenshot saved to screenshot.png."
   else:
      print( "Unable to get the screenshot." )
      
      
def locate_template(template, correlation_threshold=0.98, offset=(0,0), retries=1, interval=1, print_coeff=True):
   import cv2
   try:
      image_template = cv2.imread(template)
   except:
      print( template+" does not seem to exist." )
   
   for i in range(retries):
      take_screenshot_adb()
      image_screen   = cv2.imread("screens/screenshot.png")
      
      result = cv2.matchTemplate(image_screen,image_template,cv2.TM_CCOEFF_NORMED)
      
      if print_coeff:
         print( " %.2f"%result.max(), end='' )
         
      if result.max() > correlation_threshold:
         
         template_coords = np.unravel_index(result.argmax(),result.shape)
         template_coords = np.array([template_coords[1],template_coords[0]])
         object_coords = tuple(template_coords + np.array(offset))
         print(" (%d,%d)"%(object_coords[0],object_coords[1]),end=' ')
         return object_coords
      
      else:
                  
         # See if the cause can be an Android error:
         image_error   = cv2.imread("screens/android_error.png")
         err_result = cv2.matchTemplate(image_screen,image_error,cv2.TM_CCOEFF_NORMED)
         print( " %.2f"%err_result.max(), end='' )
         if err_result.max() > 0.9:
            print(' ')
            printAction( "Android error detected and will (hopefully) be dealt with.", newline=True )
            template_coords = np.unravel_index(err_result.argmax(),err_result.shape)
            template_coords = np.array([template_coords[1],template_coords[0]])
            left_click(template_coords + np.array([319,31]))
            retries = retries + 1                    
         
      if retries > 1:
         time.sleep(int(uniform(interval,interval*1.5))) # needed?
      
   return None
      
      #print template_coords + np.array(offset)
   
   #print('')

   
def check_if_vnc_error():
#   printAction( "Verifying VNC sanity..." )
#   ok_button = locate_template('screens/vnc_error.png', correlation_threshold=0.992, offset=(318,124))
#   printResult(not ok_button)
#   if ok_button:
#      replay_macro("left_click",offset=ok_button)
   pass
      
def abort_if_vnc_died():
#   titlebar_coords = locate_template('screens/titlebar.png', correlation_threshold=0.6)
#   titlebar_black_coords = locate_template('screens/titlebar_black.png', correlation_threshold=0.6)
#   if titlebar_coords == None and titlebar_black_coords == None:
#      raise Exception("VNC appears to have died. Aborting.")
   pass
   

def fuse_ironman():
      
   print("FUSION")
   
   printAction("Clicking fusion button...")
   fusion_button_coords = locate_template("screens/fusion_button.png", offset=(60,26))
   printResult(fusion_button_coords)
   
   if not fusion_button_coords:
      printAction( "Huh? Unable to find fusion button!!! That is bad.", newline=True)
      return
   
   left_click(fusion_button_coords)
   time.sleep(int(uniform(.5,1)))
   
   printAction("Checking if a base card is already selected or not...")
   for i in range(3):
      change_base_card_coords = locate_template("screens/fusion_change_base_card_button.png", offset=(144,15))
      base_card_menu          = locate_template("screens/fusion_select_base_card.png", offset=(100,14))
            
      if change_base_card_coords:
         time.sleep(.3)
         left_click(change_base_card_coords)
         break
         
      if base_card_menu:
         break
      
   if change_base_card_coords or base_card_menu:
      printResult(change_base_card_coords or base_card_menu)
   #base_card_menu = locate_template("screens/fusion_select_base_card.png", offset=(100,14))
   time.sleep(1)

   printAction("Searching for a base card...")
   for i in range(10):
      swipe((10,600),(10,380)) # scroll half a card at the time
      time.sleep(.5)
      ironman_base_coords = locate_template("screens/fusion_ironman_base.png", offset=(240,306))
                     
      if ironman_base_coords:
         time.sleep(.5)
         left_click(ironman_base_coords)
         time.sleep(1)
         break
      
   printResult(ironman_base_coords)
   if not ironman_base_coords:
      printAction( "Unable to find an Ironman for fusion.", newline=True)
      return False
         
   printAction("Searching for a fuser card...")
   for i in range(10):
      swipe((10,600),(10,380)) # scroll half a card at the time
      time.sleep(.5)
      ironman_fuser_coords = locate_template("screens/fusion_ironman_fuser.png", offset=(240,315))
            
      if ironman_fuser_coords:
         time.sleep(.5)
         left_click(ironman_fuser_coords)
         break
   
   printResult(ironman_fuser_coords) 
   if not ironman_fuser_coords:
      printAction( "Unable to find the fuser. This is strange and should not happen.", newline=True)
      return False
         
   printAction("Clicking \"fuse this card\" button...")
   fuse_this_card_button_coords = locate_template("screens/fusion_fuse_this_card_button.png", offset=(106,16), retries=5)
   printResult(fuse_this_card_button_coords)
   
   if not fuse_this_card_button_coords:
      return False
   
   time.sleep(1)
   left_click(fuse_this_card_button_coords)
   time.sleep(4) # The fusion thing takes some time.
   
   printAction("Waiting for first fusion screen...")
   ironman_fused_screen1 = locate_template("screens/fusion_ironman_fused1.png", correlation_threshold=0.96, offset=(155,200), retries=10)
   
#   if not ironman_fused_screen1:
#      return False
#   
#   for i in range(10):
#      time.sleep(int(uniform(1,2)))
#      ironman_fused_screen1 = locate_template("screens/fusion_ironman_fused1.png", offset=(155,200), retries=5)
#            
#      if ironman_fused_screen1:
#         left_click(ironman_fused_screen1)
#         break
   
   printResult(ironman_fused_screen1) 
   if not ironman_fused_screen1:
      printAction( "First fusion screen did not appear. Buggy game?", newline=True)
      return False
   
   time.sleep(1)
   left_click(ironman_fused_screen1)
   time.sleep(1)
   
   printAction("Waiting for fusion finished screen...")
   for i in range(10):
      time.sleep(int(uniform(1,2)))
      ironman_finished = locate_template("screens/fusion_ironman_finished.png", offset=(240,110), retries=5)
            
      if ironman_finished:
         printResult(ironman_finished) 
         printAction( "Fusion successful!", newline=True)
         return True
   
   printResult(ironman_finished) 
   return False
      
      
def play_mission(mission_number=(3,2), repeat=5):
   
   print( "Playing mission %d.%d..."%mission_number )

   for i in range(repeat+1):
      check_if_vnc_error()
      printAction("Searching for mission %d-%d button..."%mission_number)
      mission_button_coords = locate_template("screens/mission_%d_%d.png"%mission_number, correlation_threshold=0.992, offset=(215,170))
      printResult(mission_button_coords)
      if not mission_button_coords:
         printAction( "Navigating to missions list...", newline=True )
         left_click((181,774)) # mission button
         time.sleep(3)
         scroll(0,1000)
#         swipe((250,390),(250,80))
         time.sleep(2)
         left_click((240,602)) #operations button
         
         time.sleep(int(uniform(2,4)))
         printAction( "Locating mission %d button..."%mission_number[0] )
         mission_button_coords = locate_template('screens/mission_list_%d.png'%mission_number[0], correlation_threshold=0.92, offset=(170,10))
         printResult(mission_button_coords)
         if not mission_button_coords:
            swipe((240,520),(240,80))
            time.sleep(int(uniform(1,2)))
            mission_button_coords = locate_template('screens/mission_list_%d.png'%mission_number[0], correlation_threshold=0.92)
            
         if not mission_button_coords:
            print( "Unable to locate mission buttion. This shouldn't happen. Dammit!" )
            return False
         
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
            
            out_of_energy = locate_template('screens/out_of_energy.png', correlation_threshold=0.985, print_coeff=False)
            #printResult(out_of_energy)
            
            mission_started = locate_template('screens/mission_bar.png', correlation_threshold=0.985)
            #printResult(mission_started)
               
            if out_of_energy:
               print( '' )
               printAction("No energy left! Exiting.", newline=True)
               
               back_key()
               return True
               
            if mission_started:
               print( '' )
               printAction("Mission started. Returning.", newline=True)
               back_key()
               time.sleep(int(uniform(1,2)))
               mission_success = True
               break
         
         if not mission_success:
            printAction("Timeout when waiting for mission screen", newline=True)
            return False
                                  
         
      
          

def start_marvel(user):
   
   def attempt_start(user):
      unlock_phone()
      clear_marvel_cache()
      launch_marvel()
      check_if_vnc_error()
      #printAction("Searching for
      printAction("Searching for login screen...")
      login_screen_coords = locate_template('screens/login_screen.png', correlation_threshold=0.992, retries=10, interval=4)
      printResult(login_screen_coords)
      if login_screen_coords:
         adb_login( login_screen_coords, user )
   
      login_success = False
      for i in range(10):
         time.sleep(int(uniform(2,4)))
         if locate_template('screens/home_screen.png', correlation_threshold=0.985, print_coeff=False):
            time.sleep(int(uniform(1,2)))
            left_click((346,551)) # kills ads
            login_success = True
            break
      
#      if login_success:
#         printAction( "Finished login success!!", newline=True)
#      else: 
#         printAction( "login FAILED!!!", newline=True)
#         
      return login_success
      
         
   all_ok = False
   for i in range(3):
      print( '' )
      print("Login attempt %d on account %s..."%(i,user))
      login_ok = attempt_start(user)
      printResult(login_ok)
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
   
def exit_marvel():
   check_if_vnc_error()
   clear_marvel_cache() # A little harsh...?
   lock_phone()
   check_if_vnc_error()
   
def lock_wait_unlock():
   lock_phone()
   #time.sleep(60*int(uniform(15,25)))
   time.sleep(60)
   
   unlock_phone()
            
def replay_all_macros():
   
   abort_if_vnc_died()
#   unlock_phone()
#   time.sleep(100)

   while True:
     
      if start_marvel_jollyma():
         play_mission((3,5), 2*15)
         exit_marvel()
           
      abort_if_vnc_died()
      time.sleep(60)
      
      if start_marvel_joinge():
         play_mission((3,5), 2*21)
         exit_marvel()

      abort_if_vnc_died()
      time.sleep(60)
     
      if start_marvel_jojanr():
         play_mission((3,5), 2*23)
         exit_marvel()
      
      abort_if_vnc_died()
      time.sleep(60)    


    
      time.sleep(60*uniform(45,70))

if __name__ == "__main__":   
#   replay_all_macros()
#   find_mission()
   fuse_ironman()
   pass
