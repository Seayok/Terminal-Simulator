def ls(current, user, path, arg):
    if len(path) == 0 :
        target = current
    else:
        name = path[-1]
        path.pop(-1)
        destination = get_path(current, path)
        if destination[2] == 'Permission denied':
            return "ls: Permission denied\n"
        elif destination[2] != "Success":
            return "ls: No such file or directory\n"
        else:
            destination = destination[0]
            target = destination.children[name]
    daddy = ancestor(target)
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
    if destination.permission[1] == '-' or daddy[2] == "Permission denied":
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


def ancestor(current):
        while current.path != '':
            current = goto(current, ['..'])
            if current[2] == 'Permission denied':
                return current
            current = current[0]
        current = [current, '',"Success"]
        return current


def cp(current, path, path_2):
    pass

def mv(current, path, path_2):
    pass

def rmdir(current, user, path):
    name = path[-1]
    destination = get_path(current, path)
#directory not found????
    if destination[2] == "Permission denied":
        print('rmdir: Permssion denied')
    elif destination[2] == "Success":
        destination = destination[0]
        if len(destination.children) > 1 or (destination.path != '' and len(destination.children) > 0):
            print("rmdir: Directory not empty")
        elif destination.parent.permission[2] == '-':
            print('rmdir: Permission denied')
        elif destination == current:
            print('rmdir: Cannot remove pwd')
        else:
            destination.parent.children.pop(name)
    else:
        print('rmdir: Not a directory')

def rm_path(current, user, path):
    name = path[-1]
    path.pop(-1)
    destination = get_path(current, path)
    #directory not found????
    if destination[2] == "Permission denied":
        print('rm: Permission denied')
    elif destination[2] == "Success":
        destination = destination[0]
        if destination.parent.permission[2] == '-' or destination.permission[2] == '-':
            print('rm: Permission denied')
        elif name in destination.children:
            if destination.children[name].permission[0] == 'd':
                print('rm: Is a directory')
            else: 
                destination.parent.children.pop(name)        
    else:
        print('rm: No such file')


def get_path(current, path):
    if len(path) > 0 and path[0] == '':
        while current.path != '':
            result = ancestor(current)
            if result[2] == 'Permission denied':
                result = ancestor(current[0].parent)
            current = result[0]
    return goto(current, path)


def goto(current, path):
    if len(path) == 0:
        return [current, path, 'Success'] 
    name = path[0]
    path.pop(0)
    if current.permission[3] != 'x':
        return [current, name, 'Permission denied']
    elif name == ".":
        return goto(current, path)
    elif name == "..":
        return goto(current.parent, path)
    elif name in current.children:
        child = current.children[name]
        if child.permission[0] == 'd':
            current = current.children[name]
            return goto(current, path)
        else:
            return [current, name, 'Destination was a file']
    else:
        return  [current, name, "No such file or directory"]

def create(current, owner, name, command):
    if command == "mkdir":
        permission = 'drwxr-x' 
    else:
        permission = '-rw-r--'
    path = current.path + '/' + name
    new = Node (current, {}, permission, owner, path)
    current.children[name] = new

#in trong function?
def make(current, owner, path, command, arg=[]):
    name = path[-1]
    path.pop(-1)
    destination = get_path(current, path) 
    #doi ten lai
    daddy = ancestor(current) 
    if destination[2] == 'Permission denied' or daddy[2] == 'Permission denied':
        return f"{command}: Permssion denied"
    elif destination[2] == 'Success':
            destination = destination[0]
            if destination.permission[2] != 'w':
                return f"{command}: Permission denied"
            elif name in destination.children:
                return f"{command}: File exists"
    else:        
        if '-p' in arg:
            path.append('tmp')
            subname = destination[1]
            destination = destination[0]
            if destination.permission[2] == '-':
                return f"{command}: Permission denied" 
            while len(path) > 0:
                create(destination, owner, subname, command)
                destination = destination.children[subname]
                subname = path[0]
                path.pop(0)
        else:
            return f"{command}: Ancestor directory does not exist"
    create(destination, owner, name, command)
    return "Success"


def check_path(path):
    valid_syntax = [" ", ".", "..", "-", "_", "\"", "/"]
    path_check = path
    for syntax in valid_syntax:
        path_check = path_check.replace(syntax, "a")
    if not path_check.isalnum():
        return (False, [])
    elif "\"" in path:
        if path.count("\"") == 2 and path[-1] == "\"" and path[0] =="\"" and " " in path:
            res_path = path[1:-1]
        else:
            return (False, [])
    elif " " in path:
        return (False, [])
    else:
        res_path = path
    return (True, res_path.split("/"))


def check_arg(remain, arguments, arg_list):
    while len(remain) > 2 and remain[2] == " " and remain[0] == "-":
        arg = remain[:2]
        if arg in arguments and arg not in arg_list:
            arg_list.append(arg)
            remain = remain[3:]
        else:
            return (False, '')
#if ls
    if "-l" in arguments and remain in arguments and not remain in arg_list:
        arg_list.append(remain)
        remain = ''
    return (True, remain)
    
            
def check_and_split_syntax(cmd):
    command = cmd.split(' ', 1)[0]
    remain = cmd.replace(command, '')
    if remain != '':
        remain = remain[1:]
    path_2 = []
    path = []
    arg_list = []
    check = True
    path_list = [[]]
    if command in ('exit', 'pwd') and remain != '':
        check = False
    elif command in ('touch', 'cd', 'rm', 'rmdir', 'mkdir', 'ls'):
        if command == "ls": 
            check, remain = check_arg(remain, ["-a", "-d", "-l"], arg_list)
        elif command in 'mkdir': 
            check, remain = check_arg(remain, ["-p"], arg_list)
        #su va ls co the khong nhan argument
        if check == True and not (command == 'ls' and remain == ''):
            check, path = check_path(remain)
            path_list = [path] 
    elif command in ('adduser', 'deluser', 'su'):
        if not (command == "su" and remain == ''):
            check, path = check_path(remain)
        if len(path) > 1:
            check = False
        else:
            path_list = [path]
    elif command in ('cp', 'mv'):
        path = check_path(remain)
        path_2 = check_path(remain)
    return (check,  command, path_list, arg_list)


class Node:
    def __init__(self, parent, children, permission, owner, path):
        self.parent = parent
        self.children = children
        self.path = path
        self.owner = owner
        self.permission = permission


def main():
    user_list = []
    active_user = 'root'
    root = Node( None, {}, 'drwxr-x', 'root', '') 
    root.parent = root
    root.children[''] = root
    current = root
    user_list.append(active_user)

    while True:
        display = f"{current.path}$ "
        if current == root:
            display = f"/{current.path}$ "
        cmd = input(active_user + ":" + display).strip()
        if cmd == '':
            continue

        valid, command, path_list, arg_list = check_and_split_syntax(cmd)

        if not valid:
            print(f'{command}: Invalid syntax')
            continue
        else:
            path = path_list[0]

        if command == "ls":
            print(ls(current, active_user, path, arg_list), end='')
        elif command == "exit":
            print(f"bye, {active_user}")
            exit(0)
        elif command == "cd":
            result = get_path(current, path)
            if result[2] == "Success":
                current = result[0]
            else:
                print(f'cd: {result[2]}')
        elif command in ("touch", "mkdir"):
            res = make(current, active_user, path, command, arg_list)
            if res != "Success":
                print(res)            
        elif command == "pwd":
            print(display[:-2])
        elif command == 'rmdir':
            rmdir(current, active_user, path)
        elif command == 'rm':
            rm_path(current, active_user, path)
        elif command == 'adduser':
            if active_user == 'root':
                if path[0] in user_list:
                    print('adduser: The user already exist')
                else:
                    user_list.append(path[0])
            else:
                print('adduser: Permission denied')
        elif command == 'su':
            if len(path) == 0:
                active_user = 'root'
            else:
                user = path[0]
                if user in user_list:
                    active_user = user
                else:
                    print('su: Invalid user')
        elif command == "deluser":
            if active_user == 'root':
                if path[0] == 'root':
                    print('''WARNING: You are just about to delete the root account
Usually this is never required as it may render the whole system unusable
If you really want this, call deluser with parameter --force
(but this `deluser` does not allow `--force`, haha)
Stopping now without having performed any action''')
                elif path[0] not in user_list:
                    print('deluser: The user does not exist')
                else:
                    user_list.pop(path[0])
            else:
                print('deluser: Permission denied') 
        elif command == '':
            pass
        else:
            print(f"{command}: Command not found")


if __name__ == '__main__':
    main()

#white space gan cuoi
#ls -l -l -a