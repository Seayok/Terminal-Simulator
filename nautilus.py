def ls(current, cmd, data):
    res = 'Error'

    if len(cmd) == 1 or cmd[-1][0] == '-':
        path = current.path
    else:
        path = cmd[-1]
        if path not in data:
            path = current.path + '/' + cmd[-1]
            if path not in data:
                return res

    res = ''
    tmp = sorted(data[path].children.keys())
    if "-a" not in cmd and len(tmp) != 1:
        for key in tmp:
            if key[0] == '.':
                tmp.pop(tmp.index(key))

    if "-l" in cmd:
        for item in tmp:
            child = data[path].children[item]
            res += child.permission + ' ' + child.owner + ' ' + item + '\n'
    else:
        for item in tmp:
            res += item + '\n' 

    return res

def cd(current, path, data):
    if path in current.children:
        if current.children[path].permission[0] == 'd':
            return current.children[path]
        else:
            print('cd: Destination is a file')
            return 'Error'
    elif path in data:
        if data[path].permission[0] == 'd':
            return data[path]
        else:
            print('cd: Destination is a file')
            return 'Error'
    else:
        print("cd: No such file or directory")
        return 'Error'

def goto(current, path):
    if len(path) == 0:
        return current
    name = path[0]
    path.pop(0)
    if name == ".":
        return goto(current, path)
    elif name == "..":
        return goto(current.parent, path)
    if name in current.children:
        child = current.children[name]
        if child.permission[0] == 'd' and child.permission[3] == 'x':
            current = current.children[name]
            return goto(current, path)
        elif child.permission[0] == '-':
            return 'Destination was a file'
        else:
            return 'Permission denied'
    else:
        return  "No such file or directory"


def mkdir(current, owner, cmd, data):
    name = cmd[-1].split("/")[-1]
    if current.path == '/':
        path = current.path + name
    else:
        path = current.path + '/' + name
    new_folder = Node(current, {}, 'drwxr-x', owner, path)
    current.children[name] = new_folder
    return new_folder

def touch(current, owner, cmd, data):
    pass

def pwd(current):
    return current.path


class Node:
    def __init__(self, parent, children, permission, owner, path):
        self.parent = parent
        self.children = children
        self.path = path
        self.owner = owner
        self.permission = permission
        

def main():
    all_files = {}

    user = 'root'
    root = Node( None, {}, 'drwxr-x', 'root', '') 
    root.parent = root
    all_files[""] = root

    current = root

    while True:
        cmd = input(f"{user}:/{current.path}$ ")
        cmd = cmd.split(" ")

        if cmd[0] == "ls":
            print(ls(current, cmd, all_files), end='')

        elif cmd[0] == "exit":
            exit(0)

        elif cmd[0] == "cd":
            path = cmd[1].split('/')
            if path[0] == '':
                result = goto(root, path)
            else:
                result = goto(current, path)
            
            if type(result) != str:
                current = result
            else:
                print(f'cd: {result}')


        elif cmd[0] == "mkdir":
            newdir = mkdir(current, user, cmd, all_files)
            all_files[newdir.path] = newdir
            

if __name__ == '__main__':
    main()
