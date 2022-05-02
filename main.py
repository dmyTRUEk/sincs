# main

import os
import sys
import hashlib



BUF_SIZE = 2**16



def print_shifted(shift: int, string: str):
    SHIFT_STR = "-   "
    print(shift*SHIFT_STR+string)



class File:
    def __init__(self, path: str):
        self.path: str = path
        self.name: str = os.path.basename(os.path.normpath(path))
        self._hash: str | None = None

    def hash(self) -> str:
        if self._hash != None:
            return self._hash
        sha1 = hashlib.sha1()
        with open(self.path, 'rb') as file:
            while True:
                data: bytes = file.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        self._hash = sha1.hexdigest()
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
        self._hash: str | None = None

    def hash(self):
        if self._hash != None:
            return self._hash
        sha1 = hashlib.sha1()
        for file in self.files:
            data: bytes = bytes(file.hash(), 'utf-8')
            sha1.update(data)
        self._hash = sha1.hexdigest()
        return self._hash

    def print_pretty(self, shift=0):
        print_shifted(shift, f"{self.name}\t\t{self.hash()}")
        for folder in self.folders:
            folder.print_pretty(shift+1)
        for file in self.files:
            file.print_pretty(shift+1)



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

    folder_from.print_pretty()
    folder_to.print_pretty()

    print(folder_from.hash())
    print(folder_to.hash())



if __name__ == "__main__":
    main()

