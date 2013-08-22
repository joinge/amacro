from macro import *
from Accounts import Accounts

def run():

   # Abracho bfg376874
   # Chris   ddf493943
   # Dented  zpj296305
   # Frankie rnj978078
   # JoInge  bsv991976
   # Mark    jcp405955
   # TheMyth tgu808464
   
   setActiveDevice('192.168.10.10:5555')
   user.setCurrent("Joey")

#    createMultipleNewFakeAccounts([30],
#                                 referral=['qwz857729'],
#                                 description=['Dago'],
   
   accounts = Accounts()
   
   accounts.addNewAccount('testAccount', password='testPassword')

if __name__ == "__main__":

   run()
