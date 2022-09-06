def ls(current, user, path, arg):
    if len(path) == 0 :
        target = current
    else:
        name = path[-1]
        path.pop(-1)
        destination = get_path(current, path)
        if type(destination) == list or name not in destination.children:
            return "ls: No such file or directory\n"
        elif type(destination) == str:
            return "ls: Permission denied\n"
        else:
            target = destination.children[name]
    #neu la file neu la directory handle error
    #flag d
    if target.permission[0] == '-' or '-d' in arg:
        destination = target.parent
        child_dict = destination.children
        tmp = [list(child_dict.keys())[list(child_dict.values()).index(target)]]
    else:
        destination = target
        tmp = sorted(destination.children.keys())
        #root children is root
        if destination.path == "":
            tmp.pop(0)

    if destination.permission[1] == '-':
        return "ls: Permission denied\n"
    res = ''
#flag a
    if "-a" not in arg:
        index = 0
        bound = len(tmp)
        while index < bound:
            key = tmp[index]
            if len(key) > 0 and key[0] == '.':
                tmp.pop(index)
                bound -= 1
            else:
                index += 1
#flag l
    if "-l" in arg:
        for item in tmp:
            child = destination.children[item]
            if item == "":
                item = '/'
            res += child.permission + ' ' + child.owner + ' ' + item + '\n'
    else:
        for item in tmp:
            if item == "":
                item = '/'
            res += item + '\n' 
    return res


def rmdir(current, user, path):
    name = path[-1]
    destination = get_path(current, path)
#directory not found????
    if type(destination) == list:
        print('rmdir: Not a directory')
    elif type(destination) == str or destination.parent.permission[2] == '-':
        print('rmdir: Permssion denied')
    elif len(destination.children) > 1 or (destination.path != '' and len(destination.children) > 0):
        print("rmdir: Directory not empty")
    elif destination == current:
        print('rmdir: Cannot remove pwd')
    else:
        destination.parent.children.pop(name)


def rm_path(current, user, path):
    name = path[-1]
    path.pop(-1)
    destination = get_path(current, path)
    #directory not found????
    if type(destination) == list:
        print('rm: No such file')
    elif type(destination) == str or destination.parent.permission[2] == '-' or destination.permission[2] == '-':
        print('rm: Permission denied')
    elif name in destination.children:
        if destination.children[name].permission[0] == 'd':
            print('rm: Is a directory')
        else: 
            destination.parent.children.pop(name)        
    else:
        print('rm: No such file')
    

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


def mkdir(current, owner, path, arg):
    res = prepare(current, owner, path, arg)
    if type(res) == str:
        print(f'mkdir: {res}')
    else:
        create(res[0], res[1], res[2])


def create(current, owner, name):
    path = current.path + '/' + name
    new_folder = Node (current, {}, 'drwxr-x', owner, path)
    current.children[name] = new_folder


def prepare(current, owner, path, arg=[]):
    name = path[-1]
    path.pop(-1)
    destination = get_path(current, path) 
    #doi ten lai
    daddy = ancestor(current) 
    #rut gon cho nay
    if type(destination) == list:        
        if '-p' in arg:
            path.append('tmp')
            subname = destination[1]
            destination = destination[0]
            if destination.permission[2] == '-':
                return "Permission denied" 
            while len(path) > 0:
                create(destination, owner, subname)
                destination = destination.children[subname]
                subname = path[0]
                path.pop(0)
        else:
            return"Ancestor directory does not exist"
    if destination == 'Permission denied' or daddy == 'Permission denied' or destination.permission[2] == '-':
        return "Permssion denied"
    if name in destination.children:
        return "File exists"
    return [destination, owner, name]


def check_path(path):
    valid_syntax = [" ", ".", "..", "-", "_", "\"", "/"]
    path_check = path
    for syntax in valid_syntax:
        path_check = path_check.replace(syntax, "a")
    if not path_check.isalnum():
        return False
    elif "\"" in path:
        if path.count("\"") == 2 and path[-1] == "\"" and path[0] =="\"" and " " in path:
            res_path = path[1:-1]
        else:
            return False
    elif " " in path:
        return False
    else:
        res_path = path
    return res_path.split("/")


def check_arg(remain, arguments, arg_list):
    while len(remain) > 2 and remain[2] == " " and remain[0] == "-":
        arg = remain[:2]
        if arg in arguments and arg not in arg_list:
            arg_list.append(arg)
            remain = remain[3:]
        else:
            return False
#if ls
    if "-l" in arguments and remain in arguments and not remain in arg_list:
        arg_list.append(remain)
        remain = ''
    return remain
    
            
def check_syntax(cmd):
    command = cmd.split(' ', 1)[0]
    remain = cmd.replace(command, '')
    if remain != '':
        remain = remain[1:]
    path_2 = []
    path = []
    arg_list = []
    path_list = [path]
    if command in ('exit', 'pwd') and remain != '':
        remain = False
    elif command in ('touch', 'cd', 'rm', 'rmdir', 'mkdir', 'ls'):
        if command == "ls": 
            remain = check_arg(remain, ["-a", "-d", "-l"], arg_list)
        elif command in 'mkdir': 
            remain = check_arg(remain, ["-p"], arg_list)
        #su va ls co the khong nhan argument
        if type(remain) == str and not (command == 'ls' and remain == ''):
            path = check_path(remain)
            path_list = [path] 
    elif command in ('adduser', 'deluser', 'su'):
        path = check_path(remain)
        if len(path) > 1:
            remain = False
        else:
            path_list = [path]
    elif command in ('cp', 'mv', ''):
        path = check_path(remain)
        path_2 = check_path(remain)
    if path == False or path_2 == False or remain == False:
        return command
    else:
        return {"command": command,"path" : path_list, "arg" : arg_list}


def touch(current, owner, path):
    res = prepare(current, owner, path)
    if type(res) == str:
        if res == 'File exists':
            pass
        else:
            print(f'touch: {res}')
    else:
        current = res[0]
        name = res[2]
        path = current.path + '/' + name 
        new_file = Node(current, "file", '-rw-r--', owner, path)
        current.children[name] = new_file


class Node:
    def __init__(self, parent, children, permission, owner, path):
        self.parent = parent
        self.children = children
        self.path = path
        self.owner = owner
        self.permission = permission
        

def main():
    user_list = []
    user = 'root'
    root = Node( None, {}, 'drwxr-x', 'root', '') 
    root.parent = root
    root.children[''] = root
    current = root
    user_list.append(current)

    while True:
        display = f"{current.path}$ "
        if current == root:
            display = f"/{current.path}$ "
        cmd = input(user + ":" + display).strip()
        if cmd == '':
            continue
        res = check_syntax(cmd)
        if type(res) == str:
            print(f'{res}: Invalid syntax')
            continue
        else:
            command = res["command"]
            path = res["path"][0]
            arg = res["arg"]
        if command == "ls":
            print(ls(current, user, path, arg), end='')
        elif command == "exit":
            exit(0)
        elif command == "cd":
            result = get_path(current, path)
            if type(result) != list:
                current = result
            else:
                print(f'cd: {result[2]}')
        elif command == "touch":
            touch(current, user, path)
        elif command == "mkdir":
            mkdir(current, user, path, arg)            
        elif command == "pwd":
            print(display[:-2])
        elif command == 'rmdir':
            rmdir(current, user, path)
        elif command == 'rm':
            rm_path(current, user, path)
        elif command == 'adduser':
            if user == 'root':
                if path[0] in user_list:
                    print('adduser: The user already exist')
                else:
                    user_list.append(path[0])
            else:
                print('adduser: Permission denied')
        elif command == 'su':
            pass
        elif command == "deluser":
            pass
        elif command == '':
            pass
        else:
            print(f"{command}: Command not found")


if __name__ == '__main__':
    main()

#white space gan cuoi
#ls -l -l -a