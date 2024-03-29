# Some of the commands will share the same function
# Due to their similarity in error handling and functionality

# Node is an object represent both files and folders


class Node:
    def __init__(self, parent, children, type_permission,
                 owner, path, ancestor):
        self.parent = parent
        self.children = children
        self.path = path
        self.ancestor = ancestor
        self.owner = owner
        self.type = type_permission[0]
        self.all_permission = type_permission[1:]

    # Get permission for any user
    def permission(self, user):
        if user == 'root':  # root is a super user
            return 'rwx'
        elif user == self.owner:  # return permission of owner
            return self.all_permission[:3]
        else:  # return permission of other
            return self.all_permission[3:]

    # Check execute bit on ancestor
    def check_x_ancestor(self, user):
        ancestor = self.parent
        not_root = True

        while not_root:  # If the folder is not root yet

            if ancestor.permission(user)[2] == '-':
                return False

            if ancestor.path == '/':
                not_root = False

            ancestor = ancestor.parent  # Go upper the tree
        return True

    # Go to folder with a given path
    # This function will return the folder it stop and error mes.
    # This function will adjust the path array to the file that cause error
    # Example cd a/b/c.txt/d c.txt is file
    # => "Stop at" will be the "b" directory and path[0] is c.txt
    def go_to_folder(self, path):

        if len(path) > 0 and path[0] == '':  # If the given path is a fullpath
            current = self.ancestor
            while '' in path:
                path.remove('')
        else:  # If the given path is a relative path
            current = self

        while True:

            if len(path) == 0:  # Arrive at the folder
                return {"Stop_at": current, "Error_mes": 'Success'}

            name = path[0]
            # If the next folder down from the path exist
            if name in current.children:

                child = current.children[name]

                if child.type == 'd':
                    current = current.children[name]
                    path.pop(0)
                    continue
                else:  # If the child is a file
                    return {"Stop_at": current,
                            "Error_mes": "Destination is a file"}
            else:  # If the next folder is not exist
                return {"Stop_at": current,
                        "Error_mes": "No such file or directory"}

    # Go to a Node with a given path
    def go_to_Node(self, path):

        name = path[-1]  # Name of the file
        if name == '':
            name = "/"

        path.pop(-1)
        destination = self.go_to_folder(path)

        if destination["Error_mes"] == "Success" and\
                name in destination['Stop_at'].children:
            current = destination['Stop_at'].children[name]
            return {"Stop_at": current, "Error_mes": "Success"}
        else:
            destination["Error_mes"] = "No such file"
            return destination

    # Create children (file or directory) of the node
    # mkdir and touch will share this function
    def create(self, owner, name, flag):
        if flag == "d":  # Create a folder
            permission = 'drwxr-x'
        else:  # Create a file
            permission = '-rw-r--'

        # Get full path from parent path
        if self.path == "/":
            path = self.path + name
        else:
            path = self.path + '/' + name

        new_node = Node(self, {}, permission, owner, path, self.ancestor)
        new_node.children["."] = new_node
        new_node.children[".."] = new_node.parent
        self.children[name] = new_node


# Each of the comman will return the error number correspond to the list below.
def Error_handling(num, command):

    Error_list = {
        1: "Permission denied", 2: "No such file or directory",
        3: "Operation not permitted", 4: "Ancestor directory does not exist",
        5: 'Is a directory', 6: "File exists", 7: "No such file",
        8: "Not a directory", 9: "Directory not empty",
        10: "Cannot remove pwd", 11: "Destination is a directory",
        12: "Source is a directory", 13: "Invalid syntax",
        14: "The user already exists", 15: "Invalid user",
        16: "The user does not exist", 17: "Invalid mode",
        18: "Command not found"
    }

    if num != 0:  # num = 0: success
        print(f'{command}: {Error_list[num]}')


def check_and_split_syntax(cmd):
    # Initialize variable
    # The program will read and split arg by arg one at the time
    # The delimiter is setted to " or " " depends on split_arg function
    flag_list = []
    valid_path = True
    valid_format = True
    valid = True
    valid_user = True
    path_list = []
    format_string = ''
    user = ''
    path_1 = ''

    command, remain = split_arg(cmd)
    valid = check_invalid_char(command)

    # Group different command with the same syntax to different groups
    if command in ('exit', 'pwd') and remain != '':
        valid = False

    elif command in ('touch', 'cd', 'rm', 'rmdir', 'mkdir', 'ls'):
        if command == "ls":
            path_1 = check_flag(remain,
                                            ["-a", "-d", "-l"], flag_list)
        elif command == 'mkdir':
            path_1 = check_flag(remain, ["-p"], flag_list)
        else:
            path_1 = remain
        # Ls command can recieve empty path
        if not (command == 'ls' and path_1 == ''):
            path_1, remain = split_arg(path_1)
            valid_path = check_path(path_1) and remain == ''

    elif command in ('adduser', 'deluser', 'su'):
        # Su command can recieve empty path
        if not (command == "su" and remain == ''):
            user, remain = split_arg(remain)
            valid_user = check_invalid_char(user) and remain == ''

    elif command in ('cp', 'mv'):
        # Cp and mv recieve 2 paths
        path_1, remain = split_arg(remain)
        path_2, remain = split_arg(remain)
        valid_path = check_path(path_1) and check_path(path_2) and remain == ''
        path_2 = path_2.split("/")
        path_list.append(path_2)

    elif command in ('chmod', 'chown'):
        remain = check_flag(remain, ["-r"], flag_list)
        if command == "chmod":
            format_string, remain = split_arg(remain)
            path_1, remain = split_arg(remain)
            if not check_invalid_char(format_string, ["=", "-", "+"]):
                valid = False
            valid_format = check_format_string(format_string)
            valid_path = check_path(path_1) and remain == ''
        else:
            user, remain = split_arg(remain)
            path_1, remain = split_arg(remain)
            valid_path = check_path(path_1) and remain == ''
            valid_user = check_invalid_char(user)

    if path_1 == '':
        path_1 = []
    else:
        path_1 = path_1.split("/")

    path_list.insert(0, path_1)

    valid = valid and valid_user and valid_path
    
    return (valid, command, path_list, flag_list,
            user, format_string, valid_format)


# Check format string of chmod
def check_format_string(remain):

    if len(remain) < 1:
        return False

    index = 0
    while index < len(remain) and remain[index] in 'uoa':
        index += 1

    # uoa[+=-] not in remain or [uoa...] is the only thing remain contains
    if (index == 0 and remain[0] not in '-+=') or index == len(remain):
        return False
    elif remain[index] not in '-+=':
        return False
    else:
        if len(remain) - index > 1:  # Avoid a=
            for char in remain[index + 1:]:
                if char not in 'rwx':
                    return False
    return True


# Check valid of path, file and folder name
def check_path(path):
    if check_invalid_char(path, ["/"]):

        path = path.split("/")
        # Avoid test///a/b
        # Avoid False check with the path "/" which -> ['',''] when split
        if '' in path and \
                (path.count('') > 1 or path[0] != '') and path != ['', '']:
            return False
        else:
            return True
    else:
        return False


# Check flag recieve a list of valid flag
def check_flag(remain: str, valid_flag: list,
               flag_list: list):  # -> (bool, str) and adjust flag_list

    # Check for syntax form: -char or "-char" until the last argument
    while ((len(remain) > 2 and remain[0] == "-" and remain[2] == " ") or
           (len(remain) > 4 and remain[0] == "\"" and remain[1] == "-")):
        prev_remain = remain
        flag, remain = split_arg(remain)
        if flag in valid_flag and flag not in flag_list:
            flag_list.append(flag)
        else:
            remain = prev_remain
            break

    # Ls command can have flag as a last argument
    # This if condition is to check if it is a flag or path
    # The -l condition is to determine ls command
    # The only command with dash -l is ls
    if "-l" in valid_flag and remain in valid_flag and remain not in flag_list:
        flag_list.append(remain)
        remain = ''
    return remain


def split_arg(string):
    # If the string start with a " and contain another "
    if len(string) > 1 and string[0] == "\"" and "\"" in string[1:]:

        result = string.split("\"", 2)[1]
        remain = string.split("\"", 2)[2]

        # If it is not the last arg
        # And the follow after " is not space example: "ls"-d
        if len(remain) > 0 and remain[0] != " ":
            remain = "$$$Inv@lid$$$"
            # The main function will have other check that will return invalid
        else:
            remain = remain.strip()
        return result, remain
    else:  # If not just split with whitespace
        # String like a"adsf" will be catch when check path, user,...
        result = string.split(" ", 1)[0]
        if len(string.split(" ")) == 1:
            return result, ''
        else:
            remain = string.split(" ", 1)[1].strip()
            return result, remain


def check_invalid_char(string, addition=[]):
    # Addition to add other valid syntax for certain arg (a=rwx)...
    valid_syntax = [" ", ".", "..", "-", "_"] + addition

    for syntax in valid_syntax:
        string = string.replace(syntax, "a")
    return string.isalnum()


# Function to check permission that is needed for each of the command
# If the command need certain permission(e.g ancestor execute)
# -> Set the ancestor_x to True when calling the function
def check_permission(current, user, ancestor_x=False, parent_w=False,
                     dir_x=False, file_r=False, file_w=False, parent_r=False):

    a_x = ancestor_x and not current.check_x_ancestor(user)
    p_w = parent_w and current.parent.permission(user)[1] != 'w'
    d_x = dir_x and current.permission(user)[2] != 'x'
    f_r = file_r and current.permission(user)[0] != 'r'
    f_w = file_w and current.permission(user)[1] != 'w'
    p_r = parent_r and current.parent.permission(user)[0] != 'r'

    # Return False if the user does not have permission
    return not(a_x or p_w or d_x or f_r or f_w or p_r)


# Touch and mkdir share the same function
def make(current, user, path, command, arg=[]):

    name = path[-1]  # Get the name of the Node we want to make
    path.pop(-1)  # Get the path to its parent
    destination = current.go_to_folder(path)

    # Create tmp child to check permission
    tmp_child = Node(destination["Stop_at"], {}, '-'*7, '', '',
                     destination["Stop_at"].ancestor)

    if destination["Error_mes"] == 'Success':
        destination = destination["Stop_at"]  # This is the Node parent

        if name in destination.children:  # If Node exists
            if command == "mkdir":
                res = 6
            else:  # Touch do nothing
                res = 0
        elif not check_permission(tmp_child, user,
                                  ancestor_x=True, parent_w=True):
            res = 1
        else:
            del tmp_child
            flag = 'f'

            if command == "mkdir":
                flag = 'd'
            destination.create(user, name, flag)
            res = 0

        if "-p" in arg:  # Ignore all error messages with -p
            res = 0
        return res

    # If the ancestor dont exist and -p in arg
    elif (destination["Error_mes"] == "No such file or directory" and
          "-p" in arg):

        destination = destination["Stop_at"]

        # If user have permission then create the Node
        # If not only create ancestors
        if not check_permission(tmp_child, user,
                                ancestor_x=True, parent_w=True):
            return 0

        path.append(name)
        while len(path) > 0:
            subname = path[0]
            destination.create(user, subname, "d")
            # Go to the next Node to create
            destination = destination.children[subname]
            path.pop(0)
        return 0
    # If ancestor is a file and -p in arg
    elif "-p" in arg and destination["Error_mes"] == "Destination is a file":
        return 0
    else:
        return 4


# Mv and cp shares the same function
def mv_cp(current, user, path, path_2, command):
    terminate = False  # Sign for the source to be deleted(mv command)

    src = current.go_to_Node(path)  # Seek for the Node

    dst_name = path_2[-1]
    path_2.pop(-1)
    dst = current.go_to_folder(path_2)

    if src["Error_mes"] == "Success" and dst["Error_mes"] == "Success":
        src = src['Stop_at']
        dst = dst['Stop_at']
        # Des is an existed file
        if dst_name in dst.children and \
                dst.children[dst_name].type == '-':
            return 6
        elif (dst_name in dst.children and
              dst.children[dst_name].type == 'd'):  # Des is dir
            return 11
        elif src.type == 'd':  # Source is file
            return 12

        # Create Fake child to test permission
        test_child = Node(dst, {}, "-"*7, '', '', dst.ancestor)
        if command == "mv":
            check = check_permission(src, user, ancestor_x=True, parent_w=True)
            check_2 = check_permission(test_child, user,
                                       ancestor_x=True, parent_w=True)
            terminate = True
        else:
            check = check_permission(src, user, ancestor_x=True, file_r=True)
            check_2 = check_permission(test_child, user,
                                       ancestor_x=True, parent_w=True)

        del test_child
        if not(check and check_2):  # Permission denied
            return 1
        else:
            dst.create(user, dst_name, 'f')
            if terminate:
                src.parent.children.pop(src.path.split('/')[-1])
            return 0
    elif src["Error_mes"] != "Success":  # No such file
        return 7
    else:  # No such file or dir
        return 2


def rm_path(current, user, path):
    name = path[-1]  # Get the Node name
    target = current.go_to_Node(path)

    if target["Error_mes"] == "Success":
        target = target["Stop_at"]

        if target.type == 'd':  # File is dir
            return 5
        elif not check_permission(target, user,
                                  ancestor_x=True, file_w=True, parent_w=True):
            return 1
        else:
            target.parent.children.pop(name)
            del target
            return 0

    else:  # File not found
        return 7


def rmdir(current, user, path):
    name = path[-1]
    target = current.go_to_folder(path)

    if target["Error_mes"] == "Success":
        target = target["Stop_at"]

        # Not empty dir
        if len(target.children) > 3 or \
                target.path != '/' and len(target.children) > 2:
            return 9
        elif target == current:  # PWD
            return 10
        elif not check_permission(target, user,
                                  ancestor_x=True, parent_w=True):
            return 1
        else:
            target.parent.children.pop(name)
            del target
            return 0

    elif target["Error_mes"] == "Destination is a file":  # Not a directory
        return 8
    else:
        return 2


def chmod(current, user, path, format_string, arg):
    target = current.go_to_Node(path)  # Get the target Node

    if target["Error_mes"] == "Success":
        target = target["Stop_at"]

        # Initialize permission string
        u = ["-"] * 3
        o = ["-"] * 3
        perm = ["-"] * 3

        format_string = format_string.replace('a', 'uo')  # all -> user + other
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
        visit_list = [target]  # List of Node to chmod

        while len(visit_list) > 0:  # DFS and dictionary sorting
            destination = visit_list[-1]
            visit_list.pop(-1)
            if user not in (destination.owner, "root"):
                Error_handling(3, 'chmod')
            elif not check_permission(destination, user, ancestor_x=True):
                Error_handling(1, 'chmod')
            else:
                permission = list(destination.all_permission)

                if '=' in format_string:
                    if 'u' in format_string:
                        permission[:3] = u
                    if 'o' in format_string:
                        permission[3:] = o

                elif '+' in format_string:
                    for index in range(6):
                        if full_perm[index] != "-":
                            permission[index] = full_perm[index]

                else:
                    for index in range(6):
                        if full_perm[index] != "-":
                            permission[index] = '-'

                destination.all_permission = ''.join(permission)
            if "-r" in arg:
                # Dictionary sorting and using DFS(first in last out)
                # We reverse the child Node to append
                # First alphatbetic letter appended last and comes out first
                child_list = sorted(destination.children.keys(), reverse=True)
                for child in child_list:  # Child is the name assigned
                    if child not in ("..", "/", "."):
                        # Get the Node from name
                        tovisit = destination.children[child]
                        visit_list.append(tovisit)
        return 0
    else:
        return 2  # No such file or dir


def chown(current, user, path, arg):

    target = current.go_to_Node(path)

    if target['Error_mes'] == "Success":

        target = target["Stop_at"]
        visit_list = [target]

        while len(visit_list) > 0:  # DFS

            destination = visit_list[-1]
            visit_list.pop(-1)
            destination.owner = user

            if "-r" in arg:
                # Child here is name of Node
                for child in destination.children:
                    if child not in ("..", "/", "."):
                        # Get the Node from name
                        tovisit = destination.children[child]
                        visit_list.append(tovisit)
        return 0
    else:
        return 2


def ls(current, user, path, arg):
    original_path = "/".join(path)
    print_one = False
    pwd = False
    if len(path) == 0:  # The ls command receive no argument for path
        target = current
        pwd = True
    else:
        target = current.go_to_Node(path)

        if target["Error_mes"] == "Success":
            target = target["Stop_at"]
        else:  # If path does not exist
            return 2

    name_list = []  # List to store Nodes that will be display

    # Flag d
    # If destination is file or arg have -d
    if target.type == '-' or '-d' in arg:
        if not check_permission(target, user, ancestor_x=True, parent_r=True):
            return 1
        else:
            print_one = True  # Only the target Node will be print
            parent = target.parent
            name = target.path.split("/")[-1]

            if name == '':  # If the folder is root
                name = '/'

            if pwd:  # If -d and no argument given for path
                parent = target
                name = "."

            name_list.append(name)  # Only add the file or folder to the list
    else:
        if not check_permission(target, user, ancestor_x=True, file_r=True):
            return 1
        else:
            # We want to list the content inside(child) -> target is the parent
            parent = target
            # Get all the contents inside and sort
            name_list = sorted(parent.children.keys())

            if parent.path == "/":  # Root contain root as a child
                name_list.remove("/")

    # Flag a
    if "-a" not in arg:
        if print_one:
            if pwd or original_path[0] == ".":
                name_list.pop(0)
        else:
            res_list = []
            for item in name_list:
                if item[0] != '.':  # File and folder start with "."
                    res_list.append(item)
            name_list = res_list

    res = ''
    # Flag l and result
    for item in name_list:

        child = parent.children[item]  # Get the Node of the child

        # Keep the path if it is file or -d dir and not current
        if not pwd and print_one:
            item = original_path

        if "-l" in arg:
            res += child.type + child.all_permission + ' ' +\
                        child.owner + ' ' + item + '\n'  # Long listing format
        else:
            res += item + '\n'  # Simple format

    print(res, end='')
    return 0


def main():
    user_list = ['root']
    active_user = 'root'

    root = Node(None, {}, 'drwxr-x', 'root', '/', None)
    root.parent = root
    root.children["/"] = root
    root.ancestor = root
    root.children["."] = root
    root.children[".."] = root
    current = root

    while True:

        cmd = input(f"{active_user}:{current.path}$ ").strip()

        if cmd == '':
            continue

        valid, command, path_list, arg_list,\
            user, format_string, valid_format = check_and_split_syntax(cmd)

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
            result = current.go_to_folder(path)

            if result["Error_mes"] == "Success":
                folder = result["Stop_at"]

                if not check_permission(folder, active_user, dir_x=True):
                    Error_handling(1, command)
                else:
                    current = folder
            else:
                print(f"cd: {result['Error_mes']}")

        elif command in ("touch", "mkdir"):
            Error_handling(make(current, active_user,
                                path, command, arg_list), command)

        elif command == "pwd":
            print(current.path)

        elif command == 'rmdir':
            Error_handling(rmdir(current, active_user, path), command)

        elif command == 'rm':
            Error_handling(rm_path(current, active_user, path), command)

        elif command == 'adduser':
            if active_user == 'root':
                if user in user_list:
                    Error_handling(14, command)
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
            Error_handling(mv_cp(current, active_user,
                                 path, path_2, command), command)

        elif command == 'chmod':
            if not valid_format:
                Error_handling(17, command)
            else:
                Error_handling(chmod(current, active_user, path,
                                     format_string, arg_list), command)

        elif command == 'chown':
            if active_user != 'root':
                Error_handling(3, command)
            elif user not in user_list:
                Error_handling(15, command)
            else:
                Error_handling(chown(current, user, path, arg_list), command)
        else:
            Error_handling(18, command)


if __name__ == '__main__':
    main()
