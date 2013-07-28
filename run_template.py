
from macro import *

def run():
   
  setActiveDevice('192.168.10.10:5555')
  user.setCurrent("Joey")
   
  createMultipleNewFakeAccounts(
     [100,200], referral=["gjx558947","tgu808464"],
     interval=(0,0), never_abort=True, draw_ucp=False)

if __name__ == "__main__":

   run()
