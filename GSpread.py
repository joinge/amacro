'''
Created on Mar 29, 2016

@author: jbs
'''

# import requests
import gspread
import numpy as np
from scipy import interpolate
import scipy as sp
import time
import traceback

from oauth2client.service_account import ServiceAccountCredentials
# from numexpr.expressions import kind_rank


class GSpread:
   
   def __init__(self, credentials_json_file='RivalElite-87b48c4a674e.json', sheet_name='RE Macro Control', tab_name='General'):
      self.scope = ['https://spreadsheets.google.com/feeds']
      
      self.credentials_json_file = credentials_json_file
      self.sheet_name = sheet_name
      self.tab_name = tab_name
      
      self.initialized = False      
      
      print "hello"
      
   def intialize(self):
      try:
         self.setupConnection()
         self.initialized = True
         
         self.updateAll()
      except Exception as e:
         print traceback.format_exc()
         print e
      
   def setupConnection(self):
      try:
         self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_json_file, self.scope)
      
         self.gspread = gspread.authorize(self.credentials)

         self.sheet = self.gspread.open(self.sheet_name)
      
         self.tab = self.sheet.worksheet(self.tab_name)
      except Exception as e:
         print e

   def updateAll(self):
      
      if not self.initialized:
         self.intialize()
      
      self.user_info = {}
      for i in range(2):
         try:
            self.data = self.tab.get_all_values()
            break
         except:
            self.setupConnection()
         
      try:
         for i in range(len(self.data)-4):
            user_row = self.data[i+4] # Starts at row 5
            name = user_row[0]
            if user_row[1] == 'Yes':
               enabled = True
            else:
               enabled = False
            attack_type = user_row[2].lower()
            
            self.user_info["%d.%s"%(i+1,name)] = {"enabled":enabled, "login_side":"left", "attack_type":attack_type, "ancient":'Malice'}
      except Exception as e:
         print traceback.format_exc()
         print e
         print("ERROR: Unable to pull data from spreadsheet.")
         self.user_info["1.Joey"] = {"enabled":True, "login_side":"left", "attack_type":"multiplayer", "ancient":'Malice'}
         self.user_info["2.Cherie"] = {"enabled":True, "login_side":"left", "attack_type":"multiplayer", "ancient":'Malice'}
#          self.user_info["3.Rupert"] = {"enabled":False, "login_side":"left", "attack_type":"multiplayer", "ancient":'Malice'}
      

   def getUserInfo(self):
      if not self.initialized:
         self.intialize()
      
      return self.user_info
   
   def setStatus(self, user, status):
      if not self.initialized:
         self.intialize()
      
      try:
         for i in range(len(self.data)-4):
            user_row = self.data[i+4] # Starts at row 5
            name = user_row[0]
            if name == user:
               for j in range(2):
                  try:
                     self.tab.update_acell('D%d'%(i+5), status)
                     self.tab.update_acell('E%d'%(i+5), time.asctime())
                     break
                  except:
                     self.setupConnection()
                  if i==2:
                     raise Exception("ERROR: Unable to update GSpread status")

               return
         
         print "ERROR: Unable to update GSpread status"
      except Exception as e:
         print traceback.format_exc()
         print e
         print("ERROR: Unable to update GSpread status.")
         
         
        
   
# gspread = GSpread()
