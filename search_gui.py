#!/usr/bin/python3

import sys
import os
import curses


def satisfies(filename, pattern, show_hidden, case_sensitive, regex):
    if not case_sensitive:
        filename = filename.lower()
        pattern = pattern.lower()
    if not show_hidden and filename[0] == ".":
        return False
    if regex:
        pass
    return pattern in filename


def auto_complete(search_path, filename):
    search_path = path + filename
    if os.path.isdir(search_path):
        search_path += "/"
    return search_path


kwargs = {"show_hidden": False, "case_sensitive": False, "regex": False}

# init screen and hide cursor
window = curses.initscr()
curses.noecho()

# get location of the file used, to send the result output
pipe_file = sys.argv[1]

search_path = ""

try:
    while True:
        # parse input
        path = ""
        search_pattern = ""
        path_elem = search_path.split("/")
        if len(path_elem) > 1:  # if there is at least one '/' in the search_path
            search_pattern = path_elem[-1]
            prefix = path_elem[:-1]
            for d in prefix:
                path += d + "/"
        else:  # only if no leading '/'
            search_pattern = search_path
            path = "./"

        # get list of files
        try:
            dirs = os.listdir(path)
        # if file not found don't crash, just show no files
        except FileNotFoundError:
            dirs = []

        # filter files
        dirs = [
            filename
            for filename in dirs
            if satisfies(filename, search_pattern, **kwargs)
        ]
        # output = os.popen(f'ls "{path}" | grep "{filename}"').read()

        height, width = window.getmaxyx()
        for index, name in enumerate(dirs):
            h = 3 + index
            if h >= height:
                break
            if len(name) >= width - 2:
                name = name[: width - 5] + "..."
            window.addstr(3 + index, 1, name)
        window.addstr(1, 1, search_path)
        window.refresh()

        b = window.getch()
        if b == 127:  # backspace - delete last character
            search_path = search_path[:-1]
        elif b == ord("\t"):  # tab - autocomplete
            if len(dirs):
                search_path = auto_complete(search_path, dirs[0])
        elif b == ord("\n"):  # enter - break the loop, then print the search path
            break
        else:  # normal character, append to search_path
            search_path += chr(b)

        window.clear()
finally:
    # clean up - close screen
    curses.endwin()

result = search_path.replace(' ', '\\ ')

with open(pipe_file, "w") as out:
    out.write(result)
    out.write("\n")
