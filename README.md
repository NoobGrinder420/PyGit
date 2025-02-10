# PyGit
I made my own version of git using python as a way to learn file management (os, sys), hashing, and connecting urls in python. I also developed a deeper understanding of version history management with git (hashing, compressing etc)

# How to use:
depending on your OS:
python3 {path to main.py} command_name parameter(s)
**or**
python {path to main.py} command_name parameter(s)

# Commands implemented:
(Terminal input is prefixed with $. it assumes that your current directory has the main.py file)
(comments prefixed with # like python syntax)
(output has no prefix)

'''
$ python3 main.py init
git initialised!
'''
**parameters implemented:** none
**description:** initializes a Git repository by creating a .git directory with some files & directories inside it.


'''
$ python3 main.py cat-file -p <blob_sha1_hash>
hello world # This is the contents of the blob
'''
**parameters implemented:** -p <blob_sha1_hash> (compulsory)
**description:** used to view the type of an object, its size, and its content. (works only for blob objects)


'''
$ git hash-object -w test.txt
95d09f2b10159347eece71399a7e2e907ea3df4f # This is the sha1 hash of the blob (content of file stored .git/objects/95/d09f2b10159347eece71399a7e2e907ea3df4f)
'''
**parameters implemented:** -w (writes the blob to .git/objects)
**description:** used to compute the SHA1 hash of a Git blob


'''
$ python3 main.py ls-tree <tree_sha>
040000 tree <tree_sha_1>    dir1
040000 tree <tree_sha_2>    dir2
100644 blob <blob_sha_1>    file1
'''
**parameters implemented:** --name-only (only outputs names of files and folders)
eg.
'''
python3 main.py ls-tree --name-only <tree_sha>
dir1
dir2
file1
'''

**description:** used to inspect a tree object.

'''
$ python3 main.py write-tree #assumes all changes are staged in the current working directory
4b825dc642cb6eb9a060e54bf8d69288fbee4904 #returns sha1 hash of the tree object
'''
**parameters implemented:** none
**description:** creates a tree object from the current state of the "staging area". The staging area is a place where changes go when you run git add.
                 I did not implement a staging area in my code and will assume that all files in the working directory are staged.



'''
$ python3 main.py commit-tree <tree_sha> -p <commit_sha> -m <message>
'''
**parameters implemented:** -p <parent_sha> (optional param to store commit object under .git/objects/parents_sha/ instead of .git/objects) -m (includes message in commit)
**description:** creates a commit object and prints its 40-char SHA to stdout.


'''
$ python3 main.py clone https://github.com/blah/blah <some_dir>
'''
**parameters implemented:** none
**description:** creates <some_dir> and clones the given repository into it given the github url



