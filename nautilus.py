class Node:
    def __init__(self, parent, children, permission, owner, path):
        self.parent = parent
        self.children = children
        self.path = path
        self.owner = owner
        self.type = permission[0]
        self.all_permission = permission[1:] 
    
    #get permission
    def permission(self, user):
        if user == 'root':
            return 'rwx'
        elif user == self.owner:
            return self.all_permission[:3]
        else:
            return self.all_permission[3:]

    #trace the ancestor
    def ancestor(self):
        root = self.parent
        while root.path != '':
            root = root.parent
        return root

    #check x bit on ancestor
    def check_ancestor(self, user):
        root = self.parent
        while root.path != '':
            if root.permission(user)[2] == '-':
                return False
            root = root.parent
        return True

    #go to the path
    def cd(self, path):
        if len(path) > 0 and path[0] == '':
            current = self.ancestor()
        else:
            current = self
        while True:
            if len(path) == 0:
                return {"Stop_at": current, "Error_mes": 'Success'}
            name = path[0]
            if name == ".":
                path.pop(0)
                continue
            elif name == "..":
                current = current.parent
                path.pop(0)
                continue
            elif name in current.children:
                child = current.children[name]
                if child.type == 'd':
                    current = current.children[name]
                    path.pop(0)
                    continue
                else:
                    return {"Stop_at": current, "Error_mes": "Destination is a file"}
            else:
                return  {"Stop_at": current, "Error_mes": "No such file or directory"}

    #goto file
    def cf(self, path):
        name = path[-1]
        path.pop(-1)
        destination = self.cd(path)
        if destination["Error_mes"] == "Success" and name in destination['Stop_at'].children:
                current = destination['Stop_at'].children[name]
                return {"Stop_at": current, "Error_mes": "Success"}
        else:
            return destination
    
    #create children of the node
    def create(self, owner, name, flag):
        if flag == "d":
            permission = 'drwxr-x' 
        else:
            permission = '-rw-r--'
        path = self.path + '/' + name
        new = Node (self, {}, permission, owner, path)
        self.children[name] = new


def Error_handling(num, command):
    Error_list = { 1: "Permission denied", 2: "No such file or directory", 3: "Operation not permitted", 4: "Ancestor directory does not exist", 5: 'Is a directory',\
                6: "File exists", 7: "No such file", 8: "Not a directory", 9: "Directory not empty", 10: "Cannot remove pwd", 11: "Destination is a direcotry",\
                12: "Source is a directory", 13: "Invalid syntax", 14: "The user already exist", 15: "Invalid user", 16: "The user does not exist",\
                17: "Invalid mode", 18: "Command not found"}
    if num != 0:
        print(f'{command}: {Error_list[num]}')


def check_permission(current, user, ancestor_x = False, parent_w = False,\
                    dir_x = False, file_r = False, file_w = False, parent_r=False):
    a_x = ancestor_x and not current.check_ancestor(user)
    p_w = parent_w and current.parent.permission(user)[1] == '-'
    d_x = dir_x and current.permission(user)[2] == '-'
    f_r = file_r and current.permission(user)[0] == '-'
    f_w = file_w and current.permission(user)[1] == '-'
    p_r = parent_r and current.parent.permission(user)[0] == '-'
    return not(a_x or p_w or d_x or f_r or f_w or p_r)


def ls(current, user, path, arg):  
    if len(path) == 0 :
        target = current
    else:
        target = current.cf(path)
        if target["Error_mes"] == "Success":
            target = target["Stop_at"]
        else:
            return 2
    
    res = ''
    
    #neu la file neu la directory handle error
    #flag d
    parent = target.parent
    if target.type == '-' or '-d' in arg:
        name_list = [target.path.split("/")[-1]]
        if not check_permission(target, user, ancestor_x=True, parent_r=True):
            return 1

    else:
        parent = target
        name_list = sorted(target.children.keys())
        #root children is root
        if target.path == "":
            name_list.pop(0)
        if not check_permission(target, user, ancestor_x=True, file_r=True):
            return 1

    #flag a
    if "-a" not in arg:
        for item in name_list:
            if len(item) > 0 and item[0] == '.':
                name_list.remove(item)

    #flag l
    for item in name_list:
        child = parent.children[item]
        if item == "":
            item = '/'
        if "-l" in arg:
            res += child.type + child.all_permission + ' ' + child.owner + ' ' + item + '\n'
        else:
            res += item + '\n' 
    print(res, end='')
    return 0


def chmod(current, user, path, format_string, arg):
    target = current.cf(path)

    if target["Error_mes"] == "Success":

        target = target["Stop_at"]
        u = ["-"] * 3
        o = ["-"] * 3
        perm = ["-"] * 3
        format_string = format_string.replace('a', 'uo')
        if 'o' in format_string:
            o = perm
        if 'u' in format_string:
            u = perm
        
        if 'r' in format_string:
            perm[0] = 'r'
        if 'w' in format_string:
            perm[1] = 'w'
        if 'x' in format_string:
            perm[2] = 'x'
        
        full_perm = u + o

        child_list = []
        if "-r" in arg:
            child_list = bfs([target])
        child_list.append(target)

        for child in child_list:
            if not check_permission(child, user, ancestor_x=True):
                Error_handling(1, 'chmod')
            elif user not in ('root', child.owner):
                Error_handling(3, 'chmod')
            else:
                permission = list(child.all_permission)
                if '=' in format_string:
                    if 'u' in format_string:
                        permission[:3] = u
                    if 'o' in format_string:
                        permission[3:] = o
                elif '+' in format_string:
                    for index in range(6):
                        if full_perm[index] != "-":
                            permission[index] = full_perm[index]
                elif '-' in format_string:
                    for index in range(6):
                        if full_perm[index] != "-":
                            permission[index] = '-'
                child.all_permission = ''.join(permission)
                
        return 0
    else:
        return 2


def bfs(visit_list):
    child_list = []
    while True:
        if len(visit_list) == 0:
            return child_list
        destination = visit_list[0]
        visit_list.pop(0)
        for child in destination.children:
            child_list.append(destination.children[child])
            visit_list.append(destination.children[child])


def chown(current, user, path, arg):
    target = current.cf(path)
    if target['Error_mes'] == "Success":
        target = target["Stop_at"]
        target.owner = user
        if target.path == '':
            target.children.pop('')
        if '-r' in arg:
            child_list = bfs([target])
            for child in child_list:
                child.owner = user
        return 0
    else:
        return 2


def make(current, user, path, command, arg=[]):
    name = path[-1]
    path.pop(-1)
    destination = current.cd(path)
    if destination["Error_mes"] == 'Success':
        destination = destination["Stop_at"]
        if name in destination.children and command != 'touch':
            return 6
        else:
            #create tmp child to check permission
            tmp_child = Node(destination, {}, '-'*7, '', '')
            if not check_permission(tmp_child, user, ancestor_x=True, parent_w=True):
                return 1
            else:
                flag = 'f'
                if command == "mkdir":
                    flag = 'd'
                destination.create(user,name, flag)
                return 0 

    else:        
        if '-p' in arg:
            if not check_permission(destination["Stop_at"], user, ancestor_x=True, parent_w=True):
                return 1
            destination = destination["Stop_at"]
            path.append(name)
            while len(path) > 0:
                subname = path[0]
                destination.create(user, subname, "d")
                destination = destination.children[subname]
                path.pop(0)
            return 0
        else:
            return 4


def rm_path(current, user, path):
    name = path[-1]
    target = current.cf(path)

    if target["Error_mes"] == "Success":
        target = target["Stop_at"]

        if not check_permission(target, user, ancestor_x=True, file_w=True, parent_w=True):
            return 1
        elif target.type == 'd':
            return 5
        else:
            target.parent.children.pop(name)
            return 0

    else:
        return 7
    
    
def rmdir(current, user, path):
    name = path[-1]
    target = current.cd(path)

    if target["Error_mes"] == "Success":
        target = target["Stop_at"]

        if not check_permission(target, user, ancestor_x=True, parent_w=True):
            return 1
        elif target.type == '-':
            return 8
        elif len(target.children) > 1 or (target.path != '' and len(target.children) > 0):
            return 9
        elif target == current:
            return 10
        else:
            target.parent.children.pop(name)
            return 0

    else:
        return 7


def mv_cp(current, user, path, path_2, command):
    terminate = False
    file_name = path[-1]
    path.pop(-1)
    src = current.cd(path)
    name = path_2[-1]
    path_2.pop(-1)
    dst = current.cd(path_2)

    if src["Error_mes"] == "Success" and dst["Error_mes"] == "Success":
        src = src['Stop_at']
        dst = dst['Stop_at']

        if file_name not in src.children:
            return 7

        src = src.children[file_name]
        test_child = Node(dst, {}, "-"*7, '', '')

        if command == "mv":
            check = check_permission(src, user, ancestor_x=True, parent_w=True)
            check_2 = check_permission(test_child, user, ancestor_x=True, parent_w=True)
            terminate = True
        else:
            check = check_permission(src, user, ancestor_x=True, file_r=True)
            check_2 = check_permission(test_child, user, ancestor_x=True, parent_w=True)

        if not(check and check_2):
            return 1
        elif name in dst.children:
            if dst.children[name].type == 'd':
                return 11
            else:
                return 6
        elif src.type == 'd':
            return 12
        else:
            child = Node(dst, {}, src.type + src.all_permission, src.owner, src.path + '/' + name)
            dst.children[name] = child
            if terminate:
                src.parent.children.pop(src.path.split('/')[-1])
            return 0

    else:
        return 7
    

def check_format_string(remain):
    if len(remain) < 1:
        return False
    index = 0
    while index  < len(remain) and remain[index] in 'uoa':
        index += 1
    if (index == 0 and remain[0] not in '-+=') or index == len(remain):
        return False
    elif remain[index] not in '-+=':
        return False
    else:
        if len(remain) - index > 1:
            for char in remain[index + 1:]:
                if char not in 'rwx':
                    return False
    return True


def check_double_path(remain):
    res = False
    path_1 = ''
    path_2 = ''
    if remain.count(' ') > 1:
        if remain.count("\"") == 2:
            index = remain.index("\"", 1)
            if remain[0] == "\"":
                path_1 = remain[:index + 1]
                space = remain[index + 1]
                path_2 = remain[index + 2:]
            elif remain[-1] == "\"":
                path_1 = remain[:index - 1]
                space = remain[index - 1]
                path_2 = remain[index:]
            res = check_path(path_1) and check_path(path_2) and space == ' '
        elif remain.count("\"") == 4 and remain[0] == "\"" and remain [-1] == "\"":
                path = remain.split('\"')
                path_1, space, path_2 = path[1:4]
                path_1_check = f'\"{path_1} \"'
                path_2_check = f'\"{path_2} \"'
                res = check_path(path_1_check) and check_path(path_2_check) and space == ' '
    elif remain.count(' ') == 1:
        path_1, path_2 = remain.split(' ')
        res = check_path(path_1) and check_path(path_2)
    return (res, path_1, path_2)


def check_path(path):
    valid_syntax = [" ", ".", "..", "-", "_", "\"", "/"]
    path_check = path

    for syntax in valid_syntax:
        path_check = path_check.replace(syntax, "a")

    if not path_check.isalnum():
        return False
    elif ("\"" in path or " " in path) and not (path.count("\"") == 2 and path[-1] == "\"" and path[0] =="\"" and " " in path):
        return False
    else:
        return True


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
    

def check_user(remain):
    return check_path(remain) and "/" not in remain


def check_and_split_syntax(cmd):
    command = cmd.split(' ', 1)[0]
    remain = cmd.replace(command, '')
    if remain != '':
        remain = remain[1:]
    #initialize
    arg_list = []
    valid_arg = True
    valid_path = True
    valid_format = True
    valid = True
    valid_user = True
    path_list = [[]]
    format_string = ''
    user = ''


    if command in ('exit', 'pwd') and remain != '':
        valid = False

    elif command in ('touch', 'cd', 'rm', 'rmdir', 'mkdir', 'ls'):
        if command == "ls": 
            valid_arg, remain = check_arg(remain, ["-a", "-d", "-l"], arg_list)
        elif command in 'mkdir': 
            valid_arg, remain = check_arg(remain, ["-p"], arg_list)
        #su va ls co the khong nhan argument
        if valid_arg == True and not (command == 'ls' and remain == ''):
            valid_path = check_path(remain)
            if valid_path:
                path = remain.strip("\"").split("/")
                path_list = [path] 

    elif command in ('adduser', 'deluser', 'su'):
        if not (command == "su" and remain == ''):
            valid_user = check_user(remain)
            user = remain.strip("\"")

    elif command in ('cp', 'mv'):
        valid_path, path_1, path_2 = check_double_path(remain)
        path_1 = path_1.strip("\"").split("/")
        path_2 = path_2.strip("\"").split("/")
        path_list = [path_1, path_2]

    elif command in ('chmod', 'chown'):
        valid_arg, remain = check_arg(remain, ["-r"], arg_list)
        if valid_arg:
            if command == "chmod":
                format_string = remain.split(' ', 1)[0]
                valid_format = check_format_string(format_string)
                path = remain.replace(format_string, '')
                if path != '':
                    path = path[1:]
                valid_path = check_path(path)
            else:
                valid_path, path_1, path = check_double_path(remain)
                if "/" not in path_1:
                    user = path_1.strip("\"")
            path = path.strip("\"").split("/")
            path_list = [path]

    valid = valid and valid_arg and valid_user and valid_path
    return (valid, command, path_list, arg_list, user, format_string, valid_format)

            
def main():
    user_list = ['root']
    active_user = 'root'

    root = Node( None, {}, 'drwxr-x', 'root', '') 
    root.parent = root
    root.children[''] = root
    current = root

    while True:
        display = f"{current.path}$ "
        if current == root:
            display = f"/{current.path}$ "
        
        cmd = input(active_user + ":" + display).strip()
        if cmd == '':
            continue

        valid, command, path_list, arg_list, user, format_string, valid_format = check_and_split_syntax(cmd)

        if not valid:
            Error_handling(13, command)
            continue
        else:
            path = path_list[0]

        if command == "ls":
            Error_handling(ls(current, active_user, path, arg_list), command)
        elif command == "exit":
            print(f"bye, {active_user}")
            exit(0)
        elif command == "cd":
            result = current.cd(path)
            if result["Error_mes"] == "Success":
                current = result["Stop_at"]
            else:
                print(f"cd: {result['Error_mes']}")
        elif command in ("touch", "mkdir"):
            Error_handling(make(current, active_user, path, command, arg_list), command)        
        elif command == "pwd":
            if current == root:
                print('/')
            else:
                print(current.path)
        elif command == 'rmdir':
            Error_handling(rmdir(current, active_user, path), command)
        elif command == 'rm':
            Error_handling(rm_path(current, active_user, path), command)
        elif command == 'adduser':
            if active_user == 'root':
                if user in user_list:
                    Error_handling(14 ,command)
                else:
                    user_list.append(user)
            else:
                Error_handling(3, command)
        elif command == 'su':
            if user == '':
                active_user = 'root'
            else:
                if user in user_list:
                    active_user = user
                else:
                    Error_handling(15, command)
        elif command == "deluser":
            if active_user == 'root':
                if user == 'root':
                    print('''WARNING: You are just about to delete the root account
Usually this is never required as it may render the whole system unusable
If you really want this, call deluser with parameter --force
(but this `deluser` does not allow `--force`, haha)
Stopping now without having performed any action''')
                elif user not in user_list:
                    Error_handling(16, command)
                else:
                    user_list.remove(user)
            else:
                Error_handling(3, command)
        elif command in ('mv', 'cp'):
            path_2 = path_list[1]
            mv_cp(current, active_user, path, path_2, command)
        elif command == 'chmod':
            if not valid_format:
                Error_handling(17, command)
            else:
                chmod(current, active_user, path, format_string, arg_list)
        elif command == 'chown':
            if active_user != 'root':
                Error_handling(3, command)
            elif user not in user_list:
                Error_handling(15 ,command)
            else:
                chown(current, user, path, arg_list)
        elif command == '':
            pass
        else:
            Error_handling(18, command)


if __name__ == '__main__':
    main()
#permission use bitwise
#recursive error handling
