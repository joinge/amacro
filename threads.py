# cnee --record --events-to-record -1 --mouse --keyboard -o /tmp/xnee.xns -e /tmp/xnee.log -v

# cnee --record --seconds-to-record 150 --mouse --keyboard -o joinge.xns -e joinge.log -v


from subprocess import Popen, PIPE
import logging
import multiprocessing
import os
devnull = open(os.devnull, 'w')

logging.getLogger('')

class MyPopen(multiprocessing.Process):
   def __init__(self, queue, *args, **kwargs):
#      super(Run,self).__init__()
      multiprocessing.Process.__init__(self)
      self.queue = queue
      self.args = args
      self.kwargs = kwargs
      
      self.LOGGING = True
      if 'log' in self.kwargs:
         self.LOGGING = self.kwargs.pop('log')
      
      self.STDOUT = True
      if 'stdout' in self.kwargs:
         if self.kwargs['stdout'] == 'devnull':
            self.kwargs['stdout'] = PIPE
            self.STDOUT = False
         else:
            self.kwargs['stdout'] = kwargs['stdout']   
      else:
         self.kwargs['stdout'] = PIPE
      
      self.STDERR = True
      if 'stderr' in self.kwargs:
         if self.kwargs['stderr'] == 'devnull':
            self.kwargs['stderr'] = PIPE
            self.STDERR = False
         else:
            self.kwargs['stdout'] = kwargs['stderr']   
      else:
         self.kwargs['stderr'] = PIPE
         
      self.QUIET = False
      if not self.STDOUT and not self.STDERR:
         self.QUIET = True
         
      if not 'shell' in kwargs:
         self.kwargs['shell'] = True
         
           
   def run (self):
      
      proc = Popen(*self.args, **self.kwargs) 
      
      if not self.LOGGING and self.QUIET:
         proc.wait()
         
      else:
         if self.LOGGING:
            sout = proc.stdout.read()
            serr = proc.stderr.read()
            if sout:
               logging.debug(sout)
            if serr:
               logging.error(serr) 

            if self.STDOUT:
               self.queue.put(sout)
            if self.STDERR:
               self.queue.put(serr)             
               
         else:
            if self.STDOUT:
               self.queue.put(proc.stdout.read())
            if self.STDERR:
               self.queue.put(proc.stderr.read())         

class MyRun(multiprocessing.Process):
   def __init__(self, function, queue, *args, **kwargs):
      multiprocessing.Process.__init__(self)
      self.function = function
      self.queue = queue
      self.args = args
      self.kwargs = kwargs
           
   def run (self):
      
      out = self.function(*self.args, **self.kwargs)
#      if type(out) == str:
#         logging.debug(out)
      self.queue.put(out)


def myPopen(*args, **kwargs):
   
   queue = multiprocessing.Queue()
   
   if not 'timeout' in kwargs:
      timeout = 10
   else:
      timeout = kwargs['timeout']
      
   process = MyPopen(queue, *args, **kwargs)
   process.start()
#    process.run()
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
   
