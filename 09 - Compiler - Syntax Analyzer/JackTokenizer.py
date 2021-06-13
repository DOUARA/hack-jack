import re
import sys

class JackTokenizer():
    
    def __init__(self, inputFilePath):
        self.input = open(inputFilePath, "r").read()
        self.currentWord = ''
        self.currentToken = ''
        self.currentTokenType = ''
        self.xml = ''
        self.keywords = ['class','constructor','function','method','field','static',
            'var','int','char','boolean','void','true','false','null','this','let',
            'do','if','else','while','return']

        self.symbols = ['{','}','(',')','[', ']','.',',',';','+','-','*','/','&',
            '|','<','>','=','~']

        self.identifierRegex = '^[A-Za-z]\w*$'
        
        # keep tokens only 
        self.__cleanTheInput()
       
    def advance(self):
        if not self.__hasMoreTokens():
            self.currentToken = ''
            return
        if self.__hasMoreTokens():
            self.currentWord = self.input[0]
            
            # case: the word itself is a valid token
            if self.__tokenType(self.currentWord) in ['keyword', 'symbol', 'integerConstant']:
                self.__saveCurrentToken(self.currentWord, self.__tokenType(self.currentWord))
                return
                
            # case: the word is composed of multiple tokens
            else:
                token = '' 
                for i, char in enumerate(self.currentWord):
                    
                    if char in self.symbols:
                        if token:
                            if self.__tokenType(token) in ['keyword', 'integerConstant']:
                                self.__saveCurrentToken(token, self.__tokenType(token))
                                self.input.insert(0, self.currentWord[i:])
                                return
                                
                            else:
                                if self.__tokenType(token) == 'identifier':
                                    self.__saveCurrentToken(token, 'identifier')
                                    self.input.insert(0, self.currentWord[i:])
                                    return
                                else:
                                    sys.exit("Error: Invalid token: " + token)
                        
                        self.__saveCurrentToken(char, 'symbol')
                        self.input.insert(0, self.currentWord[i+1:])
                        return
                        
                    
                    if char == '"':
                        string = ''
                        for j in range(i+1, len(self.currentWord)):
                            if self.currentWord[j] == '"':
                                i=j+1
                                self.__saveCurrentToken(string, 'stringConstant')
                                self.input.insert(0, self.currentWord[i:])
                                return
                                
                            string += self.currentWord[j]
                    
                    token += char

                    if(len(token) == len(self.currentWord) ):
                        if self.__tokenType(token) == 'identifier':
                            self.__saveCurrentToken(token, 'identifier')
                            return
                            
                        else:
                            sys.exit("Error: Invalid token: " + token)
                           
                self.input.pop(0)
                return xml
            
    def getCurrentToken(self):
        return self.currentToken
    
    def getCurrentTokenType(self):
        return self.currentTokenType
    
    def __saveCurrentToken(self, token, tokenType):
        self.currentToken = token
        self.currentTokenType = tokenType
        self.input.pop(0)
    
    def __hasMoreTokens(self):
        return len(self.input) > 0

    def __cleanTheInput(self):
       # Remove inline comments
       self.input = re.sub('//.*\n', '\n', self.input)
       
       # Remove Multiline comments
       self.input = re.sub('/\*.*?\*/', '', self.input, flags=re.S)
       
       # split by white spaces 
       self.input = re.findall("(?:\".*?\"|\S)+", self.input)
       
    def __tokenType(self, token):

        if token in self.keywords:
            return 'keyword'

        if token in self.symbols:
            return 'symbol'

        if token.isdecimal():
            if int(token) >= 0 & int(token) <= 32767:
                return 'integerConstant'
        
        if re.search(self.identifierRegex, token):
            return 'identifier'       

        # check for stringConstant type is embedded in advance() method                             

        return False

