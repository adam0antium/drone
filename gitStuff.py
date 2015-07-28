# gitStuff.py - git admin file

#to get the complete repo use:
#   git clone https://github.com/adam0antium/drone.git

from subprocess import call

print "\n*****\nfor new files first do:\ngit add [filename]\n*****\n"

call(["git", "commit", "-a"]) 
call(["git", "push", "origin", "master"])
