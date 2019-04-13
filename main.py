#!/usr/local/bin python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
from typing import List, Tuple, Dict

GIT_PORJECT_PATH: str = None
BEFORE: str = None
AFTER: str = None


def parse_args():
    argv = sys.argv
    global GIT_PORJECT_PATH
    GIT_PORJECT_PATH = argv[1]

    global BEFORE
    global AFTER
    for arg in argv[2:]:
        if arg.startswith("before"):
            cmps = arg.split("=")
            BEFORE = cmps[1]
        elif arg.startswith("after"):
            cmps = arg.split("=")
            AFTER = cmps[1]


class Commiter(object):
    def __init__(self, name: str):
        self.name = name
        self.add = 0
        self.sub = 0

    def get_commit_detail(self):
        if not self.name or len(self.name) == 0:
            return

        cmd = "git log --author=\"%s\" --pretty=tformat: --numstat" % (
            self.name)

        global BEFORE
        if BEFORE and len(BEFORE):
            cmd += " --before=\"%s\"" % (BEFORE)

        global AFTER
        if AFTER and len(AFTER):
            cmd += " --after=\"%s\"" % (AFTER)

        success, result = subprocess.getstatusoutput(cmd)
        if success != 0 or result == None or len(result) == 0:
            return

        results = result.split("\n")
        for line in results:
            details = line.split("\t")
            if details[0] != "-":
                self.add += int(details[0])
            if details[1] != "-":
                self.sub += int(details[1])

    def __str__(self):
        pack = {}
        pack.setdefault("name", self.name)
        pack.setdefault("add", self.add)
        pack.setdefault("sub", self.sub)
        result = pack.__str__()
        return result


def get_all_commiter() -> List[Commiter]:
    cmd = "git log --pretty=format:\"%an\""
    success, result = subprocess.getstatusoutput(cmd)
    if success != 0:
        return None

    names = result.split("\n")
    sets = set(names)

    commiters = []
    for name in sets:
        commiter = Commiter(name)
        commiter.get_commit_detail()
        commiters.append(commiter)

    return sorted(commiters, key=lambda commiter: commiter.add, reverse=True)


def print_commiters_info(commiters: List[Commiter]):
    if not commiters or len(commiters) == 0:
        return

    print("project commiters info:")
    for commiter in commiters:
        print(commiter)


class ProjectFile(object):
    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name
        self.line = self.get_file_lines()
        self.suffix = self.get_suffix()

    def get_suffix(self) -> str:
        cmps = self.name.split(".")
        if len(cmps) == 2:
            return cmps[1]
        return ""

    def get_file_lines(self) -> int:
        count = 0
        size = 8 * 1024 * 1024

        with open(self.path, encoding="utf-8") as fp:
            try:
                while 1:
                    buf = fp.read(size)
                    if not buf:
                        break
                    count += buf.count("\n")
            except:
                pass

        return count


def print_all_project_files_info(path: str):
    if not path or len(path) == 0:
        return

    print("files in project:")

    info: Dict[str, int] = {}
    for dirpath, _, filenames in os.walk(path, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            projectfile = ProjectFile(file_path, filename)

            if projectfile.line == 0 or len(projectfile.suffix) == 0:
                continue

            if projectfile.suffix in info:
                info[projectfile.suffix] += projectfile.line
            else:
                info[projectfile.suffix] = projectfile.line

    for suffix, line in info.items():
        pack = {"suffix": suffix, "line": line}
        print(pack)


if __name__ == "__main__":
    parse_args()
    if not GIT_PORJECT_PATH or len(GIT_PORJECT_PATH) == 0:
        sys.exit(1)

    os.chdir(GIT_PORJECT_PATH)

    commiters = get_all_commiter()
    print_commiters_info(commiters)
    print_all_project_files_info(GIT_PORJECT_PATH)
