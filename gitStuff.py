# gitStuff.py - git admin file

#to get the complete repo use:
#   git clone https://github.com/adam0antium/drone.git

#to create a new branch locally use "git checkout -b branchname", and to push it back to the 
#	remote use "git push origin branchname"

#to get a single branch use:
#	git clone -b branchName --single-branch https://github.com/adam0antium/drone.git

#to make a commit with all changes included use "git commit -a"

#to push the commit back to the remote use "push origin branchname" 

#to merge a branch into the master, first update to latest branch version with  
# 	"git checkout branchname", "git pull", then get latest master version with 
#	"git checkout mastername", "git pull", then do a "git merge branchname",then check with "git show"
#	then delete local branch with "git branch -d branchname", then delete remote branch with 
#	"git push origin :branchname"

#to tag (annotated) use "git tag -a tagName -m 'git tag message' "
# 	then to push the tag to remote use 'git push origin tag tagName'
#	or also can use 'git push --follow-tags' which will push commits and also tags that are annotated and reachable

#after a merge with conflicts fix them with a mergetool eg meld or kdiff3
#	git mergetool -t meld

#use meld to combine files from different branches to current working directory files
#	git difftool --tool=meld automated:signalLogger.py ./signalLogger.py