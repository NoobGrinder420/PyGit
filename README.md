# PyGit

I made my own version of Git using Python as a way to learn about terminal and file management in python (`os`, `sys`), hashing, and connecting URLs in Python. I also developed a deeper understanding of version history management with Git (hashing, compressing, etc.).

## How to Use

Depending on your OS, run:

```sh
python3 {path to main.py} command_name parameter(s)
```
**or**
```sh
python {path to main.py} command_name parameter(s)
```

## Commands Implemented

(Terminal input is prefixed with `$`. It assumes that your current directory has the `main.py` file.)  
(Comments are prefixed with `#`, like Python syntax.)  
(Output has no prefix.)

### `init`
```sh
$ python3 main.py init
git initialised!
```
**Parameters implemented:** None  
**Description:** Initializes a Git repository by creating a `.git` directory with some files & directories inside it.

---

### `cat-file`
```sh
$ python3 main.py cat-file -p <blob_sha1_hash>
hello world # This is the contents of the blob
```
**Parameters implemented:** `-p <blob_sha1_hash>` (compulsory)  
**Description:** Used to view the type of an object, its size, and its content. (Works only for blob objects.)

---

### `hash-object`
```sh
$ python3 main.py hash-object -w test.txt
95d09f2b10159347eece71399a7e2e907ea3df4f # This is the SHA1 hash of the blob (content of file stored in .git/objects/95/d09f2b10159347eece71399a7e2e907ea3df4f)
```
**Parameters implemented:** `-w` (writes the blob to `.git/objects`)  
**Description:** Used to compute the SHA1 hash of a Git blob.

---

### `ls-tree`
```sh
$ python3 main.py ls-tree <tree_sha>
040000 tree <tree_sha_1>    dir1
040000 tree <tree_sha_2>    dir2
100644 blob <blob_sha_1>    file1
```
**Parameters implemented:** `--name-only` (only outputs names of files and folders)  

Example:
```sh
$ python3 main.py ls-tree --name-only <tree_sha>
dir1
dir2
file1
```
**Description:** Used to inspect a tree object.

---

### `write-tree`
```sh
$ python3 main.py write-tree # Assumes all changes are staged in the current working directory
4b825dc642cb6eb9a060e54bf8d69288fbee4904 # Returns SHA1 hash of the tree object
```
**Parameters implemented:** None  
**Description:** Creates a tree object from the current state of the "staging area".  
I did not implement a staging area in my code and will assume that all files in the working directory are staged.

---

### `commit-tree`
```sh
$ python3 main.py commit-tree <tree_sha> -p <commit_sha> -m <message>
```
**Parameters implemented:**  
- `-p <parent_sha>` (optional; stores the commit object under `.git/objects/parents_sha/` instead of `.git/objects/`)  
- `-m` (includes message in commit)  

**Description:** Creates a commit object and prints its 40-character SHA to stdout.

---

### `clone`
```sh
$ python3 main.py clone https://github.com/blah/blah <some_dir>
```
**Parameters implemented:** None  
**Description:** Creates `<some_dir>` and clones the given repository into it given the GitHub URL.
