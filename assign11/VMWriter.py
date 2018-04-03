class VMWriter(object):
    """Writes VM code to an output file"""

    def __init__(self, outputFile):
        super(VMWriter, self).__init__()
        self.outputFile = outputFile

    def writePush(self, segment, index):
        """Writes the vm command to push the index of segment onto
        the stack"""
        self.outputFile.write("push " + segment + " " + str(index) + "\n")

    def writePop(self, segment, index):
        """Writes the vm command to pop the top of the stack to index of segment"""
        self.outputFile.write("pop " + segment + " " + str(index) + "\n")

    def writeArithmetic(self, command):
        """Writes the vm code to perform the arithmetic command"""
        self.outputFile.write(command + "\n")

    def writeLabel(self, label, counter):
        """Writes the vm code for a label command"""
        self.outputFile.write("label " + label + "-" + str(counter) + "\n")

    def writeGoto(self, label, counter):
        """Writes the vm code for a goto command"""
        self.outputFile.write("goto " + label + "-" + str(counter) + "\n")

    def writeIf(self, label, counter):
        """Writes the vm code for an if command"""
        self.outputFile.write("if-goto " + label + "-" + str(counter) + "\n")

    def writeCall(self, name, nArgs):
        """Writes the vm code to call a function with nArgs arguments"""
        self.outputFile.write("call " + name + " " + str(nArgs) + "\n")

    def writeFunction(self, name, nLocals):
        """Writes the vm code to define a function with nLocals"""
        self.outputFile.write("function " + name + " " + str(nLocals) + "\n")

    def writeReturn(self):
        """Writes the vm code to return from a function call"""
        self.outputFile.write("return\n")

    def close(self):
        """Closes the output file"""
        self.outputFile.close()
