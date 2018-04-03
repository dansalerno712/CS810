import sys
from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable

# for compiling expressions
op = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
unaryOp = ["-", "~"]
KeyWordConstant = ["true", "false", "null", "this"]


class CompilationEngine(object):
    """This class recursively compiles a .jack file into vm code."""

    def __init__(self, inFile):
        super(CompilationEngine, self).__init__()
        # create an internal tokenizer to iterate through
        self.tokenizer = JackTokenizer(inFile)

        # setup the output file
        self.outputPath = inFile.name.replace(".jack", ".vm")
        self.outputFile = open(self.outputPath, 'w')
        self.outputFile.close()
        self.outputFile = open(self.outputPath, 'a')

        # create a VMWriter with the output file
        self.vmWriter = VMWriter(self.outputFile)

        # create a symbol table
        self.symbolTable = SymbolTable()

        # stuff we need to keep track of for the symbol table
        self.className = ""
        self.currentName = ""
        self.currentKind = ""
        self.currentType = ""
        self.ifCounter = 0
        self.whileCounter = 0

    def start(self):
        """Starts the compilation by creating the token XML file
        and then calling __compileClass()"""

        # start the tokenizer
        self.tokenizer.advance()

        # start the compilation
        self.__compileClass()

    def __checkIdentifier(self):
        """Makes sure that the current token is an identifier and saves that
        identifier as the current name for the symbol table"""
        if self.tokenizer.tokenType() == "IDENTIFIER":
            self.currentName = self.tokenizer.identifier()
            return True
        return False

    def __checkType(self):
        """Checks for a valid type and saves that type for the symbol table"""
        if self.tokenizer.tokenType() == "KEYWORD" and \
                self.tokenizer.keyWord() in ["int", "char", "boolean", "void"]:
            self.currentType = self.tokenizer.keyWord()
            return True
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            self.currentType = self.tokenizer.identifier()
            return True
        else:
            return False

    def __compileType(self):
        """Compiles a complete jack type grammar. Returns false if there is an error"""
        # check for valid keyword
        if self.tokenizer.tokenType() == "KEYWORD":
            k = self.tokenizer.keyWord()
            if k not in ["int", "char", "boolean"]:
                print("Error: type keyword must be int, char, or boolean")
                return False

            # self.__writeFullTag("keyword", k)

            self.tokenizer.advance()
            return True
        # check for className
        else:
            res = self.__compileClassName()
            # if __compileClassName() errors, this is not a valid type
            if not res:
                print("Error: type not a valid className")
            return res

    def __compileClassName(self):
        """Compiles a complete jack className grammar. Returns false if there is
        an error"""
        if self.tokenizer.tokenType() != "IDENTIFIER":
            return False

        # self.__writeFullTag("identifier", self.tokenizer.identifier())

        self.tokenizer.advance()
        return True

    def __compileSubroutineName(self):
        """Compiles a complete jack subroutineName. Returns false if there is an
        error"""
        if self.tokenizer.tokenType() != "IDENTIFIER":
            return False

        # self.__writeFullTag("identifier", self.tokenizer.identifier())

        self.tokenizer.advance()
        return True

    def __compileVarName(self):
        """Compiles a complete jack varName. Returns false if there is an
        error"""
        if self.tokenizer.tokenType() != "IDENTIFIER":
            return False

        # self.__writeFullTag("identifier", self.tokenizer.identifier())

        self.tokenizer.advance()
        return True

    def __compileClass(self):
        """Compiles a complete jack class grammar"""
        # find the class keyword
        if self.tokenizer.tokenType() != "KEYWORD" or \
                self.tokenizer.keyWord() != "class":
            print("Error: no class declaration found")
            sys.exit(1)

        self.tokenizer.advance()

        # find the className
        if not self.__checkIdentifier():
            print("Error: no class name found in class declaration")
            sys.exit(1)
        # save the class name
        self.className = self.tokenizer.identifier()
        self.tokenizer.advance()

        # find the open curly brace
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "{":
            print("Error: no opening brace found after class")
            sys.exit(0)
        self.tokenizer.advance()

        # compile the classVarDecs
        while(self.tokenizer.tokenType() == "KEYWORD" and
              (self.tokenizer.keyWord() == "static" or
               self.tokenizer.keyWord() == "field")):
            self.__compileClassVarDec()

        # compile the subroutines
        while(self.tokenizer.tokenType() == "KEYWORD" and
              (self.tokenizer.keyWord() == "constructor" or
               self.tokenizer.keyWord() == "function" or
               self.tokenizer.keyWord() == "method")):
            self.__compileSubroutineDec()

        # find last curly brace
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "}":
            print("Error: no closing brace found after class definition")
            sys.exit(1)
        self.tokenizer.advance()

    def __compileClassVarDec(self):
        """Compiles a complete jack class variable declaration. This advances the
        tokenizer completely through the variable declaration"""
        # we already checked to make sure that the keyword is valid
        self.currentKind = self.tokenizer.keyWord()
        self.tokenizer.advance()

        # look for a valid type
        if not self.__checkType():
            print("Error: invalid type in classVarDec")
            sys.exit(1)
        self.tokenizer.advance()

        # check for varName
        if self.__checkIdentifier():
            self.symbolTable.define(
                self.currentName, self.currentType, self.currentKind)
            self.tokenizer.advance()
        else:
            print("Error: missing varName identifier in classVarDec")
            sys.exit(1)

        # check for comma then more varNames (possible not existing)
        while self.tokenizer.tokenType() == "SYMBOL" and \
                self.tokenizer.symbol() == ",":
            self.tokenizer.advance()

            # check for varName again
            if self.__checkIdentifier():
                self.symbolTable.define(
                    self.currentName, self.currentType, self.currentKind)
                self.tokenizer.advance()
            else:
                print("Error: missing varName identifier in classVarDec")
                sys.exit(1)

        # check for closing semicolon
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            print("Error: missing semicolon after classVarDec")
            sys.exit(1)
        self.tokenizer.advance()

    def __compileSubroutineDec(self):
        """Compiles a complete jack subroutine description. This advances the
        tokenizer completely through the subroutine declaration"""
        # clear the subroutine symbol table
        self.symbolTable.startSubroutine()

        # since we already checked for the subroutine kind, grab it
        subroutineKind = self.tokenizer.keyWord()
        self.tokenizer.advance()

        # look for return type
        if not self.__checkType():
            print("Error: illegal return type for subroutine")
            sys.exit(1)
        self.tokenizer.advance()

        # check for subroutineName and save it with the specified format
        if self.__checkIdentifier():
            currentSubroutineName = self.className + "." + self.currentName
            self.tokenizer.advance()
        else:
            print("Error: missing subroutineName in subroutineDec")
            sys.exit(1)

        # if the subroutine is a method, the first arg needs to be this
        if subroutineKind == "method":
            self.symbolTable.define("this", self.className, "arg")

        # check for open parentheses
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "(":
            print("Error: missing ( for parameter list")
            sys.exit(1)
        self.tokenizer.advance()

        # do parameter list (this could add nothing)
        self.__compileParameterList()

        # check for closing parentheses
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
            print("Error: missing ) for parameter list")
            sys.exit(1)
        self.tokenizer.advance()

        # compile subroutine body
        self.__compileSubroutineBody(subroutineKind, currentSubroutineName)

    def __compileParameterList(self):
        """Compiles a complete jack parameter list grammar"""
        # we know all parameter lists are arguments, so set the current kind
        self.currentKind = "arg"

        # if the next symbol is a ), then there is no parameter list, so just return
        # the rest of compileSubroutine will handle writing that
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ")":
            return
        # look for a valid type
        else:
            if not self.__checkType():
                print("Error: invalid type in parameter list")
                sys.exit(1)
            self.tokenizer.advance()

            # check for varName
            if self.__checkIdentifier():
                self.symbolTable.define(
                    self.currentName, self.currentType, self.currentKind)
                self.tokenizer.advance()
            else:
                print("Error: missing varName identifier in parameterList")
                sys.exit(1)

            # check for comma separated list of type and varName
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                # write the comma
                self.tokenizer.advance()

                # look for a valid type
                if not self.__checkType():
                    print("Error: invalid type in parameter list")
                    sys.exit(1)
                self.tokenizer.advance()

                # check for varName
                if self.__checkIdentifier():
                    self.symbolTable.define(
                        self.currentName, self.currentType, self.currentKind)
                    self.tokenizer.advance()
                else:
                    print("Error: missing varName identifier in parameterList")
                    sys.exit(1)

    def __compileSubroutineBody(self, currentSubKind, currentSubName):
        """Compile a complete jack subroutine body grammar"""
        # check for {
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "{":
            print("Error: missing { for subroutine body")
            sys.exit(1)
        self.tokenizer.advance()

        # check to see if we need to compile varDec
        while self.tokenizer.tokenType() == "KEYWORD" and \
                self.tokenizer.keyWord() == "var":
            self.__compileVarDec()

        # write the function
        self.vmWriter.writeFunction(
            currentSubName, self.symbolTable.varCount("var"))

        # write stuff for constructor
        if currentSubKind == "constructor":
            # get number of class fields to allocate space for them
            numFields = self.symbolTable.varCount("field")
            if numFields > 0:
                self.vmWriter.writePush("constant", numFields)
            self.vmWriter.writeCall("Memory.alloc", 1)
            self.vmWriter.writePop("pointer", 0)
        # write stuff for method
        elif currentSubKind == "method":
            # get the this pointer
            self.vmWriter.writePush("argument", 0)
            self.vmWriter.writePop("pointer", 0)

        # compile statements
        self.__compileStatements()

        # check for closing }
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "}":
            print("Error: missing closing } for subroutine body")
            sys.exit(1)
        self.tokenizer.advance()

        return

    def __compileVarDec(self):
        """Compiles a complete jack varDec grammar"""
        # all var decs are of type var, so set it
        self.currentKind = "var"

        self.tokenizer.advance()

        # check for type
        if not self.__checkType():
            print("Error: invalid type in var dec")
            sys.exit(1)
        self.tokenizer.advance()

        # check for varName
        if self.__checkIdentifier():
            self.symbolTable.define(
                self.currentName, self.currentType, self.currentKind)
            self.tokenizer.advance()
        else:
            print("Error: missing varName identifier in varDec")
            sys.exit(1)

        # check for comma separated list of type and varName
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
            # write the comma
            self.tokenizer.advance()

            # check for varName
            if self.__checkIdentifier():
                self.symbolTable.define(
                    self.currentName, self.currentType, self.currentKind)
                self.tokenizer.advance()
            else:
                print("Error: missing varName identifier in varDec")
                sys.exit(1)

        # check for semicolon
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            print("Error: missing ; after varDec")
            sys.exit(1)
        self.tokenizer.advance()

        return

    def __compileStatements(self):
        """Compiles a complete jack statements grammar"""
        # check for the keywords for all the statements
        while self.tokenizer.tokenType() == "KEYWORD":
            k = self.tokenizer.keyWord()

            if k == "let":
                self.__compileLetStatement()
            elif k == "if":
                self.__compileIfStatement()
            elif k == "while":
                self.__compileWhileStatement()
            elif k == "do":
                self.__compileDoStatement()
            elif k == "return":
                self.__compileReturnStatement()
            else:
                print("Error: invalid statment " + k)
                sys.exit(1)

    def __compileLetStatement(self):
        """Compiles a complete jack let statment grammar"""
        self.tokenizer.advance()

        # look for varName
        if not self.__checkIdentifier():
            print("Error: missing varName for let statement")
        self.tokenizer.advance()

        # get values from symbol table
        varName = self.currentName
        kind = self.symbolTable.kindOf(varName)
        varType = self.symbolTable.typeOf(varName)
        index = self.symbolTable.indexOf(varName)
        isArray = False

        # check for [
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "[":
            isArray = True
            self.tokenizer.advance()

            # compile expression
            self.__compileExpression()

            # get the index from the top of the stack from compileExpression
            self.vmWriter.writePush(kind, index)
            self.vmWriter.writeArithmetic("add")
            self.vmWriter.writePop("temp", 2)

            # write the closing bracket
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "]":
                print("Error: missing closing ] in let statement")
                sys.exit(1)
            self.tokenizer.advance()

        # check for =
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "=":
            print("Error: missing = in let expression")
            sys.exit(1)
        self.tokenizer.advance()

        # compile expression
        self.__compileExpression()

        # write code to pop since expression puts result on top of stack
        if isArray:
            self.vmWriter.writePush("temp", 2)
            self.vmWriter.writePop("pointer", 1)
            self.vmWriter.writePop("that", 0)
        else:
            self.vmWriter.writePop(kind, index)

        # look for ;
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            print("Error: missing ; after let statement")
            sys.exit(1)
        self.tokenizer.advance()

    def __compileIfStatement(self):
        """Compiles a complete jack if statement grammar"""
        # setup local counter
        localIfCounter = self.ifCounter
        self.ifCounter += 1

        self.tokenizer.advance()

        # check for (
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "(":
            print("Error: missing ( in if statement")
            sys.exit(1)
        self.tokenizer.advance()

        # compile expression
        self.__compileExpression()

        # get the ~ if part from the stack
        self.vmWriter.writeArithmetic("not")

        # check for )
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
            print("Error: missing ) in if statement")
            sys.exit(1)
        self.tokenizer.advance()

        # check for {
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "{":
            print("Error: missing { for if statement")
            sys.exit(1)
        self.tokenizer.advance()

        # write the if for L1
        self.vmWriter.writeIf("if-false", localIfCounter)

        # compile more statements
        self.__compileStatements()

        # write the goto for L2
        self.vmWriter.writeGoto("if-true", localIfCounter)

        # check for }
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "}":
            print("Error: missing } after if statement")
            sys.exit(1)
        self.tokenizer.advance()

        # write label for L1
        self.vmWriter.writeLabel("if-false", localIfCounter)

        # check for else
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyWord() == "else":
            self.tokenizer.advance()

            # check for {
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "{":
                print("Error: missing { for if statement")
                sys.exit(1)
            self.tokenizer.advance()

            # compile more statements
            self.__compileStatements()

            # check for }
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "}":
                print("Error: missing } after if statement")
                sys.exit(1)
            self.tokenizer.advance()

        # write label for L2
        self.vmWriter.writeLabel("if-true", localIfCounter)

    def __compileWhileStatement(self):
        """Compiles a complete jack while statement grammar"""
        # get counter and write label for L1
        localWhileCounter = self.whileCounter
        self.whileCounter += 1
        self.vmWriter.writeLabel("whileStart", localWhileCounter)

        self.tokenizer.advance()

        # check for (
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "(":
            print("Error: missing ( in if statement")
            sys.exit(1)
        self.tokenizer.advance()

        # compile expression
        self.__compileExpression()

        # get ~cond from stack
        self.vmWriter.writeArithmetic("not")

        # check for )
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
            print("Error: missing ) in if statement")
            sys.exit(1)
        self.tokenizer.advance()

        # check for {
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "{":
            print("Error: missing { for if statement")
            sys.exit(1)
        self.tokenizer.advance()

        # write the if for L2
        self.vmWriter.writeIf("whileEnd", localWhileCounter)

        # compile more statements
        self.__compileStatements()

        # write the goto for L1
        self.vmWriter.writeGoto("whileStart", localWhileCounter)

        # check for }
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "}":
            print("Error: missing } after if statement")
            sys.exit(1)
        self.tokenizer.advance()

        # write the label for L2
        self.vmWriter.writeLabel("whileEnd", localWhileCounter)

    def __compileDoStatement(self):
        """Compiles a complete jack do statement grammar"""
        self.tokenizer.advance()

        # compile subroutine call
        if self.__checkIdentifier():
            firstHalf = self.currentName
            self.tokenizer.advance()
            if self.tokenizer.tokenType() == "SYMBOL" and (self.tokenizer.symbol() == "."
                                                           or self.tokenizer.symbol() == "("):
                self.__compileSubroutineCall(firstHalf)

        # check for semicolon
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            print("Error: missing ; after do statement")
            sys.exit(1)
        self.tokenizer.advance()

        # pop the 0 from the return
        self.vmWriter.writePop("temp", 0)

    def __compileReturnStatement(self):
        """Compiles a complete jack return statement grammar"""
        self.tokenizer.advance()

        # if the next symbol isn't a symbol, it must be an expression
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            self.__compileExpression()

            # write ;, checking again to make sure after calling compile expression
            # that the next symbol is still a valid ;
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
                print("Error: missing ; after return statement")
                sys.exit(1)
        else:
            # write the return of 0
            self.vmWriter.writePush("constant", 0)

        self.tokenizer.advance()
        # write the return
        self.vmWriter.writeReturn()

    def __convertOp(self, op):
        """Converts the operators that interfere with xml tags to their properly
        escaped versions"""
        op = op.replace("&", "&amp;")
        op = op.replace("<", "&lt;")
        op = op.replace(">", "&gt;")
        op = op.replace("\"", "&quot;")

        return op

    def __compileExpression(self):
        """Compiles a complete jack expression grammar"""
        # compile term
        self.__compileTerm()

        # check for op
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in op:
            s = self.tokenizer.symbol()

            self.tokenizer.advance()

            # compile another term
            self.__compileTerm()

            # write op vm code
            if s == "+":
                self.vmWriter.writeArithmetic("add")
            elif s == "-":
                self.vmWriter.writeArithmetic("sub")
            elif s == "*":
                self.vmWriter.writeCall("Math.multiply", 2)
            elif s == "/":
                self.vmWriter.writeCall("Math.divide", 2)
            elif s == "&":
                self.vmWriter.writeArithmetic("and")
            elif s == "|":
                self.vmWriter.writeArithmetic("or")
            elif s == "<":
                self.vmWriter.writeArithmetic("lt")
            elif s == ">":
                self.vmWriter.writeArithmetic("gt")
            elif s == "=":
                self.vmWriter.writeArithmetic("eq")

    def __compileTerm(self):
        """Compiles a complete jack term grammar"""
        # term logic
        # check for integerConstant
        if self.tokenizer.tokenType() == "INT_CONST":
            self.vmWriter.writePush("constant", self.tokenizer.intVal())
            self.tokenizer.advance()
        # check for string constant
        elif self.tokenizer.tokenType() == "STRING_CONST":
            # need to make a string constant
            string = self.tokenizer.stringVal()

            # push the length of the string
            self.vmWriter.writePush("constant", len(string))

            # call String.new 1
            self.vmWriter.writeCall("String.new", 1)

            # append to create the string
            for letter in string:
                self.vmWriter.writePush("constant", ord(letter))
                self.vmWriter.writeCall("String.appendChar", 2)

            self.tokenizer.advance()
        # check for keyword for KeywordConstant
        elif self.tokenizer.tokenType() == "KEYWORD":
            k = self.tokenizer.keyWord()

            if k not in KeyWordConstant:
                print("Error: invalid KeyWordConstant" + k + " in term")
                sys.exit(1)

            # write the outputs for the keyword constants
            if k == "null" or k == "false":
                self.vmWriter.writePush("constant", 0)
            elif k == "true":
                self.vmWriter.writePush("constant", 1)
                self.vmWriter.writeArithmetic("neg")
            elif k == "this":
                self.vmWriter.writePush("pointer", 0)

            self.tokenizer.advance()
        # check for symbol for either ( expression ) or unary op
        elif self.tokenizer.tokenType() == "SYMBOL":
            s = self.tokenizer.symbol()

            # ( expression )
            if s == "(":
                self.tokenizer.advance()

                # compile expression
                self.__compileExpression()

                # check for )
                if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
                    print("Error: missing ) after expression in term")
                    sys.exit(1)
                self.tokenizer.advance()
            # unaryOp term
            elif s in unaryOp:
                self.tokenizer.advance()

                # compile term
                self.__compileTerm()

                # write the unary output
                if s == "-":
                    self.vmWriter.writeArithmetic("neg")
                else:
                    self.vmWriter.writeArithmetic("not")
            else:
                print("Error: invalid symbol " + s + " in term")
                sys.exit(1)
        # check for varName | varName [ expression ] | subroutineCall
        elif self.__checkIdentifier():
            # advance the tokenizer one more step to check for [, (, or other
            self.tokenizer.advance()
            firstHalf = self.currentName

            if self.tokenizer.tokenType() == "SYMBOL":
                s = self.tokenizer.symbol()

                # varName[expression]
                if s == "[":
                    # push the array address
                    self.vmWriter.writePush(self.symbolTable.kindOf(firstHalf),
                                            self.symbolTable.indexOf(firstHalf))

                    # write [
                    self.tokenizer.advance()

                    # compile expression
                    self.__compileExpression()

                    # write vm code for array expression
                    self.vmWriter.writeArithmetic("add")
                    self.vmWriter.writePop("pointer", 1)
                    self.vmWriter.writePush("that", 0)

                    # write ]
                    if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "]":
                        print("Error: missing ] after varName[expression]")
                        sys.exit(1)
                    self.tokenizer.advance()
                # subroutineCall
                elif s == "(" or s == ".":
                    # compile subroutineCall
                    self.__compileSubroutineCall(firstHalf)
                else:
                    self.vmWriter.writePush(self.symbolTable.kindOf(self.currentName),
                                            self.symbolTable.indexOf(self.currentName))
            else:
                self.vmWriter.writePush(self.symbolTable.kindOf(self.currentName),
                                        self.symbolTable.indexOf(self.currentName))
        else:
            print("Error: invalid term")
            sys.exit(1)

    def __compileSubroutineCall(self, firstHalf):
        """Compiles a complete jack subroutine call grammar"""
        # look ahead one token to see if it is a ( or a .
        isClass = firstHalf[0].isupper()
        fullSubroutineName = ""
        nArgs = 0

        # subroutineName
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "(":
            fullSubroutineName = self.className + "." + firstHalf
            # since this a self method, we need to push pointer
            self.vmWriter.writePush("pointer", 0)
            self.tokenizer.advance()

            # compile expression list
            nArgs = self.__compileExpressionList(isClass)

            # check for )
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
                print("Error: missing ) after expressionList in subroutineCall")
                sys.exit(1)
            self.tokenizer.advance()
        # className | varName
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ".":
            self.tokenizer.advance()
            if self.__checkIdentifier():
                if isClass:
                    fullSubroutineName = firstHalf + "." + self.currentName
                else:
                    fullSubroutineName = self.symbolTable.typeOf(
                        firstHalf) + "." + self.currentName
                    # push the address of firstHalf
                    self.vmWriter.writePush(self.symbolTable.kindOf(
                        firstHalf), self.symbolTable.indexOf(firstHalf))
            else:
                print("Error: missing varName|className in subroutineCall")

            # check for (
            self.tokenizer.advance()
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "(":
                print("Error: missing ( in subroutineCall before expressionList")
                sys.exit(1)
            self.tokenizer.advance()

            # compile expression list
            nArgs = self.__compileExpressionList(isClass)

            # check for )
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
                print("Error: missing ) after expressionList in subroutineCall")
                sys.exit(1)
            self.tokenizer.advance()
        else:
            print("Error: invalid subroutineCall")
            sys.exit(1)

        if fullSubroutineName != "":
            self.vmWriter.writeCall(fullSubroutineName, nArgs)

    def __compileExpressionList(self, isClass):
        """Compiles a complete jack expression list grammar"""
        # if the symbol is ), there is no expression list
        if isClass:
            argCounter = 0
        else:
            argCounter = 1

        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ")":
            return argCounter
        else:
            # compile expression
            self.__compileExpression()

            argCounter += 1

            # loop until you dont see a comma
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.tokenizer.advance()

                # compile expression
                self.__compileExpression()

                argCounter += 1

            return argCounter
