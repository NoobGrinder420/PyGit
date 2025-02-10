from operator import itemgetter
import os
import sys
import zlib
import hashlib
import struct
from pathlib import Path
from typing import Tuple, List, cast
import urllib.request

def init(parent):
    (parent / ".git").mkdir(parents=True)
    (parent / ".git" / "objects").mkdir(parents=True)
    (parent / ".git" / "refs").mkdir(parents=True)
    (parent / ".git" / "refs" / "heads").mkdir(parents=True)
    (parent / ".git" / "HEAD").write_text("ref: refs/heads/main\n")

    

def cat_file(blob_sha): #cat-file command
    #open file with 2 first hash chars as header and next 38 as file name
    with open(f".git/objects/{blob_sha[:2:]}/{blob_sha[2::]}", "rb") as blob_file:
        #decompress blob_file (all git files including blob_file are compressed using zlib)
        blob_raw = zlib.decompress(blob_file.read())
        
        #find blob content after null binary val
        blob_content = blob_raw[(blob_raw.find(b"\0")+1)::]
        
        #find blob size in bytes before null binary val
        blob_size = blob_raw[:blob_raw.find(b"\0"):] #not used
        
        #print content
        print(blob_content.decode(encoding="utf-8"), end="")
        
        
def hash_object(args):

        #splitting parameters
        options = [] #stores all options including -w
        do_write = False #to decide whether part 2 is called or not (-w)
        
        while args[0].startswith("-"):
            options.append(args[0])
            if args[0] == "-w":
                do_write = True # -w called
            args = args[1:] #removes all options so that only file name left
        
        file_name = args[0] #last element left in args is file name as options removed
        
        
        #PART 1: PRINTING SHA HASH
        #open file
        with open(file_name, "rb") as f:
            f_content = f.read()
        
        #using Git blob format <datatype> <length in bytes> <\0 (null bin char)> <content>
        blob_raw = f"blob {len(f_content)}\0".encode("utf-8") + f_content #f_content is still encoded
        
        #hashlib is Python built in module for cryptographic hashing
        SHA1_hash_raw = hashlib.sha1(blob_raw) #using SHA1 hashing here (20 chars)

        #hexdigest function is used for turning the raw binary hash into human readable format
        SHA1_hash_readable = SHA1_hash_raw.hexdigest() # 20 chars to 40 chars
        
        print(SHA1_hash_readable, end = "") #prints readable SHA hash
        
        
        #PART 2: WRITING SHA HASH IN .git/objects
        
        if do_write: #run part 2 only if -w parameter parsed
        
            #creates directory if it does not exist (of first 2 chars)
            #do not reference last 38 chars as it will create a folder (directory) instead of file
            os.makedirs(f".git/objects/{SHA1_hash_readable[:2:]}", exist_ok=True)
            
            #open file to write SHA hash to
            with open(f".git/objects/{SHA1_hash_readable[:2:]}/{SHA1_hash_readable[2::]}", "wb") as f:
                f_data = zlib.compress(blob_raw) #zlib compresses blob raw to store at SHA hash
                f.write(f_data)
                
                
def ls_tree(args):
    options = [] #stores options such as --name-only
    name_only = False #boolean to decide whether to print only the name if --name-only in options
    
    while args[0].startswith('-'):
        if args[0] == "--name-only":
            name_only = True
            
        options.append(args[0])
        args = args[1::] #removes values added to options so only tree_sha is left
    
    tree_sha = args[0]
    
    with open(f".git/objects/{tree_sha[:2:]}/{tree_sha[2::]}", "rb") as f:
        f_content = zlib.decompress(f.read())
        
    _, data = f_content.split(b'\0', maxsplit = 1)
    # removes <datatype tree> <tree byte size> while data stores the rest
    
    mode_name_SHAS = [] # list to store data in the form of [mode, name, 20_byte_sha1]
    # .hexdigest() vs .hex(): .hexdigest() is used for converting strings that were hashed using hashlib.sha1()
    while len(data) > 0:
        mode, data = data.split(b' ', 1)
        name, data = data.split(b'\0', 1)
        
        SHA1 = data[:20:].hex()
        data = data[20::]
        
        mode_name_SHAS.append([mode, name, SHA1])
        
    res = [] # res to return
    #name only?
    if name_only:
        for i in range(len(mode_name_SHAS)):
            res += (mode_name_SHAS[i][1].decode(encoding = "utf-8")) + "\n"
    
    else:
        for i in range(len(mode_name_SHAS)):
            res += (f"{mode_name_SHAS[i][0].decode(encoding='utf-8') if len(mode_name_SHAS[i][0].decode(encoding='utf-8')) == 6 else '0' + mode_name_SHAS[i][0].decode(encoding='utf-8')} {'tree' if '0' + mode_name_SHAS[i][0].decode(encoding='utf-8') == '040000' else 'blob'} {mode_name_SHAS[i][2]}    {mode_name_SHAS[i][1].decode(encoding='utf-8')}") + "\n"
    
    return ''.join(res)
    
#helper function for error handling etc
def create_blob_entry(path, write=True):
    with open(path, "rb") as f:
        data = f.read()
        
    header = f"blob {len(data)}\0".encode("utf-8")
    store = header + data
    sha1 = hashlib.sha1(store).hexdigest()
    
    if write:
        os.makedirs(f".git/objects/{sha1[:2:]}", exist_ok=True)
        
        with open(f".git/objects/{sha1[:2:]}/{sha1[2::]}", "wb") as f:
            f.write(zlib.compress(store))
        
    return sha1
    
    
def write_tree(path):
        
    #used during recursion
    if os.path.isfile(path):
        return create_blob_entry(path)
    
        
    #sorts files and folders in given path { os.listdir(path) }
    contents = sorted(
        os.listdir(path),
        
        #key is parameter to decided what values to sort by
        #trees always have files before folders if they have the same name so add a "/" for greater value (string sorting)
        key = lambda x: x if os.path.isfile(os.path.join(path, x)) else f"{x}/",
    )
    
    tree_content = b"" #final tree content
    
    for f in contents:
        if f == ".git": continue #ignore .git
        
        fullPath = os.path.join(path, f) #full path for f
        #fullPath = f"{path}/{f}" may not work depending on edge cases and Operating System
        
        if os.path.isfile(fullPath):
            #using git tree format <mode> <name><\0 (null bin char)><20_byte_sha1>
            tree_content += f"100644 {f}\0".encode("utf-8")
            
        else:
            tree_content += f"40000 {f}\0".encode("utf-8")
            
        
        SHA1_raw = bytes.fromhex(write_tree(fullPath))  # Converts hex string back to bytes (20 char sha1)

        tree_content += SHA1_raw
        
    
    header = f"tree {len(tree_content)}\0".encode("utf-8")
    tree_content = header + tree_content #adds tree header
    SHA1_readable = hashlib.sha1(tree_content).hexdigest() #40 char sha1
    
    os.makedirs(f".git/objects/{SHA1_readable[:2:]}", exist_ok=True) #makes dir for first 2 chars of tree sha1
    
    with open(f".git/objects/{SHA1_readable[:2:]}/{SHA1_readable[2:]}", "wb") as f:
        f.write(zlib.compress(tree_content))
        
    return SHA1_readable #returns tree sha1 (used for recursion)

        
def commit_tree(args):
    username = "NoobGrinder420"
    email = "d1h2a3n4v5i6n@gmail.com"
    unixTimestamp = "1717605000" #SGT
    UTC_offset = "+0800" #SGT
    message = ""
    commit_sha = ""
    
    options = []
    tree_sha = args[0]
    args = args[1:]
    
    
    
    while args:
        if args[0] == "-m":
            message = args[1]
            options.append(args[0])
            args = args[2:]
        elif args[0] == "-p":
            commit_sha = args[1]
            options.append(args[0])
            args = args[2:]
        else:
            options.append(args[0])
            args = args[1:]
            
    
    content = ( #information to be stored in commit object
        f"tree {tree_sha}\n"
        f"{ 'parent ' + commit_sha + '\n' if commit_sha else ''}" #handling no parent sha1 (commit_sha)
        f"author {username} <{email}> {unixTimestamp} {UTC_offset}\n"
        f"committer {username} <{email}> {unixTimestamp} {UTC_offset}\n\n"
        f"{message}\n"
    
    )
    
    content = content.encode()
    
    
    header = f"commit {len(content)}\0".encode("utf-8")
    content = header + content
    
    SHA1 = hashlib.sha1(content).hexdigest()
    compressed = zlib.compress(content)

    dirPath = os.path.join("./", f".git/objects/{SHA1[:2:]}")
    fullPath = os.path.join("./", f".git/objects/{SHA1[:2:]}/{SHA1[2::]}")
    os.makedirs(dirPath, exist_ok = True)
    
    with open(fullPath, "wb") as f:
        f.write(compressed)
        
    return SHA1
    
#helper function for clone
def read_object(parent, sha):
    pre = sha[:2]
    post = sha[2:]
    
    p = parent / ".git" / "objects" / pre / post
    bs = p.read_bytes()
    
    head, content = zlib.decompress(bs).split(b"\0", maxsplit=1)
    ty, _ = head.split(b" ")
    
    return ty.decode(), content
    
#helper function for clone
def write_object(parent, ty, content):
    content = ty.encode() + b" " + f"{len(content)}".encode() + b"\0" + content
    hash = hashlib.sha1(content).hexdigest()
    compressed_content = zlib.compress(content, level=zlib.Z_BEST_SPEED)
    
    pre = hash[:2]
    post = hash[2:]
    
    p = parent / ".git" / "objects" / pre / post
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(compressed_content)
    
    return hash
    
        
def clone(url, dir):
    parent = Path(dir)
    init(parent)
    # fetch refs
    req = urllib.request.Request(f"{url}/info/refs?service=git-upload-pack")
    with urllib.request.urlopen(req) as f:
        refs = {
            bs[1].decode(): bs[0].decode()
            for bs0 in cast(bytes, f.read()).split(b"\n")
            if (bs1 := bs0[4:])
            and not bs1.startswith(b"#")
            and (bs2 := bs1.split(b"\0")[0])
            and (bs := (bs2[4:] if bs2.endswith(b"HEAD") else bs2).split(b" "))
        }
        
    # render refs
    for name, sha in refs.items():
        Path(parent / ".git" / name).write_text(sha + "\n")
        
    # fetch pack
    body = (
        b"0011command=fetch0001000fno-progress"
        + b"".join(b"0032want " + ref.encode() + b"\n" for ref in refs.values())
        + b"0009done\n0000"
    )
    req = urllib.request.Request(
        f"{url}/git-upload-pack",
        data=body,
        headers={"Git-Protocol": "version=2"},
    )
    with urllib.request.urlopen(req) as f:
        pack_bytes = cast(bytes, f.read())
    pack_lines = []
    while pack_bytes:
        line_len = int(pack_bytes[:4], 16)
        if line_len == 0:
            break
        pack_lines.append(pack_bytes[4:line_len])
        pack_bytes = pack_bytes[line_len:]
    pack_file = b"".join(l[1:] for l in pack_lines[1:])
    def next_size_type(bs: bytes) -> Tuple[str, int, bytes]:
        ty = (bs[0] & 0b_0111_0000) >> 4
        match ty:
            case 1:
                ty = "commit"
            case 2:
                ty = "tree"
            case 3:
                ty = "blob"
            case 4:
                ty = "tag"
            case 6:
                ty = "ofs_delta"
            case 7:
                ty = "ref_delta"
            case _:
                ty = "unknown"
        size = bs[0] & 0b_0000_1111
        i = 1
        off = 4
        while bs[i - 1] & 0b_1000_0000:
            size += (bs[i] & 0b_0111_1111) << off
            off += 7
            i += 1
        return ty, size, bs[i:]
    def next_size(bs: bytes) -> Tuple[int, bytes]:
        size = bs[0] & 0b_0111_1111
        i = 1
        off = 7
        while bs[i - 1] & 0b_1000_0000:
            size += (bs[i] & 0b_0111_1111) << off
            off += 7
            i += 1
        return size, bs[i:]
    # get objs
    pack_file = pack_file[8:]  # strip header and version
    n_objs, *_ = struct.unpack("!I", pack_file[:4])
    pack_file = pack_file[4:]
    for _ in range(n_objs):
        ty, _, pack_file = next_size_type(pack_file)
        match ty:
            case "commit" | "tree" | "blob" | "tag":
                dec = zlib.decompressobj()
                content = dec.decompress(pack_file)
                pack_file = dec.unused_data
                write_object(parent, ty, content)
            case "ref_delta":
                obj = pack_file[:20].hex()
                pack_file = pack_file[20:]
                dec = zlib.decompressobj()
                content = dec.decompress(pack_file)
                pack_file = dec.unused_data
                target_content = b""
                base_ty, base_content = read_object(parent, obj)
                # base and output sizes
                _, content = next_size(content)
                _, content = next_size(content)
                while content:
                    is_copy = content[0] & 0b_1000_0000
                    if is_copy:
                        data_ptr = 1
                        offset = 0
                        size = 0
                        for i in range(0, 4):
                            if content[0] & (1 << i):
                                offset |= content[data_ptr] << (i * 8)
                                data_ptr += 1
                        for i in range(0, 3):
                            if content[0] & (1 << (4 + i)):
                                size |= content[data_ptr] << (i * 8)
                                data_ptr += 1
                        # do something with offset and size
                        content = content[data_ptr:]
                        target_content += base_content[offset : offset + size]
                    else:
                        size = content[0]
                        append = content[1 : size + 1]
                        content = content[size + 1 :]
                        # do something with append
                        target_content += append
                write_object(parent, base_ty, target_content)
            case _:
                raise RuntimeError("Not implemented")
    # render tree
    def render_tree(parent: Path, dir: Path, sha: str):
        dir.mkdir(parents=True, exist_ok=True)
        _, tree = read_object(parent, sha)
        while tree:
            mode, tree = tree.split(b" ", 1)
            name, tree = tree.split(b"\0", 1)
            sha = tree[:20].hex()
            tree = tree[20:]
            match mode:
                case b"40000":
                    render_tree(parent, dir / name.decode(), sha)
                case b"100644":
                    _, content = read_object(parent, sha)
                    Path(dir / name.decode()).write_bytes(content)
                case _:
                    raise RuntimeError("Not implemented")
    _, commit = read_object(parent, refs["HEAD"])
    tree_sha = commit[5 : 40 + 5].decode()
    render_tree(parent, parent, tree_sha)
    
    
    
    
    

def main():
    command = sys.argv[1]
    stage = []
        
        
    if command == "init":
        params = sys.argv[2::]
        init(Path("."))
        print("Initialized git directory")
        

    elif command == "cat-file" and sys.argv[2] == "-p": # -p stands for print
        blob_sha = sys.argv[3]
        
        cat_file(blob_sha) #runs cat-file command function
    
            
    elif command == "hash-object":
        params = sys.argv[2::] #takes in -w (optional) and file name as parameters
        
        hash_object(params) #runs hash-file command function
    
    
    elif command == "ls-tree":
        params = sys.argv[2::]
        
        print(ls_tree(params), end = '')
        
        
    elif command == "write-tree":
        print(write_tree("./"), end = '')
        
        
#TODO    elif command == "add":
        
    elif command == "commit-tree":
        params = sys.argv[2::]
        print(commit_tree(params), end = '')
        
    
    elif command == "clone":
        url = sys.argv[2]
        dir = sys.argv[3]
        
        clone(url, dir)
        

    else:
        raise RuntimeError(f"Unknown command #{command}")
        
if __name__ == "__main__":
    main()

