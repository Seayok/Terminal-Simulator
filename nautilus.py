def ls(current, cmd):
    res = 'Error'

    if len(cmd) == 1 or cmd[-1][0] == '-':
        destination = current
    else:
        path = cmd[-1]
        path = path.split('/')
        destination = get_path(current, path)
    res = ''
    tmp = sorted(destination.children.keys())
    if "-a" not in cmd and len(tmp) != 1:
        index = 0
        bound = len(tmp)
        while index < bound:
            key = tmp[index]
            if key[0] == '.':
                tmp.pop(index)
                bound -= 1
            else:
                index += 1

    if "-l" in cmd:
        for item in tmp:
            child = destination.children[item]
            res += child.permission + ' ' + child.owner + ' ' + item + '\n'
    else:
        for item in tmp:
            res += item + '\n' 

    return res


def ancestor(current):
    while current.path != '':
        current = goto(current,['..'])
    return current


def get_path(current, path):
    if len(path) > 0 and path[0] == '':
        current = ancestor(current)
    return goto(current, path)


    
def goto(current, path):
    if current.permission[3] != 'x':
        return 'Permission denied'
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
        if child.permission[0] == 'd':
            current = current.children[name]
            return goto(current, path)
        else:
            return [current, name, 'Destination was a file']
    else:
        return  [current, name, "No such file or directory"]


def mkdir(current, owner, cmd):
    res = make(current, owner, cmd)
    if type(res) == str:
        print(f'{cmd[0]}: {res}')
    else:
        create(res[0], res[1], res[2])

def create(current, owner, name):
    path = current.path + '/' + name
    new_folder = Node (current, {}, 'drwxr-x', owner, path)
    current.children[name] = new_folder


def make(current, owner, cmd):
    path = cmd[-1].split('/')
    name = path[-1]
    path.pop(-1)
    cmd[-1] = '/'.join(path)
    destination = get_path(current, path) 
    #doi ten lai
    daddy = ancestor(current) 
    #rut gon cho nay
    if type(destination) == list:        
        if cmd[1] == '-p' and destination[-1] == 'No such file or directory':
            subname = destination[1]
            destination = destination[0]
            create(destination, owner, subname)
            return make(destination, owner, cmd)
        else:
            return"Ancestor directory does not exist"
    elif destination == 'Permission denied' or daddy == 'Permission denied' or destination.permission[2] == '-':
        return "Permssion denied"
    elif name in destination.children:
        return "File exists"
    else:
        return [destination, owner, name]


def touch(current, owner, cmd):
    res = make(current, owner, cmd)
    if type(res) == str:
        if res == 'File exists':
            pass
        else:
            print(f'{cmd[0]}: {res}')
    else:
        name = cmd[-1].split('/')[-1]
        path = current.path + '/' + name 
        new_file = Node(current, {}, '-rw-r--', owner, path)
        current.children[name] = new_file

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
    user = 'root'
    root = Node( None, {}, 'drwxr-x', 'root', '') 
    root.parent = root
    current = root

    while True:
        if current == root:
            cmd = input(f"{user}:/{current.path}$ ")
        else:
            cmd = input(f"{user}:{current.path}$ ")
        cmd = cmd.split(" ")

        if cmd[0] == "ls":
            print(ls(current, cmd), end='')

        elif cmd[0] == "exit":
            exit(0)

        elif cmd[0] == "cd":
            path = cmd[1].split('/')
            result = get_path(current, path)
            if type(result) != str:
                current = result
            else:
                print(f'cd: {result}')
        elif cmd[0] == "touch":
            touch(current, user, cmd)
        elif cmd[0] == "mkdir":
            mkdir(current, user, cmd)            

if __name__ == '__main__':
    main()
