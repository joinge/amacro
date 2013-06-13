#cnee --record --events-to-record -1 --mouse --keyboard -o /tmp/xnee.xns -e /tmp/xnee.log -v

#cnee --record --seconds-to-record 150 --mouse --keyboard -o joinge.xns -e joinge.log -v


from subprocess import Popen, PIPE
import multiprocessing


class MyPopen( multiprocessing.Process ):
   def __init__(self, queue, *args, **kwargs):
#      super(Run,self).__init__()
      multiprocessing.Process.__init__(self)
      self.queue = queue
      self.args = args
      self.kwargs = kwargs
      
      if not 'stdout' in kwargs:
         self.kwargs['stdout'] = PIPE
         
      if not 'shell' in kwargs:
         self.kwargs['shell'] = True
         
           
   def run ( self ):
      
      out = Popen(*self.args, **self.kwargs).stdout.read()
      
      self.queue.put(out)


class Run( multiprocessing.Process ):
   def __init__(self, function, queue, *args, **kwargs):
      multiprocessing.Process.__init__(self)
      self.function = function
      self.queue = queue
      self.args = args
      self.kwargs = kwargs
           
   def run ( self ):
      
      out = self.function(*self.args, **self.kwargs)
      
      self.queue.put(out)


def myPopen(timeout=5, *args, **kwargs):

   queue = multiprocessing.Queue()
   
   process = MyPopen(queue, *args, **kwargs)
   process.start()
   process.join(timeout) 
   
   if not queue.empty():
      return queue.get(timeout=timeout)
   else:
      return None
   

def run(function, timeout=5, *args, **kwargs):

   queue = multiprocessing.Queue()
   
   process = Run(function, queue, *args, **kwargs)
   process.start()
   process.join(timeout) 
   
   if not queue.empty():
      return queue.get(timeout=timeout)
   else:
      return None