
from Accounts import Accounts
from printing import printAction, myPrint


# The user object deals with user info 
class Users():
   
   def __init__(self, name=None):
      
      if name:
         self.current = name
      else:
         self.current = '-'

      self.setCurrent(self.current)
      
      
   def setCurrent(self, user):

      self.current = user
      self.accounts = self.listAccounts()
      
      printAction("Current user:")
      myPrint(user)
      
      
   def getCurrent(self):
      
      return self.current
   
   
   def listAccounts(self):
      
      account = Accounts()
      return account.getAccountsFor(self.current)
   
 
user = Users()
      
      
if __name__ == "__main__":

   from run import run
   run()