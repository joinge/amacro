import MySQLdb

class Accounts():
   
   def __init__(self):
      
      self.db = MySQLdb.connect(host='localhost', user='macro', passwd='moneymakers', db='macro')

      self.cur = self.db.cursor()


   def printAccounts(self):
      
      self.cur.execute('SELECT * FROM accounts;')

      for row in self.cur.fetchall():
         print row
   
   
   def addNewAccount(self, user, **kwargs):
      
      allowed_values = ['password', 'email', 'type', 'coins', 'last_harvest']
      types = ''
      values = ''
      first_run = True
      
      for key,val in kwargs.items():
         if key in allowed_values:
            if first_run:
               first_run = False
            else:
               types  += ', '
               values += ', '
            types  += '"%s"'%key
            values += '"%s"'%val
               
      self.cur.execute('INSERT INTO accounts (%s) VALUES(%s);'%(types,values))
      
      
if __name__ == "__main__":

   from run import run
   run()