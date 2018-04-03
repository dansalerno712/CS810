import sys
import os
from CompilationEngine import CompilationEngine


def main():
    # make sure they used the program right
    if len(sys.argv) != 2:
        print("usage: python Compiler.py <some .jack file or a directory with .jack files in it>")
        return

    # holds the open file descriptors to pass to the Parser constructor
    fileHandles = []
    inputPath = sys.argv[1]

    # see if file or directory
    if inputPath.endswith(".jack"):
        # file
        jackFile = open(inputPath, 'r')
        fileHandles.append(jackFile)

    elif os.path.isdir(inputPath):
        # make sure that the path doesn't end in a slash for a directory
        if inputPath.endswith("/"):
            inputPath = inputPath[:-1]
        # get .vm files and open them from directory
        for file in os.listdir(inputPath):
            if file.endswith(".jack"):
                jack = open(os.path.join(inputPath, file), 'r')
                fileHandles.append(jack)
    else:
        # error
        print("You must enter a single .jack file or a directory with .jack files in it")

    for file in fileHandles:
        # create a compilation engine and start it, which will recursively
        # compile the entire file and generate the token xml file
        e = CompilationEngine(file)
        e.start()


if __name__ == '__main__':
    main()
