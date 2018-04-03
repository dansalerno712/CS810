import sys
from JackTokenizer import JackTokenizer

# for compiling expressions
op = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
unaryOp = ["-", "~"]
KeyWordConstant = ["true", "false", "null", "this"]


class CompilationEngine(object):
    """This class recursively compiles a .jack file into (eventually) vm code.
    For now, this just outputs a grammar xml file"""

    def __init__(self, inFile):
        super(CompilationEngine, self).__init__()
        # create an internal tokenizer to iterate through
        self.tokenizer = JackTokenizer(inFile)

        # spacing so I can make nicely formatted xml, this will increase by
        # 4 spaces every time I recurse
        self.spacing = ""

        # setup the output file
        self.outputPath = inFile.name.replace(".jack", ".xml")
        self.outputFile = open(self.outputPath, 'w')
        self.outputFile.close()
        self.outputFile = open(self.outputPath, 'a')

    def __increaseSpacing(self):
        """Adds 2 spaces to self.spacing"""
        self.spacing += "  "

    def __decreaseSpacing(self):
        """Removes 2 spaces from self.spacing"""
        self.spacing = self.spacing[:-2]

    def __writeFullTag(self, tag, value):
        """Writes the spacing, then <tag> value </tag> to the output file"""
        self.outputFile.write(self.spacing + "<" + tag +
                              "> " + value + " </" + tag + ">\n")

    def __writeOpenTag(self, tag):
        """Writes spacing, then <tag>, then increases the spacing"""
        self.outputFile.write(self.spacing + "<" + tag + ">\n")
        self.__increaseSpacing()

    def __writeCloseTag(self, tag):
        """Decreases spacing, then writes spacing, then </tag>"""
        self.__decreaseSpacing()
        self.outputFile.write(self.spacing + "</" + tag + ">\n")

    def start(self):
        """Starts the compilation by creating the token XML file
        and then calling __compileClass()"""

        # start the tokenizer
        self.tokenizer.advance()

        # make token xml file
        self.__createTokenXML()

        # reset tokenizer and compile
        self.tokenizer.reset()
        self.tokenizer.advance()
        self.__compileClass()

    def __createTokenXML(self):
        """Creates the token XML file for a .jack file"""
        outputPath = self.outputPath.replace(".xml", "T.xml")
        f = open(outputPath, 'w')
        f.close()
        f = open(outputPath, 'a')
        f.write("<tokens>\n")
        # make an output file that is filename but with testXML.xml at end
        while self.tokenizer.hasMoreTokens():
            # output to xml to check
            tokenType = self.tokenizer.tokenType()
            if tokenType == "KEYWORD":
                f.write("<keyword>" + self.tokenizer.keyWord() + "</keyword>\n")
            elif tokenType == "SYMBOL":
                symbol = self.tokenizer.symbol()
                symbol = symbol.replace("&", "&amp;")
                symbol = symbol.replace("<", "&lt;")
                symbol = symbol.replace(">", "&gt;")
                symbol = symbol.replace("\"", "&quot;")
                f.write("<symbol>" + symbol + "</symbol>\n")
            elif tokenType == "IDENTIFIER":
                f.write("<identifier>" +
                        self.tokenizer.identifier() + "</identifier>\n")
            elif tokenType == "INT_CONST":
                f.write("<integerConstant>" +
                        self.tokenizer.intVal() + "</integerConstant>\n")
            elif tokenType == "STRING_CONST":
                f.write("<stringConstant>" +
                        self.tokenizer.stringVal() + "</stringConstant>\n")

            self.tokenizer.advance()

        # close the xml tag
        f.write("</tokens>")

    def __compileType(self):
        """Compiles a complete jack type grammar. Returns false if there is an error"""
        # check for valid keyword
        if self.tokenizer.tokenType() == "KEYWORD":
            k = self.tokenizer.keyWord()
            if k not in ["int", "char", "boolean"]:
                print("Error: type keyword must be int, char, or boolean")
                return False
            self.__writeFullTag("keyword", k)
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
        self.__writeFullTag("identifier", self.tokenizer.identifier())
        self.tokenizer.advance()
        return True

    def __compileSubroutineName(self):
        """Compiles a complete jack subroutineName. Returns false if there is an
        error"""
        if self.tokenizer.tokenType() != "IDENTIFIER":
            return False
        self.__writeFullTag("identifier", self.tokenizer.identifier())
        self.tokenizer.advance()
        return True

    def __compileVarName(self):
        """Compiles a complete jack varName. Returns false if there is an
        error"""
        if self.tokenizer.tokenType() != "IDENTIFIER":
            return False
        self.__writeFullTag("identifier", self.tokenizer.identifier())
        self.tokenizer.advance()
        return True

    def __compileClass(self):
        """Compiles a complete jack class grammar"""
        # find the class keyword
        if self.tokenizer.tokenType() != "KEYWORD" or \
                self.tokenizer.keyWord() != "class":
            print("Error: no class declaration found")
            sys.exit(1)
        # write both the class tag and the keyword tag for class
        self.__writeOpenTag("class")
        self.__writeFullTag("keyword", self.tokenizer.keyWord())
        self.tokenizer.advance()

        # find the className
        if not self.__compileClassName():
            print("Error: no class name found in class declaration")
            sys.exit(1)

        # find the open curly brace
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "{":
            print("Error: no opening brace found after class")
            sys.exit(0)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
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
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # close class tag
        self.__writeCloseTag("class")
        self.tokenizer.advance()

    def __compileClassVarDec(self):
        """Compiles a complete jack class variable declaration. This advances the
        tokenizer completely through the variable declaration"""
        # since we already checked to make sure this is valid, we can write
        # the tag here and either static or filed
        self.__writeOpenTag("classVarDec")
        self.__writeFullTag("keyword", self.tokenizer.keyWord())
        self.tokenizer.advance()

        # look for a valid type
        if not self.__compileType():
            sys.exit(1)

        # check for varName
        if not self.__compileVarName():
            print("Error: missing varName identifier in classVarDec")
            sys.exit(1)

        # check for comma then more varNames (possible not existing)
        while self.tokenizer.tokenType() == "SYMBOL" and \
                self.tokenizer.symbol() == ",":
            # write the comma
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()

            # check for varName again
            if not self.__compileVarName():
                print("Error: missing varName identifier in classVarDec")
                sys.exit(1)

        # check for closing semicolon
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            print("Error: missing semicolon after classVarDec")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # close classVarDec tag
        self.__writeCloseTag("classVarDec")

    def __compileSubroutineDec(self):
        """Compiles a complete jack subroutine description. This advances the
        tokenizer completely through the subroutine declaration"""
        # write the opening tag
        self.__writeOpenTag("subroutineDec")
        # since we already checked for constructor/function/method, write it
        self.__writeFullTag("keyword", self.tokenizer.keyWord())
        self.tokenizer.advance()

        # look for void or type
        if self.tokenizer.tokenType() == "KEYWORD" and \
                self.tokenizer.keyWord() == "void":
            # if void, write it
            self.__writeFullTag("keyword", self.tokenizer.keyWord())
            self.tokenizer.advance()
        elif not self.__compileType():
            print("Error: subroutine return type not void or valid type")
            sys.exit(1)

        # check for subroutineName
        if not self.__compileSubroutineName():
            print("Error: missing subroutineName in subroutineDec")
            sys.exit(1)

        # check for open parentheses
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "(":
            print("Error: missing ( for parameter list")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # do parameter list (this could add nothing)
        self.__compileParameterList()

        # check for closing parentheses
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
            print("Error: missing ) for parameter list")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # compile subroutine body
        self.__compileSubroutineBody()

        # close subroutineDec tag
        self.__writeCloseTag("subroutineDec")

    def __compileParameterList(self):
        """Compiles a complete jack parameter list grammar"""
        # write opening tag
        self.__writeOpenTag("parameterList")

        # if the next symbol is a ), then there is no parameter list, so just return
        # the rest of compileSubroutine will handle writing that
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ")":
            # close tag
            self.__writeCloseTag("parameterList")
            return
        # look for a valid type
        else:
            res = self.__compileType()
            if not res:
                sys.exit(1)

            # check for varName
            if not self.__compileVarName():
                print("Error: missing varName identifier in parameterList")
                sys.exit(1)

            # check for comma separated list of type and varName
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                # write the comma
                self.__writeFullTag("symbol", self.tokenizer.symbol())
                self.tokenizer.advance()

                # look for a valid type
                if not self.__compileType():
                    sys.exit(1)

                # check for varName
                if not self.__compileVarName():
                    print("Error: missing varName identifier in parameterList")
                    sys.exit(1)

            # write closing tag
            self.__writeCloseTag("parameterList")

    def __compileSubroutineBody(self):
        """Compile a complete jack subroutine body grammar"""
        # write opening tag
        self.__writeOpenTag("subroutineBody")

        # check for {
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "{":
            print("Error: missing { for subroutine body")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # check to see if we need to compile varDec
        while self.tokenizer.tokenType() == "KEYWORD" and \
                self.tokenizer.keyWord() == "var":
            self.__compileVarDec()

        # compile statements
        self.__compileStatements()

        # check for closing }
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "}":
            print("Error: missing closing } for subroutine body")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # close tag
        self.__writeCloseTag("subroutineBody")
        return

    def __compileVarDec(self):
        """Compiles a complete jack varDec grammar"""
        # write open tag
        self.__writeOpenTag("varDec")
        # since we already checked to make sure there is a var, write it
        self.__writeFullTag("keyword", self.tokenizer.keyWord())
        self.tokenizer.advance()

        # check for type
        if not self.__compileType():
            sys.exit(1)

        # check for varName
        if not self.__compileVarName():
            print("Error: missing varName identifier in varDec")
            sys.exit(1)

        # check for comma separated list of type and varName
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
            # write the comma
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()

            # check for varName
            if not self.__compileVarName():
                print("Error: missing varName identifier in varDec")
                sys.exit(1)

        # check for semicolon
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            print("Error: missing ; after varDec")
            sys.exit(1)
        # write ;
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # close tag
        self.__writeCloseTag("varDec")

        return

    def __compileStatements(self):
        """Compiles a complete jack statements grammar"""
        # write statements tag
        self.__writeOpenTag("statements")

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

        # close statements tag
        self.__writeCloseTag("statements")

    def __compileLetStatement(self):
        """Compiles a complete jack let statment grammar"""
        # write opening tag
        self.__writeOpenTag("letStatement")
        # since we already checked for the keyword let, write it
        self.__writeFullTag("keyword", self.tokenizer.keyWord())
        self.tokenizer.advance()

        # look for varName
        if not self.__compileVarName():
            print("Error: missing varName for let statement")

        # check for [
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "[":
            # write the bracket
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()

            # compile expression
            self.__compileExpression()

            # write the closing bracket
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "]":
                print("Error: missing closing ] in let statement")
                sys.exit(1)
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()

        # check for =
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "=":
            print("Error: missing = in let expression")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # compile expression
        self.__compileExpression()

        # look for ;
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            print("Error: missing ; after let statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # write closing tag
        self.__writeCloseTag("letStatement")

    def __compileIfStatement(self):
        """Compiles a complete jack if statement grammar"""
        # write opening tag
        self.__writeOpenTag("ifStatement")
        # since we already checked for if, write it
        self.__writeFullTag("keyword", self.tokenizer.keyWord())
        self.tokenizer.advance()

        # check for (
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "(":
            print("Error: missing ( in if statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # compile expression
        self.__compileExpression()

        # check for )
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
            print("Error: missing ) in if statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # check for {
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "{":
            print("Error: missing { for if statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # compile more statements
        self.__compileStatements()

        # check for }
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "}":
            print("Error: missing } after if statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # check for else
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyWord() == "else":
            # write else
            self.__writeFullTag("keyword", self.tokenizer.keyWord())
            self.tokenizer.advance()

            # check for {
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "{":
                print("Error: missing { for if statement")
                sys.exit(1)
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()

            # compile more statements
            self.__compileStatements()

            # check for }
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "}":
                print("Error: missing } after if statement")
                sys.exit(1)
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()

        # close tag
        self.__writeCloseTag("ifStatement")

    def __compileWhileStatement(self):
        """Compiles a complete jack while statement grammar"""
        # write opening tag
        self.__writeOpenTag("whileStatement")
        # since we checked for while already, write it
        self.__writeFullTag("keyword", self.tokenizer.keyWord())
        self.tokenizer.advance()

        # check for (
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "(":
            print("Error: missing ( in if statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # compile expression
        self.__compileExpression()

        # check for )
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
            print("Error: missing ) in if statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # check for {
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "{":
            print("Error: missing { for if statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # compile more statements
        self.__compileStatements()

        # check for }
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "}":
            print("Error: missing } after if statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # write closing tag
        self.__writeCloseTag("whileStatement")

    def __compileDoStatement(self):
        """Compiles a complete jack do statement grammar"""
        # write opening tag
        self.__writeOpenTag("doStatement")
        # since we already checked for do, write it
        self.__writeFullTag("keyword", self.tokenizer.keyWord())
        self.tokenizer.advance()

        # compile subroutine call
        self.__compileSubroutineCall()

        # check for semicolon
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            print("Error: missing ; after do statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # write closing tag
        self.__writeCloseTag("doStatement")

    def __compileReturnStatement(self):
        """Compiles a complete jack return statement grammar"""
        # write opening tag
        self.__writeOpenTag("returnStatement")
        # since we checked for return already, write it
        self.__writeFullTag("keyword", self.tokenizer.keyWord())
        self.tokenizer.advance()

        # if the next symbol isn't a symbol, it must be an expression
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            self.__compileExpression()

        # write ;, checking again to make sure after calling compile expression
        # that the next symbol is still a valid ;
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            print("Error: missing ; after return statement")
            sys.exit(1)
        self.__writeFullTag("symbol", self.tokenizer.symbol())
        self.tokenizer.advance()

        # write closing tag
        self.__writeCloseTag("returnStatement")

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
        # write opening tag
        self.__writeOpenTag("expression")

        # compile term
        self.__compileTerm()

        # check for op
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in op:
            s = self.tokenizer.symbol()

            # write op
            self.__writeFullTag("symbol", self.__convertOp(s))
            self.tokenizer.advance()

            # compile another term
            self.__compileTerm()

        # close tag
        self.__writeCloseTag("expression")

    def __compileTerm(self):
        """Compiles a complete jack term grammar"""
        # write opening tag
        self.__writeOpenTag("term")

        # term logic
        # check for integerConstant
        if self.tokenizer.tokenType() == "INT_CONST":
            self.__writeFullTag("integerConstant", self.tokenizer.intVal())
            self.tokenizer.advance()
        # check for string constant
        elif self.tokenizer.tokenType() == "STRING_CONST":
            self.__writeFullTag("stringConstant", self.tokenizer.stringVal())
            self.tokenizer.advance()
        # check for keyword for KeywordConstant
        elif self.tokenizer.tokenType() == "KEYWORD":
            k = self.tokenizer.keyWord()

            if k not in KeyWordConstant:
                print("Error: invalid KeyWordConstant" + k + " in term")
                sys.exit(1)

            # write the keywordconstant
            self.__writeFullTag("keyword", k)
            self.tokenizer.advance()
        # check for symbol for either ( expression ) or unary op
        elif self.tokenizer.tokenType() == "SYMBOL":
            s = self.tokenizer.symbol()

            # ( expression )
            if s == "(":
                self.__writeFullTag("symbol", s)
                self.tokenizer.advance()

                # compile expression
                self.__compileExpression()

                # check for )
                if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
                    print("Error: missing ) after expression in term")
                    sys.exit(1)
                self.__writeFullTag("symbol", self.tokenizer.symbol())
                self.tokenizer.advance()
            # unaryOp term
            elif s in unaryOp:
                self.__writeFullTag("symbol", s)
                self.tokenizer.advance()

                # compile term
                self.__compileTerm()
            else:
                print("Error: invalid symbol " + s + " in term")
                sys.exit(1)
        # check for varName | varName [ expression ] | subroutineCall
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            # advance the tokenizer one more step to check for [, (, or other
            self.tokenizer.advance()

            if self.tokenizer.tokenType() == "SYMBOL":
                s = self.tokenizer.symbol()

                # varName[expression]
                if s == "[":
                    # go back to varName
                    self.tokenizer.retreat()

                    # compile varName
                    if not self.__compileVarName():
                        print("Error: invalid varName in term")
                        sys.exit(1)

                    # write [
                    self.__writeFullTag("symbol", self.tokenizer.symbol())
                    self.tokenizer.advance()

                    # compile expression
                    self.__compileExpression()

                    # write ]
                    if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != "]":
                        print("Error: missing ] after varName[expression]")
                        sys.exit(1)
                    self.__writeFullTag("symbol", self.tokenizer.symbol())
                    self.tokenizer.advance()
                # subroutineCall
                elif s == "(" or s == ".":
                    # go back to subroutineName
                    self.tokenizer.retreat()

                    # compile subroutineCall
                    self.__compileSubroutineCall()
                else:
                    # go back to varName
                    self.tokenizer.retreat()

                    # compile varName
                    if not self.__compileVarName():
                        print("Error: invalid varName in term")
                        sys.exit(1)
            else:
                # go back to varName
                self.tokenizer.retreat()

                # compile varName
                if not self.__compileVarName():
                    print("Error: invalid varName in term")
                    sys.exit(1)
        else:
            print("Error: invalid term")
            sys.exit(1)

        # close tag
        self.__writeCloseTag("term")

    def __compileSubroutineCall(self):
        """Compiles a complete jack subroutine call grammar"""
        # look ahead one token to see if it is a ( or a .
        self.tokenizer.advance()

        # subroutineName
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "(":
            # go back to subroutine name
            self.tokenizer.retreat()

            # compile subroutine name
            if not self.__compileSubroutineName():
                print("Error: invalid subroutineName in subroutineCall")
                sys.exit(1)

            # check for (
            if self.tokenizer.tokenType() != "SYMBOL" and self.tokenizer.symbol() != "(":
                print("Error: missing ( in subroutineCall before expressionList")
                sys.exit(1)
            # write (
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()

            # compile expression list
            self.__compileExpressionList()

            # check for )
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
                print("Error: missing ) after expressionList in subroutineCall")
                sys.exit(1)
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()
        # className | varName
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ".":
            # go back to varName/className
            self.tokenizer.retreat()

            if self.tokenizer.tokenType() != "IDENTIFIER":
                print("Error: missing varName|className in subroutineCall")
            # Hacky, but className and varName both correspond to just an
            # identitifer, so I just call compileVarName to handle both
            if not self.__compileVarName():
                print("Error: invalid className or varName in subroutineCall")
                sys.exit(1)

            # check for .
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ".":
                print("Error: missing . in subroutineCall")
                sys.exit(1)
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()

            # compile subroutineName
            if not self.__compileSubroutineName():
                print("Error: missing subroutineName after . in subroutineCall")
                sys.exit(1)

            # check for (
            if self.tokenizer.tokenType() != "SYMBOL" and self.tokenizer.symbol() != "(":
                print("Error: missing ( in subroutineCall before expressionList")
                sys.exit(1)
            # write (
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()

            # compile expression list
            self.__compileExpressionList()

            # check for )
            if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
                print("Error: missing ) after expressionList in subroutineCall")
                sys.exit(1)
            self.__writeFullTag("symbol", self.tokenizer.symbol())
            self.tokenizer.advance()
        else:
            print("Error: invalid subroutineCall")
            sys.exit(1)

    def __compileExpressionList(self):
        """Compiles a complete jack expression list grammar"""
        # write open tag
        self.__writeOpenTag("expressionList")

        # if the symbol is ), there is no expression list
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ")":
            # close tag
            self.__writeCloseTag("expressionList")
            return
        else:
            # compile expression
            self.__compileExpression()

            # loop until you dont see a comma
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                # write ,
                self.__writeFullTag("symbol", self.tokenizer.symbol())
                self.tokenizer.advance()

                # compile expression
                self.__compileExpression()

            # write closing tag
            self.__writeCloseTag("expressionList")
