class Node:
    def __init__(self, parent, children, permission, owner, path):
        self.parent = parent
        self.children = children
        self.path = path
        self.owner = owner
        self.type = permission[0]
        self.owner_permission = permission[1:4]
        self.other_permission = permission[4:]
    
    #get permission
    def permission(self, user):
        if user in (self.owner, 'root'):
            return self.owner_permission
        else:
            return self.other_permssion

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
                    return {"Stop_at": current, "Error_mes": "Destination was a file"}
            else:
                return  {"Stop_at": current, "Error_mes": "No such file or directory"}
    
    #create children of the node
    def create(self, owner, name, flag):
        if flag == "d":
            permission = 'drwxr-x' 
        else:
            permission = '-rw-r--'
        path = self.path + '/' + name
        new = Node (self, {}, permission, owner, path)
        self.children[name] = new


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
        name = path[-1]
        path.pop(-1)
        destination = current.cd(path)
        if destination["Error_mes"] != "Success" or name not in destination["Stop_at"].children:
            return "ls: No such file or directory\n"
        else:
            target = destination["Stop_at"].children[name]
    
    #neu la file neu la directory handle error
    #flag d
    parent = target.parent
    if target.type == '-' or '-d' in arg:
        name_list = [target.path.split("/")[-1]]
        if not check_permission(target, user, ancestor_x=True, parent_r=True):
            return "ls: Permission denied\n"
    else:
        parent = target
        name_list = sorted(target.children.keys())
        #root children is root
        if target.path == "":
            name_list.pop(0)
        if not check_permission(target, user, ancestor_x=True, file_r=True):
            return "ls: Permission denied\n"
    
    res = ''
#flag a
    if "-a" not in arg:
        del_arr = []
        for item in name_list:
            if len(item) > 0 and item[0] == '.':
                del_arr.append(item)
        for i in del_arr:
            name_list.pop(name_list.index(i))
#flag l
    if "-l" in arg:
        for item in name_list:
            child = parent.children[item]
            if item == "":
                item = '/'
            res += child.type + child.owner_permission + child.other_permission + ' ' + child.owner + ' ' + item + '\n'
    else:
        for item in name_list:
            if item == "":
                item = '/'
            res += item + '\n' 
    return res


def make(current, user, path, command, arg=[]):
    name = path[-1]
    path.pop(-1)
    destination = current.cd(path)
    if destination["Error_mes"] == 'Success':
        destination = destination["Stop_at"]
        if name in destination.children:
            if command == 'touch':
                pass
            else:
                return f"{command}: File exists"
        else:
            #create tmp child to check permission
            tmp_child = Node(destination, {}, '-'*7, '', '')
            if not check_permission(tmp_child, user, ancestor_x=True, parent_w=True):
                return "mkdir: Permssion denied"
            else:
                flag = 'f'
                if command == "mkdir":
                    flag = 'd'
                destination.create(user,name, flag)
                return "Success"    

    else:        
        if '-p' in arg:
            if not check_permission(current, user, ancestor_x=True, parent_w=True):
                return "mkdir: Permission denied"
            destination = destination["Stop_at"]
            path.append(name)
            while len(path) > 0:
                subname = path[0]
                destination.create(user, subname, "d")
                destination = destination.children[subname]
                path.pop(0)
            return "Success"
        else:
            return f"{command}: Ancestor directory does not exist"


def rm_path(current, user, path):
    name = path[-1]
    target = current.cd(path)
    if target["Error_mes"] == "Success":
        target = target["Stop_at"]
        if not check_permission(current, user, ancestor_x=True, file_w=True, parent_w=True):
            print('rm: Permission denied')
        elif target.type == 'd':
            print('rm: Is a directory')
        else:
            target.parent.pop(name)
    else:
        print("rm: No such file")
    
    
def rmdir(current, user, path):
    name = path[-1]
    target = current.cd(path)
    if target["Error_mes"] == "Success":
        target = target["Stop_at"]
        if not check_permission(current, user, ancestor_x=True, parent_w=True):
            print('rm: Permission denied')
        elif target.type == '-':
            print('rmdir: Not a directory')
        elif len(target.children) > 1 or (target.path != '' and len(target.children) > 0):
            print('rmdir: Directory not empty')
        elif target == current:
            print('rmdir: Cannot remove pwd')
        else:
            target.parent.pop(name)
    else:
        print("rm: No such file") 


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
            print(f"{command}: No such file")
            return
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
            print(f"{command}: Permission denied")
        elif name in dst.children:
            if dst.children[name].type == 'd':
                print(f"{command}: Destination is a directory")
            else:
                print(f"{command}: File exists")
        elif src.type == 'd':
            print(f"{command}: Source is a directory")
        else:
            child = Node(dst, {}, src.type + src.owner_permission + src.other_permission, src.owner, src.path + '/' + name)
            dst.children[name] = child
            if terminate:
                src.parent.children.pop(src.path.split('/')[-1])
    else:
        print(f"{command}: No such file")
    


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
        elif " " in path:
            return (False, [" "])
        else:
            return (False, [])
    elif " " in path:
        return (False, [" "])
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
        check, path = check_path(remain)
        if check == False and path == [" "]:
            check = True
            remain_1, remain_2 = remain.split(" ", 1)
            check, path = check_path(remain_1)
            check_2, path_2 = check_path(remain_2)
            check = check and check_2
            path_list = [path, path_2]
        else:
            check = False
    elif command in ('chmod', 'chown'):
        check, remain = check_arg(remain, ["-r"], arg_list)
        if check == True:
            if command == "chmod":
                target = remain[0]
                todo = remain[1]
                
            else:
                check, path = check_path(remain)

            if check == False and path == [" "]:
                check = True
                remain_1, remain_2 = remain.split(" ", 1)
                check, user = check_path(remain_1)
                check_2, path = check_path(remain_2)
                check = check and check_2 and len(user) == 1
                path_list = [path, user]
            else:
                check = False
    return (check,  command, path_list, arg_list)

            
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
            result = current.cd(path)
            if result["Error_mes"] == "Success":
                current = result["Stop_at"]
            else:
                print(f'cd: {result["Error_mes"]}')
        elif command in ("touch", "mkdir"):
            res = make(current, active_user, path, command, arg_list)
            if res != "Success":
                print(res)            
        elif command == "pwd":
            print(current.path)
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
                print('adduser: Operation not permitted')
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
                print('deluser: Operation not permitted') 
        elif command in ('mv', 'cp'):
            path_2 = path_list[1]
            mv_cp(current, active_user, path, path_2, command)
        elif command == '':
            pass
        else:
            print(f"{command}: Command not found")


if __name__ == '__main__':
    main()
# cp "a a/asdf/asdf" "b b/asdf/asdf"