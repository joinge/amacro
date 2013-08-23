import MySQLdb


class Accounts():
   
   def __init__(self):
      
      self.db = MySQLdb.connect(host='localhost', user='macro', passwd='moneymakers', db='macro')
      self.cur = self.db.cursor()
      self.account_fields = self.getAccountFields()
   

   def getAccountFields(self):
      
      self.cur.execute('SHOW COLUMNS FROM accounts;')
      
      return [i[0] for i in self.cur.fetchall()]
   
   
   def getAndroidId(self, name):
      
      return self.get(name, 'android_id')
   
   
   def getAccountsFor(self, user):
      
      self.cur.execute('SELECT name FROM accounts WHERE owner="%s";'%user)
      
      return self.cur.fetchall()
   
   def printAccounts(self):
      
      self.cur.execute('SELECT * FROM accounts;')

      for row in self.cur.fetchall():
         print row
         

   def add(self, name, **kwargs):
       
      fields = 'name'
      values = '"%s"'%name
      
      for key,val in kwargs.items():
         if key in self.account_fields:
            fields += ', %s'%key
            values += ', "%s"'%val
               
      self.cur.execute('INSERT INTO accounts (%s) VALUES(%s);'%(fields,values))


   def edit(self, name, **kwargs):
      
      items = ''
      
      first_run = True
      for key,val in kwargs.items():
         if key in self.account_fields:
            if first_run:
               first_run = False
            else:
               items += ', '
            items += '%s="%s"'%(key,val)
               
      self.cur.execute('UPDATE accounts SET %s WHERE name="%s";'%(items,name))
      
      
   def get(self, name, **kwargs):
       
      fields = ''
      first_run = True
      for key in kwargs.keys():
         if key in self.account_fields:
            if first_run:
               first_run = False
            else:
               fields += ', '
            fields += '%s'%key
            
      self.cur.execute('SELECT (%s) FROM accounts WHERE name="%s";'%(fields,name))
      
      return self.cur.fetchall()
      
      
if __name__ == "__main__":

   from run import run
   run()