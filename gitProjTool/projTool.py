#!/usr/local/bin python3
# -*- coding: utf-8 -*-

import os
import argparse
import subprocess
import prettytable as pt
from typing import List
from multiprocessing import Pool

ARGS: argparse.Namespace = None


class Commiter(object):
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self.add = 0
        self.sub = 0

    def amountOfCode(self):
        if not self.name or len(self.name) == 0:
            return

        cmd = "git log --author=\"%s\" --pretty=tformat: --numstat" % (
            self.name)

        global ARGS
        before = ARGS.before
        if before and len(before) > 0:
            cmd += " --before=\"%s\"" % (before)

        after = ARGS.after
        if after and len(after) > 0:
            cmd += " --after=\"%s\"" % (after)

        success, result = subprocess.getstatusoutput(cmd)
        if success != 0 or result == None or len(result) == 0:
            return

        results = result.split("\n")
        for line in results:
            cmps = line.split("\t")
            if len(cmps) != 3:
                continue

            addVal, subVal = cmps[0], cmps[1]
            if addVal.isnumeric():
                self.add += int(addVal)
            if subVal.isnumeric():
                self.sub += int(subVal)


def parseArgsFromShell():
    parser = argparse.ArgumentParser()
    parser.add_argument("gitProjPath")
    parser.add_argument("-before")
    parser.add_argument("-after")

    global ARGS
    ARGS = parser.parse_args()


def changeToProjDir():
    global ARGS
    os.chdir(ARGS.gitProjPath)


def getAllCommitersOfProj() -> List[Commiter]:
    cmd = "git log --pretty=format:\"%an %ae\""
    success, result = subprocess.getstatusoutput(cmd)
    if success != 0:
        return None

    commiters = []
    infos = set(result.split("\n"))
    for info in infos:
        if not info or len(info) == 0:
            continue

        cmps = info.split(" ")
        emailIdx = len(cmps) - 1
        email = cmps[emailIdx]
        if not email or len(email) == 0:
            continue

        name = " ".join(cmps[0:emailIdx])
        commiter = Commiter(name, email)
        commiters.append(commiter)

    return commiters


def getAmountOfCode(commiter: Commiter) -> Commiter:
    commiter.amountOfCode()
    return commiter


def printAmountOfCodeOfCommiters(commiters: List[Commiter]):
    if commiters is None or len(commiters) == 0:
        return

    pool = Pool()
    results = pool.map(getAmountOfCode, commiters)
    pool.close()
    pool.join()

    sortedResult = sorted(
        results, key=lambda commiter: commiter.add, reverse=True)

    tb = pt.PrettyTable()
    tb.field_names = ["name", "email", "add", "sub"]
    for commiter in sortedResult:
        tb.add_row([commiter.name, commiter.email, commiter.add, commiter.sub])
    print(tb)


def main():
    parseArgsFromShell()
    changeToProjDir()
    commiters = getAllCommitersOfProj()
    printAmountOfCodeOfCommiters(commiters)


if __name__ == "__main__":
    main()
