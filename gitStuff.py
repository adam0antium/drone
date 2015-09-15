# gitStuff.py - git admin file

#to get the complete repo use:
#   git clone https://github.com/adam0antium/drone.git

#to get a single branch use:
#	git clone -b theBranchName --single-branch https://github.com/adam0antium/drone.git
#NB this script will not work for other branches since the last call is to push to master

#to make a commit with all changes included use "git commit -a"

#to push the commit back to the remote use "push origin branchname" 

#to merge a branch into the master, first update to latest branch version with  
# 	"git checkout branchname", "git pull", then get latest master version with 
#	"git checkout mastername", "git pull", then do a "git merge branchname",then check with "git show"
#	then delete local branch with "git branch -d branchname", then delete remote branch with 
#	"git push origin :branchname"

