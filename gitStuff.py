# gitStuff.py - git admin file

#to get the complete repo use:
#   git clone https://github.com/adam0antium/drone.git

#to get a single branch use:
#	git clone -b theBranchName --single-branch https://github.com/adam0antium/drone.git
#NB this script will not work for other branches since the last call is to push to master

from subprocess import call

print "\n*****\nfor new files first do:\ngit add [filename]\n*****\n"

call(["git", "commit", "-a"]) 
call(["git", "push", "origin", "master"])
