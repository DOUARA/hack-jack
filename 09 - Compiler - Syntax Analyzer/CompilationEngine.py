from JackTokenizer import JackTokenizer
import sys
import ntpath

class CompilationEngine():
    def __init__(self, inputFilePath, outPutFilePath):
        self.outputFile = open(outPutFilePath, "w")
        self.tokenizer = JackTokenizer(inputFilePath)
        self.currentToken = ''
        self.pauseFlow = False
        self.currentTokenType = ''
        self.compileClass()

    def compileClass(self):
        self.writeXmlTag('class') 

        self.writeNextTokens(3) # 'class' className '{' 
        self.compileClassVarDec()
        self.compileSubroutineDec()
        self.writeNextTokens(1) # '}' 

        self.writeXmlTag('/class') 

    
    def compileClassVarDec(self):
        
        self.advanceAndPause()
        
        if self.currentToken not in ['static', 'field']:
            return
        
        self.writeXmlTag('classVarDec')
        
        self.writeNextTokens(3) #  ('static' | 'field') type varName
        self.writeMultiVar()
        self.writeNextTokens(1) # '}'
        
        self.writeXmlTag('/classVarDec')
        
        self.advanceAndPause() 
        
        # if we have multiple variable declarations
        if self.currentToken in ['static', 'field']:
            self.compileClassVarDec()

    def compileSubroutineDec(self):
        
        self.advanceAndPause() 
        if self.currentToken not in ['constructor', 'function', 'method']:
            return

        self.writeXmlTag('subroutineDec')

        # ('constructor'| 'function' | 'method') ('void' | type) subroutineName '('
        self.writeNextTokens(4) 

        self.compileParameterList()

        self.writeNextTokens(1) # ')' 

        self.compileSubroutineBody()

        self.writeXmlTag('/subroutineDec')

        self.advanceAndPause()

        if self.currentToken in ['constructor', 'function', 'method']:
            self.compileSubroutineDec()

    def compileParameterList(self):
        
        self.advanceAndPause()
        
        self.writeXmlTag('parameterList')

        if self.currentToken == ')':
            self.writeXmlTag('/parameterList')
            return
        
        self.writeNextTokens(2) # type varName

        self.writeMultiVar({'withVarType': True})

        self.writeXmlTag('/parameterList')
    
    
    def compileSubroutineBody(self):
        
        self.writeXmlTag('subroutineBody') 

        self.writeNextTokens(1) # {
        
        self.compileVarDec()

        self.compileStatements()
        
        self.writeNextTokens(1) # }

        self.writeXmlTag('/subroutineBody') 

    
    def compileVarDec(self):
        
        self.advanceAndPause()

        if self.currentToken != 'var':
            return
        
        self.writeXmlTag('varDec')

        self.writeNextTokens(3) # 'var' type varName

        self.writeMultiVar()

        self.writeNextTokens(1) # ';'
        
        self.writeXmlTag('/varDec')

        self.advanceAndPause()

        if self.currentToken == 'var':
            self.compileVarDec()
    
    def compileStatements(self):
        self.writeXmlTag('statements')

        self.__recursiveStatements()

        self.writeXmlTag('/statements')
        
        
    def __recursiveStatements(self):
        self.advanceAndPause()
        if self.currentToken in ['let', 'if', 'while', 'do', 'return']:
            exec('self.compile' + self.currentToken.capitalize() + 'Statement()')
            self.advanceAndPause()
            if self.currentToken in ['let', 'if', 'while', 'do', 'return']:
                self.__recursiveStatements()
            
    
    def compileReturnStatement(self):
        self.writeXmlTag('returnStatement')

        self.writeNextTokens(1) # 'return'
        
        self.advanceAndPause()

        if self.currentToken != ';':
            self.compileExpression()
        
        self.writeNextTokens(1) #  ';'
        
        self.writeXmlTag('/returnStatement')
    
    def compileDoStatement(self):

        self.writeXmlTag('doStatement')

        self.writeNextTokens(1) # 'do'  

        self.compileSubroutineCall()
            
        self.writeNextTokens(1) #  ';'
        
        self.writeXmlTag('/doStatement')

    
    def compileWhileStatement(self):

        self.writeXmlTag('whileStatement')

        self.writeNextTokens(2) # 'while' '(' 
        
        self.compileExpression() # x

        self.writeNextTokens(2) #  ')' '{' 
        
        self.compileStatements()

        self.writeNextTokens(1) # '}'

        self.writeXmlTag('/whileStatement')

    
    def compileIfStatement(self):
        self.writeXmlTag('ifStatement')
        
        self.writeNextTokens(2) # 'if' '('

        self.compileExpression() # x

        self.writeNextTokens(2) # ')' '{'

        self.compileStatements()

        self.writeNextTokens(1) # '}'

        self.advanceAndPause()

        if self.currentToken == 'else':
            self.writeNextTokens(2) # 'else' '{'
            
            self.compileStatements()

            self.writeNextTokens(1) # '}' 
        
        self.writeXmlTag('/ifStatement')


    def compileLetStatement(self):

        self.writeXmlTag('letStatement')
        
        self.writeNextTokens(2) # 'let' varName

        self.advanceAndPause()

        if self.currentToken == '[':
            
            self.writeNextTokens(1) # '['

            self.compileExpression()
           
            self.writeNextTokens(2) # ']' '=' 

            self.compileExpression()

            self.writeNextTokens(1) # ';'
            
            self.writeXmlTag('/letStatement')
            
            return
        
        self.writeNextTokens(1) # '=' 

        self.compileExpression() # x

        self.writeNextTokens(1) # ';'

        self.writeXmlTag('/letStatement')
        
    def compileSubroutineCall(self):
        
        self.writeNextTokens(1) # subroutineName | className | varName

        self.advanceAndPause()

        if self.currentToken == '(':
            self.writeNextTokens(1) # '('
            
            self.compileExpressionList()

            self.writeNextTokens(1) # ')'
        
        if self.currentToken == '.':
            self.writeNextTokens(3) # '.' subroutineName '('

            self.compileExpressionList()

            self.writeNextTokens(1) # ')'

    
    def compileExpressionList(self):
        self.writeXmlTag('expressionList')

        self.advanceAndPause()

        if self.currentToken != ')':
            self.compileExpression()

            self.advanceAndPause()

            if self.currentToken == ',':
                self.writeMultExpressions()

        self.writeXmlTag('/expressionList')

    def compileExpression(self):
        self.writeXmlTag('expression')

        self.compileTerm()

        self.writeXmlTag('/expression')

    def compileTerm(self):
        self.writeXmlTag('term')

        self.advanceAndPause() 
        
        self.writeNextTokens(1) # integerConstant | stringConstant | keywordConstant | varName

        if self.currentToken == '(':
            self.compileExpression()
            self.writeNextTokens(1)
        
        if self.currentToken in ['-', '~']:
            self.compileTerm()

        self.advanceAndPause()

        if self.currentToken == '[':
            self.writeNextTokens(1) # '[' 
            
            self.compileExpression()
            
            self.writeNextTokens(1) # ']'  

        if self.currentToken == '(':
            self.writeNextTokens(1) # '('

            self.compileExpressionList()

            self.writeNextTokens(1) # ')'

        
        if self.currentToken == '.':
            self.writeNextTokens(3) # '.' subroutineName '('

            self.compileExpressionList()

            self.writeNextTokens(1) # '.' subroutineName ')'
        
        self.writeXmlTag('/term') 
        
        self.advanceAndPause()

        if self.currentToken in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.writeNextTokens(1)
            self.compileTerm()

    def writeMultExpressions(self):
        self.writeNextTokens(1) # ','
        
        self.compileExpression()

        self.advanceAndPause()

        if self.currentToken == ',':
            self.writeMultExpressions()
        
    
    def writeMultiVar(self, options = {'withVarType': False}):
        
        self.advanceAndPause()
        
        if self.currentToken == ',':
            self.writeNextTokens(3 if options['withVarType'] else 2)
            self.writeMultiVar({'withVarType': options['withVarType']} )
        
    
    def writeNextTokens(self, i):
        j = i
        if self.pauseFlow == True:
            self.writeCurrentToken()
            self.pauseFlow = False
            j = i - 1
        for _ in range(j) :
            self.tokenizer.advance()
            self.currentToken = self.tokenizer.getCurrentToken()
            self.currentTokenType = self.tokenizer.getCurrentTokenType()
            self.writeCurrentToken()
            
    
    def advanceAndPause(self):
        if self.pauseFlow:
            return
        self.tokenizer.advance()
        self.currentToken = self.tokenizer.getCurrentToken()
        self.currentTokenType = self.tokenizer.getCurrentTokenType()
        self.pauseFlow = True
    
    def writeCurrentToken(self):
        if not self.currentToken:
            return
        specialChars = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            '&': '&amp;'
        }
        if self.currentToken in specialChars:
            self.currentToken = specialChars[self.currentToken] 
        xml = '<' + self.currentTokenType + '>'
        xml += self.currentToken
        xml += '</' + self.currentTokenType + '>'
        xml += '\n'
        self.outputFile.write(xml)
    
    def writeXmlTag(self, tag):
        xml = '<' + tag + '>\n'
        self.outputFile.write(xml)
        
    
