import re
import sys

KEYWORDS = ["class", "constructor", "function", "method", "field", "static",
            "var", "int", "char", "boolean", "void", "true", "false", "null",
            "this", "let", "do", "if", "else", "while", "return"]
SYMBOLS = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/",
           "&", "|", "<", ">", "=", "~"]


class JackTokenizer(object):
    """The JackTokenizer takes in a Jack file and splits it into its Tokens"""

    def __init__(self, inFile):
        super(JackTokenizer, self).__init__()
        self.inFile = inFile
        self.tokenList = self.__getTokenList(inFile)
        # said to make sure advance is called before any access to tokens
        self.tokenIndex = -1

    def hasMoreTokens(self):
        """Returns true if the Tokenizer has more tokens to process"""
        return self.tokenIndex < len(self.tokenList)

    def advance(self):
        """Moves to the next token in the Tokenizer"""
        if self.hasMoreTokens():
            self.tokenIndex += 1

    def retreat(self):
        """Moves to the previous token in the Tokenizer. Used to peek ahead for
        generating the grammar for term to distinguish between varName,
        varName[expression], and subroutineCall"""
        self.tokenIndex -= 1

    def reset(self):
        """Reset the tokenizer back to the beginning"""
        self.tokenIndex = -1

    def tokenType(self):
        """Returns the type of the current token, from the set {KEYWORD, SYMBOL,
        IDENTIFIER, INT_CONST, STRING_CONST}"""

        # check if there are tokens
        if not self.hasMoreTokens():
            print("Error: Out of tokens")
            sys.exit(1)

        currentToken = self.tokenList[self.tokenIndex]

        if currentToken in KEYWORDS:
            return "KEYWORD"
        elif currentToken in SYMBOLS:
            return "SYMBOL"
        else:
            # regular expression to match open quote at the start, then anything
            # that isnt a quote or newline, then open quote at the end
            string = re.compile('^\"[^\"\r\n]*\"$')

            # matches a number in the range 0..32767
            integer = re.compile(
                '^([0-9]|[1-8][0-9]|9[0-9]|[1-8][0-9]{2}|9[0-8][0-9]|99[0-9]|[1-8][0-9]{3}|9[0-8][0-9]{2}|99[0-8][0-9]|999[0-9]|[12][0-9]{4}|3[01][0-9]{3}|32[0-6][0-9]{2}|327[0-5][0-9]|3276[0-7])$')

            # matches a sequence of letters, digits, and underscores not starting
            # with a digit
            identifier = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*')

            # match and return the type or exit with invalid token
            if string.match(currentToken):
                return "STRING_CONST"
            elif integer.match(currentToken):
                return "INT_CONST"
            elif identifier.match(currentToken):
                return "IDENTIFIER"
            else:
                print("Error: invalid token " + currentToken)
                sys.exit(1)

    def keyWord(self):
        """Returns the value of the token that is of type KEYWORD. If this is
        called when tokenType() is not KEYWORD, Tokenizer exits"""

        # check for tokens
        if not self.hasMoreTokens():
            print("Error: Out of tokens")
            sys.exit(1)

        if self.tokenType() == "KEYWORD":
            return self.tokenList[self.tokenIndex]
        else:
            print("Error: keyWord() called when token type was not KEYWORD")
            sys.exit(1)

    def symbol(self):
        """Returns the value of the token that is of type SYMBOL. If this is
        called when tokenType() is not SYMBOL, Tokenizer exits"""

        # check for tokens
        if not self.hasMoreTokens():
            print("Error: Out of tokens")
            sys.exit(1)

        if self.tokenType() == "SYMBOL":
            return self.tokenList[self.tokenIndex]
        else:
            print("Error: symbol() called when token type was not SYMBOL")
            sys.exit(1)

    def identifier(self):
        """Returns the value of the token that is of type IDENTIFIER. If this is
        called when tokenType() is not IDENTIFIER, Tokenizer exits"""

        # check for tokens
        if not self.hasMoreTokens():
            print("Error: Out of tokens")
            sys.exit(1)

        if self.tokenType() == "IDENTIFIER":
            return self.tokenList[self.tokenIndex]
        else:
            print("Error: indentifier() called when token type was not IDENTIFIER")
            sys.exit(1)

    def intVal(self):
        """Returns the value of the token that is of type INT_CONST. If this is
        called when tokenType() is not INT_CONST, Tokenizer exits"""

        # check for tokens
        if not self.hasMoreTokens():
            print("Error: Out of tokens")
            sys.exit(1)

        if self.tokenType() == "INT_CONST":
            return self.tokenList[self.tokenIndex]
        else:
            print("Error: intVal() called when token type was not INT_CONST")
            sys.exit(1)

    def stringVal(self):
        """Returns the value of the token that is of type STRING_CONST without the
        quotation marks. If this is called when tokenType() is not STRING_CONST,
        Tokenizer exits"""

        # check for tokens
        if not self.hasMoreTokens():
            print("Error: Out of tokens")
            sys.exit(1)

        # make sure to remove the quotations marks here
        if self.tokenType() == "STRING_CONST":
            return self.tokenList[self.tokenIndex].strip('"')
        else:
            print("Error: stringVal() called when token type was not STRING_CONST")
            sys.exit(1)

    def __getTokenList(self, inFile):
        """Parses and input file and returns a list of (possibly valid) tokens"""
        tokenList = []

        # loop through the input file
        for line in inFile:
            # get all the tokens from the line
            tokens = self.__parseTokens(line)

            # make sure tokens were returned
            if tokens:
                # add each token to the token list (strip just in case, but not
                # sure if needed)
                for token in tokens:
                    t = token.strip()
                    if len(t) == 0:
                        continue
                    tokenList.append(t)

        return tokenList

    def __parseTokens(self, line):
        """Takes a line and returns a list of (possibly valid) tokens in that line"""
        # get rid of whitespace
        stripped = line.strip()
        stripped = stripped.replace("\n", "")
        stripped = stripped.replace("\r", "")
        if len(stripped) == 0:
            return None

        # dont do anything if the line is a comment
        if stripped[0:2] in ["//", "/*"] or stripped.startswith("*"):
            return None

        # remove trailing comments
        noComments = stripped.split("//")[0]

        # define regex for grammar
        # these aren't the strict grammar, just enough to get me the general tokens
        # i check these more throroughly later

        # this just returns one or more words
        identifier = '\w+'
        # this returns one or more digits
        integer = '\d+'
        # this returns anything between quotes
        string = '\".*\"'
        # these are correct because its just choosing from a list
        keyword = (
            'class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return')
        symbol = '{|}|\[|\]|\(|\)|\.|,|;|\+|-|\*|\/|&|\||<|>|=|~'
        grammar = '(' + identifier + '|' + integer + '|' + string + '|' + keyword \
            + '|' + symbol + ')'

        # find grammar matches and return all of them
        return re.findall(grammar, noComments)
