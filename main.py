# main

import os
import sys
import time
import hashlib

from typing import NewType



BUF_SIZE = 2**16



Hash = NewType("Hash", str)



SHIFT_STR = "-   "
def print_shifted(shift: int, string: str):
    print(shift*SHIFT_STR+string)



class File:
    def __init__(self, path: str):
        self.path: str = path
        self.name: str = os.path.basename(os.path.normpath(path))
        self._hash: Hash | None = None

    def hash(self) -> Hash:
        if self._hash != None:
            return self._hash
        sha1 = hashlib.sha1()
        with open(self.path, 'rb') as file:
            while True:
                data: bytes = file.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        self._hash = Hash(sha1.hexdigest())
        return self._hash

    def print_pretty(self, shift=0):
        print_shifted(shift, f"{self.name}\t\t{self.hash()}")



class Folder:
    def __init__(self, path: str):
        self.path: str = path
        self.name: str = os.path.basename(os.path.normpath(path))
        self.files: list[File] = []
        self.folders: list[Folder] = []
        for entry in os.scandir(path):
            match entry:
                case folder if entry.is_dir():
                    self.folders.append(Folder(folder.path))
                case file if entry.is_file():
                    self.files.append(File(file.path))
        self._hash: Hash | None = None

    def hash(self) -> Hash:
        if self._hash != None:
            return self._hash
        sha1 = hashlib.sha1()
        for file in self.files:
            data: bytes = bytes(file.hash(), 'utf-8')
            sha1.update(data)
        self._hash = Hash(sha1.hexdigest())
        return self._hash

    def print_pretty(self, shift=0):
        print_shifted(shift, f"{self.name}\t\t{self.hash()}")
        for folder in self.folders:
            folder.print_pretty(shift+1)
        for file in self.files:
            file.print_pretty(shift+1)



def calc_diff_similar_paths(folder1: Folder, folder2: Folder) -> list[(Folder | File, Folder | File)]:
    def create_f_to_h(folder: Folder) -> dict[Folder | File, Hash]:
        res = {}
        for subfolder in folder.folders:
            res[subfolder] = subfolder.hash()
        for file in folder.files:
            res[file] = file.hash()
        return res

    # Folder/File to Hash
    f_to_h_1: dict[Folder | File, Hash] = create_f_to_h(folder1)
    f_to_h_2: dict[Folder | File, Hash] = create_f_to_h(folder2)

    diff: set[(Folder | File, Folder | File)] = set()
    for f1 in f_to_h_1:
        print(f1.name)
        print(f1.path)
        for f2 in f_to_h_2:
            print(SHIFT_STR+f2.name)
            print(SHIFT_STR+f2.path)
            if f1.name == f2.name and f_to_h_1[f1] != f_to_h_2[f2]:
                print(f"add: {f1.name=}\t\t\t{f2.name=}")
                print(f"add: {f1.path=}\t\t\t{f2.path=}")
                diff.add((f1, f2))

    return list(diff)



def calc_diff_similar_hashs(folder1: Folder, folder2: Folder) -> list[list[Folder | File]]:
    return []



def interactive_decider(folder1: Folder, folder2: Folder):
    print("Calculating hashes... ", end="", flush=True)
    time_start = time.time()
    if folder1.hash() == folder2.hash():
        if folder1.name != folder2.name:
            print("Folders' content is equal, but they have different names.")
            print("What would you like to do?")
            raise NotImplementedError()
        else:
            print("Folders' content is equal.")
        return
    time_finish = time.time()
    print(f"finished in {time_finish-time_start:.1f}s\n")
    print("This is interactive folder comparator.")
    print("First, let's decide what to do, and only then I'll do it all.")
    diff_sim_path: list = calc_diff_similar_paths(folder1, folder2)
    diff_sim_hash: list = calc_diff_similar_hashs(folder1, folder2)
    while diff_sim_path != [] or diff_sim_hash != []:
        for d in diff_sim_path:
            match d:
                case (f1, f2):
                    print(f"{f1.name=}\t\t\t{f2.name=}")
                case _:
                    raise NotImplementedError()
        input()



def parse_argv(argv: list[str]) -> tuple[str, str]:
    match argv:
        case [str(path_to_sync_from), str(path_to_sync_to)]:
            return (path_to_sync_from, path_to_sync_to)
        case _:
            print(f"Expected two paths, but {len(argv)} got.")
            sys.exit(1)


def main() -> None:
    path_from, path_to = parse_argv(sys.argv[1:])

    folder_from = Folder(path_from)
    folder_to = Folder(path_to)

    interactive_decider(folder_from, folder_to)

    # folder_from.print_pretty()
    # folder_to.print_pretty()

    # print(folder_from.hash())
    # print(folder_to.hash())



if __name__ == "__main__":
    main()

