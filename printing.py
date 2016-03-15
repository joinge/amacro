from __future__ import print_function
import multiprocessing
import select
import sys

PAD = 60

import os
import json
import logging
import logging.config

def setupLogging(
    default_path='log.json', 
    default_level=logging.INFO
):
   """Setup logging configuration

   """
   
   print("Initiating logging")
   path = default_path
   if os.path.exists(path):
      with open(path, 'rt') as f:
         config = json.load(f)
      logging.config.dictConfig(config)
   else:
      logging.basicConfig(level=default_level)
      
   logger = logging.getLogger("")
   logger.info("Logger initiated")
   


msg_queue = multiprocessing.Queue()
def myPrint(arg, **kwargs):

   msg = ''
#    max_num = 500
#    while True and max_num>0:
#       if not msg_queue.empty():
#          msg = msg + msg_queue.get(block=True)
#       else:
#          break
#       max_num = max_num - 1
# #   msg = ''
# #   if not msg_queue.empty():
#      msg = msg_queue.get()
   
   if 'msg_type' in kwargs:
      severity = kwargs.pop('msg_type')
      getattr(logging, severity)(msg+arg,**kwargs)
   else:
      logging.debug(msg+arg,**kwargs)
      
   print(arg, **kwargs)

def printResult(res, msg_type='debug'):
   global msg_queue
   msg = ''
   
   while True:
      if not msg_queue.empty():
         msg = msg + msg_queue.get(block=True)
      else:
         break
      
   if isinstance(res, basestring):
      getattr(logging, msg_type)(msg.ljust(PAD, ' ')+res)
      sys.stdout.write(res)
   elif res:
      getattr(logging, msg_type)(msg.ljust(PAD, ' ')+':)')
      sys.stdout.write(":)")
   else:
      getattr(logging, msg_type)(msg.ljust(PAD, ' ')+':s')
      sys.stdout.write(":s")
      
   sys.stdout.flush()
   sys.stdout.write("\n")
   
def printQueue(string):
   msg_queue.put(string, block=True)
   
def printLog(string, newline=True, msg_type='debug'):
   string = "   %s" % str
   global msg_queue
      
   if newline:
      getattr(logging, msg_type)(string)
   else:
      msg_queue.put(string, block=True)

def printAction(str, res=None, newline=False, msg_type='debug'):
   string = "   %s" % str
   global msg_queue
      
   if newline:
      getattr(logging, msg_type)(string.ljust(PAD, ' '))
      sys.stdout.write(string.ljust(PAD, ' '))
      sys.stdout.flush()
      sys.stdout.write("\n")
   else:
      msg_queue.put(string.ljust(PAD, ' '), block=True)
      sys.stdout.write(string.ljust(PAD, ' '))
      sys.stdout.flush()
   if res:
      printResult(res, msg_type=msg_type)
      
def printNotify(message, timeout=30):
   myPrint("notify() - THIS FUNCTION IS DISABLED!!!")
#    myPrint("NOTIFICATION: " + message)
#    notify()
#    myPrint("Type Enter to continue (will do so anyways in 30s)")
#    
#    select.select([sys.stdin], [], [], timeout)