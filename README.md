# OSX-Pineapple-Backdoor
A collection of python-based scripts that exploit a privilege escalation vulnerability in OS X versions 10.10.2 - 10.10.5 and sets up a listening client that allows custom backdoor activities.
## Usage
In the target computer, run the pineapple-exec.py python script. After a few seconds, the listener client should be triggered. In order to connect to it, run the getPineapple.py script with the host IP address and port as parameters.
## Requirements
The target computer must be running OS X 10.10.2 - 10.10.5 and have python installed. 
## Disclaimer
These scripts are not to be used for malicious purposes, only for cybersecurity educational purposes.
Persistence scripts are not in working order in order to avoid misuse of backdoor.
## Note
This exploit modifies your /etc/sudoers file to include "ALL ALL=(ALL) NOPASSWD: ALL", which gives unrestricted access to root through the sudo command. After testing, make sure to delete the additional line at the end of the file.
