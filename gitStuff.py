# gitStuff.py - git committing changes


from subprocess import call

print "\n*****\nfor new files first do:\ngit add [filename]\n*****\n"

call(["git", "commit", "-a"]) 
call(["git", "push", "origin", "master"])
