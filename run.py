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
   
   account = Accounts()
   
#   account.add('testAccount', password='testPassword')
#   account.edit('testAccount', email='something@gmail.com',
#                 type='bot', coins=0, last_harvest='2013-08-23 17:10:00')

   account.edit('testAccount', owner='Default')
   account.getAndroidId('testAccount')

if __name__ == "__main__":

   run()
