# NOTE: This class does not error check because of the use of maps.
# If a command that shouldnt be run comes in, this will crash when it
# tries to pull from the maps, this is good enough for me


class CodeWriter:
    labelCounter = 0
    logicCounter = 0
    # helpers
    # puts the head of the stack in the D register and decrements stack pointer
    load_stack_head_to_D = "@SP\nAM=M-1\nD=M\n"
    # pushes the current value of the D register to the stack and increments statck pointer
    push_d_to_stack = "@SP\nM=M+1\nA=M-1\nM=D\n"
    # map between the arithmetic operations and the boolean/arithmetic operations that are used on their corresponding registers
    arithmeticMap = {
        "add": "+",
        "sub": "-",
        "neg": "-",
        "eq": "-",
        "lt": "-",
        "gt": "-",
        "and": "&",
        "or": "|",
        "not": "!"
    }
    # maps the logical stack operators to their jump directives in assembly
    logicalMap = {
        "eq": "JEQ",
        "lt": "JLT",
        "gt": "JGT"
    }
    # maps the memory access stack commands to their assembly keywords
    memoryMap = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT",
        "pointer": "3",
        "temp": "5",
    }

    # takes in a file path and creates an output file to write to
    def __init__(self, path):
        self.outputPath = ""
        self.outputFile = None
        # keeps track of how many labels we've made
        self.filename = ""

        self.outputPath = path
        # clears file in case this a redo
        self.outputFile = open(self.outputPath, 'w')
        self.outputFile.close()
        # appends to empty file
        self.outputFile = open(self.outputPath, 'a')

    # sets the filename for static memory stuff
    def setFileName(self, name):
        self.filename = name

    # the init function for vm does 2 things
    # 1) sets SP to 256
    # 2) call Sys.init
    def writeInit(self):
        output = ""
        # set SP to 256
        output += "@256\nD=A\n@SP\nM=D\n"
        self.outputFile.write(output)
        # call Sys.init
        self.writeCall("Sys.init", 0)

    # writes the assembly for all the arithmetic commands
    def writeArithmetic(self, command):
        output = ""
        # get which operator should be used on x/y
        operator = self.arithmeticMap[command]

        # operations that use x and y
        if command in ["add", "sub", "eq", "gt", "lt", "and", "or"]:
            # store y in R13
            output += self.load_stack_head_to_D
            output += "@R13\nM=D\n"

            # store X in R14
            output += self.load_stack_head_to_D
            output += "@R14\nM=D\n"

            # perform the correct operation on R13 and R14 and store the result in D
            output += "@R14\nD=M\n@R13\nM=D" + operator + "M\n@R13\nD=M\n"

        # operations that only use y
        elif command in ["neg", "not"]:
            # store get Y from stack and store the result of the correct operation in D
            output += self.load_stack_head_to_D
            output += "D=" + operator + "D\n"

        # logical stuff needs more commands for branching
        if command in ["eq", "gt", "lt"]:
            # get what logical jump directive we need
            logical = self.logicalMap[command]

            # create a tag for where to go if this comp is true
            output += "@True" + str(self.logicCounter) + "\n"

            # jump with correct directive
            output += "D;" + logical + "\n"

            # if we dont jump, set D to false and jump to the part that sets the stack
            output += "@0\nD=A\n"
            output += "@Continue" + str(self.logicCounter) + "\n"
            output += "0;JMP\n"

            # if true, set D to 0
            output += "(True" + str(self.logicCounter) + ")\n@0\nD=!A\n"

            # this part is run no matter what (this tag holds the push T/F to stack, which is captured down there)
            output += "(Continue" + str(self.logicCounter) + ")\n"

            # increment logicCounter
            self.logicCounter += 1

        # always dump d to stack at the end (this is the down there part)
        output += self.push_d_to_stack

        # write to file
        self.outputFile.write(output)

    def writePushPop(self, command, segment, index):
        output = ""
        # push command
        if command == "C_PUSH":
            # constant
            if segment == "constant":
                # load the constant and store in D
                output += "@" + str(index) + "\nD=A\n"
                output += self.push_d_to_stack

            # static - uses the filname.index convention described in the book
            elif segment == "static":
                # get the @xxx.index label and does D=M
                output += "@" + \
                    self.filename.split(".")[0] + "." + str(index) + "\n"
                output += "D=M\n"
                output += self.push_d_to_stack

            # everything else
            else:
                # get the assembly tag for the segment we are trying to address
                memTag = self.memoryMap[segment]

                # get the segment and store in D
                output += "@" + memTag + "\n"

                # if we want pointer or temp, we store the A register in D, since pointer and temp refer to constants 3 and 5
                if segment in ["pointer", "temp"]:
                    output += "D=A\n"
                # if we have anything else, we store the M register in D, since all other segments are stored in the memory of their @tag
                else:
                    output += "D=M\n"

                # get the constant for index and add to D, storing in A register (essentially doing the pointer math we need)
                output += "@" + str(index) + "\n"
                output += "A=D+A\n"

                # set D to Memory[A](the memory location of the index of the segment we want to access)
                output += "D=M\n"

                # push d to the stack to move the memory onto the stack
                output += self.push_d_to_stack
        # pop command
        elif command == "C_POP":
            # get the correct @tag
            # static needs the filename.index convention
            if segment == "static":
                memTag = self.filename.split(".")[0] + "." + str(index)
            else:
                # everything else just uses the assembly reserved words
                memTag = self.memoryMap[segment]

            # get the value of the segment tag and store in D
            output += "@" + memTag + "\n"

            # if we have pointer, temp, or static, set D to A since we want the constant from the @ tag
            if segment in ["pointer", "temp", "static"]:
                output += "D=A\n"
            else:
                # everything else set D to M since we want the memory location stored in the segment tag
                output += "D=M\n"

            # only do the pointer math if we aren't using segment
            if segment != "static":
                # get the constant for index and add to D, storing in D regiter
                output += "@" + str(index) + "\n"
                output += "D=D+A\n"

            # store D (address we want to pop to) for later
            output += "@R13\n"
            output += "M=D\n"

            # set D to stack head, get r13 memory value (the address we want to pop to) and store it in A
            # when we do the final M=D, we set Memory[address we want to pop to] = D (the value from the top of the stack)
            output += self.load_stack_head_to_D
            output += "@R13\nA=M\nM=D\n"

        # write the assembly to the output file
        self.outputFile.write(output)

    # writes a label - just writes (label) to file
    def writeLabel(self, label):
        output = ""
        output += "(" + label + ")\n"

        self.outputFile.write(output)

    # writes the assembly to jump to a label
    def writeGoto(self, label):
        output = ""
        # get label
        output += "@" + label + "\n"
        # jump to it
        output += "0;JMP\n"

        self.outputFile.write(output)

    # pops the topmost value from the stack and jumps to label if that value is not 0
    def writeIf(self, label):
        output = ""
        # pop from stack to check if 0
        output += self.load_stack_head_to_D
        # get label
        output += "@" + label + "\n"
        # if D is not 0, jump to label
        output += "D;JNE\n"

        self.outputFile.write(output)

    # creates a label for the function, then pushes numArgs 0s to the stack
    def writeFunction(self, functionName, numLocals):
        # write the function label
        self.writeLabel(functionName)
        # push the locals
        for i in range(numLocals):
            self.writePushPop("C_PUSH", "constant", 0)

    # writes the call function protocol in chapter 8
    def writeCall(self, functionName, numArgs):
        output = ""
        # create return address label
        return_address = functionName + "-return-" + str(self.labelCounter)
        self.labelCounter += 1

        # push return_address
        output += "@" + return_address + "\nD=A\n" + self.push_d_to_stack

        # push LCL
        output += "@LCL\nD=M\n" + self.push_d_to_stack

        # push ARG
        output += "@ARG\nD=M\n" + self.push_d_to_stack

        # push THIS
        output += "@THIS\nD=M\n" + self.push_d_to_stack

        # push THAT
        output += "@THAT\nD=M\n" + self.push_d_to_stack

        # reposition ARG
        # get SP
        output += "@SP\nD=M\n"
        # sub n
        output += "@" + str(numArgs) + "\nD=D-A\n"
        # sub 5
        output += "@5\nD=D-A\n"
        # set ARG to D
        output += "@ARG\nM=D\n"

        # reposition LCL
        output += "@SP\nD=M\n@LCL\nM=D\n"

        # goto f
        output += "@" + functionName + "\n0;JMP\n"

        # (return-address)
        output += "(" + return_address + ")\n"

        self.outputFile.write(output)

    # writes the return from function protocol described in chapter 8
    def writeReturn(self):
        output = ""
        # FRAME = LCL
        output += "@LCL\nD=M\n@FRAME\nM=D\n"

        # RET=*(FRAME-5)
        # get frame
        output += "@FRAME\nD=M\n"
        # sub 5
        output += "@5\nD=D-A\n"
        # get Memory[FRAME - 5]
        output += "A=D\nD=M\n"
        # store in RET
        output += "@RET\nM=D\n"

        # *ARG=pop()
        # pop top value of stack
        output += self.load_stack_head_to_D
        # store in ARG
        output += "@ARG\nA=M\nM=D\n"

        # SP=ARG+1
        # get ARG
        output += "@ARG\n"
        # add 1
        output += "D=M+1\n"
        # store in SP
        output += "@SP\nM=D\n"

        # THAT=*(FRAME-1)
        # load frame
        output += "@FRAME\n"
        # sub 1
        output += "A=M-1\n"
        # store in THAT
        output += "D=M\n@THAT\nM=D\n"

        # THIS=*(FRAME-2)
        # sub 2 from FRAME
        output += "@2\nD=A\n@FRAME\nD=M-D\n"
        # do the pointer dereference
        output += "A=D\nD=M\n"
        # store in THIS
        output += "@THIS\nM=D\n"

        # ARG=*(FRAME-3)
        # sub 3 from FRAME
        output += "@3\nD=A\n@FRAME\nD=M-D\n"
        # do pointer dereference
        output += "A=D\nD=M\n"
        # store in ARG
        output += "@ARG\nM=D\n"

        # LCL=*(FRAME-4)
        # sub 4 from FRAME
        output += "@4\nD=A\n@FRAME\nD=M-D\n"
        # do pointer dereference
        output += "A=D\nD=M\n"
        # store in LCL
        output += "@LCL\nM=D\n"

        # goto RET
        output += "@RET\nA=M\n0;JMP\n"

        self.outputFile.write(output)

    # closes output file
    def close(self):
        self.outputFile.close()
