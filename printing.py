from __future__ import print_function
import logging
import multiprocessing
import select
import sys

PAD = 60

msg_queue = multiprocessing.Queue()
def myPrint(arg, **kwargs):
   
   msg = ''
#    if not msg_queue.empty():
#       msg = msg_queue.get()
   
   if 'type' in kwargs:
      severity = kwargs.pop('type')
      getattr(logging, severity)(msg+arg,**kwargs)
   else:
      logging.debug(msg+arg,**kwargs)
      
   print(msg+arg, **kwargs)

def printResult(res, msg_type='debug'):
   global msg_queue
   msg = ''
   
   if not msg_queue.empty():
      msg = msg_queue.get()
      
#   logging.debug('Happy Hoppy')
   if res:
      getattr(logging, msg_type)(msg.ljust(PAD, ' ')+':)')
      sys.stdout.write(":)")
   else:
      getattr(logging, msg_type)(msg.ljust(PAD, ' ')+':s')
      sys.stdout.write(":s")
      
   sys.stdout.flush()
   sys.stdout.write("\n")

def printAction(str, res=None, newline=False, msg_type='debug'):
   string = "   %s" % str
   global msg_queue
      
   if newline:
      getattr(logging, msg_type)(string)
      sys.stdout.write(string.ljust(PAD, ' '))
      sys.stdout.flush()
      sys.stdout.write("\n")
   else:
      msg_queue.put(string.ljust(PAD, ' '), True)
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