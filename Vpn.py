import Exception

class Vpn():

   def updateVPN(self):
      
      printAction('Starting VPN...')
      
      device.adbShell('am force-stop com.privateinternetaccess.android')
      
      device.adbShell('echo "am start -n com.privateinternetaccess.android/.LauncherActivity" \| su')
      
      locateTemplate('vpn_checkbox')
      
      time.sleep(8)
      
      homeKey()
      
      print("hello")
      
      
      # am start -n com.privateinternetaccess.com/.LauncherActivity
      # am force-close com.privateinternetaccess.com
      
      # In /data/data/com.privateinternetaccess.android/shared_prefs/com.privateinternetaccess.android_preferences.xml
         # <?xml version='1.0' encoding='utf-8' standalone='yes' ?>
         # <map>
         # <string name="lport"></string>
         # <boolean name="autoconnect" value="true" />
         # <string name="onBootProfile">4335cfe0-4069-40cb-9e19-a4a91016634d</string>
         # <string name="rport">auto</string>
         # <boolean name="autostart" value="true" />
         # <string name="selectedregion">germany</string>
         # </map>
         
      # MainActivity.xml
         # <?xml version='1.0' encoding='utf-8' standalone='yes' ?>
         # <map>
         # <string name="password">spzCg2PwVy</string>
         # <string name="login">p1526501</string>
         # </map>
         
   def ensureStealth(self):
      
      printAction('Stealth check', newline=True)
      
      ensureValidIP()
      setVPNFirewall()
      
         
   def ensureValidIP(self, recursing=False):
      """
      
      """
      
      host_ip = myPopen('wget http://www.joinge.net/getmyip.php -q -O -')
      printAction('   Host IP')
      print(host_ip)
      
      vm_ip = device.adbShell('"wget http://www.joinge.net/getmyip.php -q -O -"')
      printAction('   Android IP (%s)'%device.active_device)
      print(vm_ip)
      
      # This sanity check doesn't ensure valid IP range but should be sufficient
      filtered_vm_ip = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', vm_ip)
      
      if not filtered_vm_ip:
         printAction('   VM IP sanity check...', res=False)   
         print('ERROR: VM IP does not seem to be sane.')
         
         if recursing:
            raise Exception('ERROR: Unable to recover!')
         else:
            updateVPN()
            setVPNFirewall()
            ensureValidIP(True)
      
      else:
         printAction('   VM IP sanity check...', res=True)
      
      if host_ip == vm_ip:
         printAction('   IPs differ?', res=False)   
         print('ERROR: IPs are identical.')
         
         if recursing:
            raise Exception('ERROR: Unable to recover!')
         else:
            updateVPN()
            setVPNFirewall()
            ensureValidIP(True)
         
      else:
         printAction('   IPs differ?', res=True)
      

   def setVPNFirewall(self, allow_only_current_vpn_server = True):
      
      printAction('   Setting up VPN firewall...')
      device_no = device.getInfo('deviceNo')
      
      try:
         os.mkdir(TEMP_PATH+'/pia%d'%device_no)
      except:
         pass

      curdir = os.getcwd()
      os.chdir(TEMP_PATH+'/pia%d'%device_no)
      #myPopen('rm *.ovpn *.crt *.vpn *.zip', stderr='devnull')
      myPopen('rm *', stderr='devnull')
   #   myPopen('wget -q https://www.privateinternetaccess.com/openvpn/openvpn.zip')

      pia_ip_list = []

      if allow_only_current_vpn_server:
         vm_ip = device.adbShell('"wget http://www.joinge.net/getmyip.php -q -O -"')
      
         # This sanity check doesn't ensure valid IP range but should be sufficient
         filtered_vm_ip = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', vm_ip)
         
         if filtered_vm_ip:
            pia_ip_list = [vm_ip]
         else:
            print('ERROR: Unable to read current VPN IP')
            sys.exit()
         
      else:
         # Fetch and extract new data (if it was changed)
         myPopen('wget -q -O openvpn.zip https://www.privateinternetaccess.com/openvpn/openvpn.zip')
         myPopen('unzip -q openvpn.zip')
         
         # Perform DNS lookups to find each server's IPs
         pia_servers = myPopen('grep -h "remote " *ovpn | sort')
         
         for pia_server in re.findall('remote\s([a-z\.-]+)\s[0-9]+', pia_servers):
            dns_ip_string = myPopen('dig %s A +short | sort'%pia_server)
            dns_ips = re.split('\n',dns_ip_string)
            dns_ips.pop(-1)
            pia_ip_list.extend(dns_ips) 
            
         pia_ip_list.sort()

      # Start building iptables script - starts by overwriting old file
      iptables_file = open('iptables.vpn', 'w')
      
      print('iptables -F',                               file=iptables_file)
      print('iptables -A INPUT  -i tun+ -j ACCEPT',      file=iptables_file)
      print('iptables -A OUTPUT -o tun+ -j ACCEPT',      file=iptables_file)
      print('iptables -A INPUT  -s 127.0.0.1 -j ACCEPT', file=iptables_file)
      print('iptables -A OUTPUT -d 127.0.0.1 -j ACCEPT', file=iptables_file)
      
      for ip  in pia_ip_list:
         print('iptables -A INPUT  -s %s -j ACCEPT'%ip, file=iptables_file)
         print('iptables -A OUTPUT -d %s -j ACCEPT'%ip, file=iptables_file)

      # Add access for host-only network
      print('iptables -A INPUT  -s 192.168.1%d.1 -j ACCEPT'%device_no, file=iptables_file)
      print('iptables -A OUTPUT -d 192.168.1%d.1 -j ACCEPT'%device_no, file=iptables_file)

      # Stop anything not from PIA or internal or localhost
      print('iptables -A INPUT -j DROP', file=iptables_file)
      print('iptables -A OUTPUT -j DROP', file=iptables_file)

      iptables_file.close()
      
      device.adb('push iptables.vpn /sdcard/macro/', stdout='devnull', stderr='devnull', log=False)
      device.adbShell('echo "sh /sdcard/macro/iptables.vpn" \| su')

      os.chdir(curdir)

      printResult(True)
      