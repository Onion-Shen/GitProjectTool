#!/usr/local/bin python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import prettytable as pt
from typing import List
from multiprocessing import Pool

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
        self.get_commit_detail()

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
            cmps = line.split("\t")
            self.add += 0 if cmps[0] == "-" else int(cmps[0])
            self.sub += 0 if cmps[1] == "-" else int(cmps[1])


def generate_commiter(name: str) -> Commiter:
    return Commiter(name)


def get_all_commiter() -> List[Commiter]:
    cmd = "git log --pretty=format:\"%an\""
    success, result = subprocess.getstatusoutput(cmd)
    if success != 0:
        return None
    names = set(result.split("\n"))

    pool = Pool(processes=10)
    commiters = pool.map(generate_commiter, names)
    pool.close()
    pool.join()

    return sorted(commiters, key=lambda commiter: commiter.add, reverse=True)


def print_commiters_info():
    commiters = get_all_commiter()

    if not commiters or len(commiters) == 0:
        return

    tb = pt.PrettyTable()
    tb.field_names = ["name", "add", "sub"]
    for commiter in commiters:
        tb.add_row([commiter.name, commiter.add, commiter.sub])
    print(tb)


if __name__ == "__main__":
    parse_args()
    if not GIT_PORJECT_PATH or len(GIT_PORJECT_PATH) == 0:
        sys.exit(1)

    os.chdir(GIT_PORJECT_PATH)

    print_commiters_info()
