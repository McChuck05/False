#!/usr/bin/python
# False interpreter
# Copyright (C) 2022 McChuck
# Released under GNU General Public License
# See LICENSE for more details.
#
# The pick character has been replaced with '>', which was unused.
# Keyboard and display flushing is done automatically.
# assembly programming is omitted, and the '`' character is used as a break.


import sys
import os

try:
    from getch import getch, getche         # Linux
except ImportError:
    from msvcrt import getch, getche        # Windows

data = []
running = True
variables = []


def push(item):
    global data
    data.append(item)

def pop(deep):
    global data
    if len(data) > 0:
        return data.pop(-(deep+1))
    else:
        print("\n\nCan't pop from an empty stack")
        raise IndexError


def parse(mem):
    try:
        global data, running, variables
        mem = mem + ' '
        char = ''
        in_string = False
        in_lambda = False
        in_char = False
        in_num = False
        in_comment = False

        for char_index, char in enumerate(mem):

            if in_string:
                if char == '"':
                    print(build_str, end="", flush=True)
                    build_str = ""
                    in_string = False
                else:
                    build_str += char
                continue

            elif in_char:
                push(ord(char))
                in_char = False
                continue

            elif in_lambda:
                build_lambda += char
                if char == ']':
                    lambda_level -= 1
                    if lambda_level == 0:
                        in_lambda = False
                        push(build_lambda)
                        build_lambda = ""
                if char == '[':
                    lambda_level += 1
                continue

            elif in_comment:
                if char == '}':
                    in_comment = False
                continue

            elif in_num:
                if char.isdigit():
                    build_num *= 10
                    build_num += int(char)
                    continue
                else:
                    in_num = False
                    push(build_num)
                    build_num=0

            if char == '?':                         #   IF
                to_exec = pop(0)
                condition = pop(0)
                if condition != 0:
                    if to_exec[0] == '[' and to_exec[-1] == ']':
                        to_exec = to_exec[1:-1]     # strip off brackets to avoid recursion error
                        parse(to_exec)
                    else:
                        print("\n\nError: ? expected lambda: ", to_exec)
                        raise ValueError

            elif char == '#':                         #   WHILE
                to_exec = pop(0)
                to_eval = pop(0)
                if to_eval[0] == '[' and to_eval[-1] == ']':
                    to_eval = to_eval[1:-1]
                else:
                    print("\n\nError: # expected lambda: ", to_eval)
                    raise ValueError
                if to_exec[0] == '[' and to_exec[-1] == ']':
                    to_exec = to_exec[1:-1]
                else:
                    print("\n\nError: # expected lambda: ", to_exec)
                    raise ValueError
                parse(to_eval)
                condition = pop(0)
                while condition != 0:
                    parse(to_exec)
                    parse(to_eval)
                    condition = pop(0)

            elif char == '!':       #   execute
                to_exec = pop(0)
                if to_exec[0] == '[' and to_exec[-1] == ']':
                    to_exec = to_exec[1:-1]
                    parse(to_exec)
                else:
                    print("\n\nError: ! expected lambda: ", to_exec)
                    raise ValueError

            elif char == "'":       # next character's ordinal value will be pushed
                in_char = True

            elif char.isdigit():
                in_num = True
                build_num = int(char)

            elif char.islower():    #   variables
                push(char)

            elif char == ':':        #  store
                to_var = pop(0)
                value = pop(0)
                if to_var.islower:
                    index = ord(to_var) - ord('a')
                    variables[index] = value
                else:
                    print("\n\nError: : expected variable: ", to_var)
                    raise ValueError

            elif char == ';':       #   fetch
                from_var = pop(0)
                if from_var.islower:
                    index = ord(from_var) - ord('a')
                    push(variables[index])
                else:
                    print("\n\nError: ; expected variable: ", from_var)
                    raise ValueError

            elif char == '"':
                in_string = True
                build_str = ""

            elif char == '[':
                in_lambda = True
                build_lambda = char
                lambda_level = 1

            elif char == '$':       #   DUP
                temp = data[-1]
                push(temp)

            elif char == '%':       #   DROP
                pop(0)

            elif char == '\\':       #   SWAP
                temp = pop(1)
                push(temp)

            elif char == '@':       #   ROT
                temp = pop(2)
                push(temp)

            elif char == '<':       # PICK      # 0 is top of stack
                deep = pop(0)
                if len(data) > deep:
                    push(data[deep])
                else:
                    print("\n\nError: Attempt to pick:", deep, "< deeper than stack height", flush=True)
                    raise IndexError

            elif char == '+':
                temp2 = pop(0)
                temp1 = pop(0)
                push(temp1 + temp2)

            elif char == '-':
                temp2 = pop(0)
                temp1 = pop(0)
                push(temp1 - temp2)

            elif char == '*':
                temp2 = pop(0)
                temp1 = pop(0)
                push(temp1 * temp2)

            elif char == '/':
                temp2 = pop(0)
                temp1 = pop(0)
                if temp2 != 0:
                    push(temp1 // temp2)    #   integer division
                else:
                    print("\n\nError:  Division by zero")
                    raise ValueError

            elif char == '_':       # negate
                temp1 = pop(0)
                push(-temp1)

            elif char == '~':       #   NOT
                temp1 = pop(0)
                push(~temp1)

            elif char == '&':       #   AND
                temp2 = pop(0)
                temp1 = pop(0)
                push(temp1 & temp2)

            elif char == '|':       #   OR
                temp2 = pop(0)
                temp1 = pop(0)
                push(temp1 | temp2)

            elif char == '>':
                temp2 = pop(0)
                temp1 = pop(0)
                if temp1 > temp2:
                   push(-1)         # True
                else:
                    push(0)         # False

            elif char == '=':
                temp2 = pop(0)
                temp1 = pop(0)
                if temp1 == temp2:
                    push(-1)
                else:
                    push(0)

            elif char == '^':       #   read char from keyboard
                temp1 = ord(getche())
                push(temp1)

            elif char == '.':       #   print number
                temp1 = pop(0)
                if isinstance(temp1, int):
                    print(temp1, end="", flush=True)
                else:
                    print("\n\nError: expected number to print:", temp1)
                    raise ValueError

            elif char == ',':       # print char
                temp1 = pop(0)
                if isinstance(temp1, int) and temp1 >= 0:
                    print(chr(temp1), end="", flush=True)
                else:
                    print("\n\nError: expected character to print:", temp1)
                    raise ValueError

            elif char == '{':       # comment
                in_comment = True

            elif char == '`':       #   BREAK
                break

            else:
                pass
        # END for

        if in_string:
            print("\n\nError: Incomplete string")
            raise ValueError
        if in_lambda:
            print("\n\nError: Incomplete lambda")
            raise ValueError
        if in_char:
            print("\n\nError: Incomplete character")
            raise ValueError
        if in_num:
            print("\n\nError: Incomplete number")
            raise ValueError
        if in_comment:
            print("\n\nError: Incomplete comment")
            raise ValueError

    except(ValueError):
        excerpt = extract_excerpt(char_index, mem)
        print("\nValue error", char, "@", char_index, "\n", excerpt)
        print("Variables:", variables, "\nStack:", data)
        exit()
    except(IndexError):
        excerpt = extract_excerpt(char_index, mem)
        print("\nIndex error", char, "@", char_index, "\n", excerpt)
        print("Variables:", variables, "\nStack:", data)
        exit()

def extract_excerpt(index, code):
    low = index - 10
    high = index + 10
    if low < 0:
        low = 0
    if high > len(code):
        high = len(code)
    return code[low:high]


def main(args):
    global variables, data

    print()
    for i in range(26):
        variables.append(0)
    try:
        if len(args) == 1:
            infile_name = args[0]
            mem = ''
            with open(infile_name, "r") as in_file:
                raw = in_file.read()
                in_file.close()
            parse(raw)
            print("\n\nProgram completed")
            print("Variables:", variables, "\nStack:", data)
        else:
            print("usage: python false.py infile.f\n")
    except FileNotFoundError:
        print("< *Peter_Lorre* >\nYou eediot!  What were you theenking?\nTry it again, but thees time with a valid file name!\n</ *Peter_Lorre* >\n")
        print("usage: python false.py infile.f\n")
    except(ValueError, IndexError):
                print("I just don't know what went wrong!\n")
                in_file.close()


if __name__ == '__main__':
    main(sys.argv[1:])
