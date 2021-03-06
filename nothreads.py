# cnee --record --events-to-record -1 --mouse --keyboard -o /tmp/xnee.xns -e /tmp/xnee.log -v

# cnee --record --seconds-to-record 150 --mouse --keyboard -o joinge.xns -e joinge.log -v


from printing import myPrint
from subprocess import Popen, PIPE
import multiprocessing
import os
devnull = open(os.devnull, 'w')


class MyPopen():
   def __init__(self, *args, **kwargs):
#      super(Run,self).__init__()
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
            self.kwargs['stderr'] = kwargs['stderr']   
      else:
         self.kwargs['stderr'] = PIPE
         
      self.QUIET = False
      if not self.STDOUT and not self.STDERR:
         self.QUIET = True
         
      if not 'shell' in kwargs:
         if os.name == "posix":
            self.kwargs['shell'] = True
         else:
            self.kwargs['shell'] = False
         
           
   def run (self):
      
      proc = Popen(*self.args, **self.kwargs)
      
      if not self.LOGGING and self.QUIET:
         proc.wait()
         
      else:
         if self.LOGGING:
            sout = proc.stdout.read()
            try:
               serr = proc.stderr.read()
            except:
               self.STDERR = False
               serr = None
               
#             if sout:
#                log.debug(sout)
#             if serr:
#                log.error(serr)

            if self.STDOUT and self.STDERR:
               return sout+serr
            if self.STDOUT:
               return sout
            if self.STDERR:
               return serr     
               
         else:
            sout = proc.stdout.read()
            try:
               serr = proc.stderr.read()
            except:
               self.STDERR = False
               serr = None
               
            if self.STDOUT and self.STDERR:
               return sout + serr
            if self.STDOUT:
               return sout
            if self.STDERR:
               return serr
            

def myPopen(*args, **kwargs):
   
   if not 'timeout' in kwargs:
      timeout = 10
   else:
      timeout = kwargs.pop('timeout')
      
   process = MyPopen(*args, **kwargs)
   return process.run()

def myRun(function, *args, **kwargs):

   if 'timeout' in kwargs:
      timeout = kwargs.pop('timeout')
   
   return function(*args, **kwargs)
   
#    if not queue.empty():
#       return queue.get(timeout=timeout)
#    else:
#       process.terminate()
#       return None   
#    
#    process.join(timeout) 
   
