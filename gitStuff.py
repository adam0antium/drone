# gitStuff.py - git admin file

#to get the complete repo use:
#   git clone https://github.com/adam0antium/drone.git

#to get a single branch use:
#	git clone -b theBranchName --single-branch https://github.com/adam0antium/drone.git
#NB this script will not work for other branches since the last call is to push to master

#to merge a branch into the master first checkout both versions, then switch to master
#	with "git checkout master", then do a "git merge branch",then check with "git show"

from subprocess import call

print "\n*****\nfor new files first do:\ngit add [filename]\n*****\n"

call(["git", "commit", "-a"]) 
call(["git", "push", "origin", "master"])
