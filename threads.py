#cnee --record --events-to-record -1 --mouse --keyboard -o /tmp/xnee.xns -e /tmp/xnee.log -v

#cnee --record --seconds-to-record 150 --mouse --keyboard -o joinge.xns -e joinge.log -v


from subprocess import Popen, PIPE
import multiprocessing, os
devnull = open(os.devnull,'w')

class MyPopen( multiprocessing.Process ):
   def __init__(self, queue, *args, **kwargs):
#      super(Run,self).__init__()
      multiprocessing.Process.__init__(self)
      self.queue = queue
      self.args = args
      self.kwargs = kwargs
      
      self.SUPPRESS_OUTPUT = False
      
      if 'stdout' in self.kwargs:
         if self.kwargs['stdout'] == 'devnull':
            self.kwargs['stdout'] = devnull
            self.SUPPRESS_OUTPUT = True
         else:
            self.stdout = kwargs['stdout']   
      else:
         self.kwargs['stdout'] = PIPE
         
      if 'stderr' in self.kwargs:
         if self.kwargs['stderr'] == 'devnull':
            self.kwargs['stderr'] = devnull
            self.SUPPRESS_OUTPUT = True
         else:
            self.stdout = kwargs['stderr']   
      else:
         self.kwargs['stderr'] = PIPE
         
      if not 'shell' in kwargs:
         self.kwargs['shell'] = True
         
           
   def run ( self ):
      
      if self.SUPPRESS_OUTPUT:
         Popen(*self.args, **self.kwargs).wait()
#          Popen('adb shell /system/bin/screencap -p /sdcard/screenshot.png', stdout=devnull, shell=True).wait()
#          self.queue.put(0)
      else:
         out = Popen(*self.args, **self.kwargs).stdout.read()
         self.queue.put(out)


class MyRun( multiprocessing.Process ):
   def __init__(self, function, queue, *args, **kwargs):
      multiprocessing.Process.__init__(self)
      self.function = function
      self.queue = queue
      self.args = args
      self.kwargs = kwargs
           
   def run ( self ):
      
      out = self.function(*self.args, **self.kwargs)
      
      self.queue.put(out)


def myPopen(*args, **kwargs):
   
   queue = multiprocessing.Queue()

   if not 'timeout' in kwargs:
      timeout = 10
   else:
      timeout = kwargs['timeout']
      
   process = MyPopen(queue, *args, **kwargs)
   process.start()
   process.join(timeout) 
   
   if not queue.empty():
      return queue.get(timeout=timeout)
   else:
      return None
   

def myRun(function, *args, **kwargs):

   queue = multiprocessing.Queue()
   
   if not 'timeout' in kwargs:
      timeout = 10
   else:
      timeout = kwargs['timeout']
   
   process = MyRun(function, queue, *args, **kwargs)
   process.start()
   
   res = queue.get(timeout=timeout)
   
   if res != None:
      process.join(0.5)
      if process.is_alive():
         process.terminate()
         
#       if    process.join(0.5): pass
#       else: process.terminate()
         
      return res
   else:
      process.terminate()
      return None
   
#    if not queue.empty():
#       return queue.get(timeout=timeout)
#    else:
#       process.terminate()
#       return None   
#    
#    process.join(timeout) 
   
