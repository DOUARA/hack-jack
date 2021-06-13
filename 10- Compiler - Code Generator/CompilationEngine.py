from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable
import sys
import ntpath
import re 
import uuid

class CompilationEngine():
    def __init__(self, inputFilePath, outPutFilePath):
        self.vm = VMWriter(outPutFilePath)
        self.symbolTable = SymbolTable()
        self.tokenizer = JackTokenizer(inputFilePath)
        self.currentToken = ''
        self.currentTokenType = ''
        self.passedTokens = []
        self.pauseFlow = False
        self.currentExpression = ''
        self.currentFunction = ''
        self.currentFunctionType = ''
        self.currentFunctionKind = ''
        self.currentClass=''
        self.nArgs = 0
        self.compileClass()

    def compileClass(self):
        self.saveNextTokens(3) # 'class' className '{' 
        self.currentClass = self.passedTokens[1]['token']
        self.compileClassVarDec()
        self.compileSubroutineDec()
        self.saveNextTokens(1) # '}' 
    
    def compileClassVarDec(self):
        
        self.advanceAndPause()
        
        if self.currentToken not in ['static', 'field']:
            return
        
        self.saveNextTokens(3) #  ('static' | 'field') type varName
        
        self.symbolTable.define(
            self.passedTokens[2]['token'], 
            self.passedTokens[1]['token'], 
            self.passedTokens[0]['token']
        )
        
        self.writeMultiVar(self.passedTokens[1]['token'], self.passedTokens[0]['token'])
        
        self.saveNextTokens(1) # '}'
                
        self.advanceAndPause() 
        
        # if we have multiple variable declarations
        if self.currentToken in ['static', 'field']:
            self.compileClassVarDec()

    def compileSubroutineDec(self):
        self.symbolTable.startSubroutine()
        
        self.advanceAndPause() 
        
        if self.currentToken not in ['constructor', 'function', 'method']:
            return

        # ('constructor'| 'function' | 'method') ('void' | type) subroutineName '('
        self.saveNextTokens(4) 
        
        self.currentFunction = self.passedTokens[2]['token']
        self.currentFunctionType = self.passedTokens[1]['token']
        self.currentFunctionKind = self.passedTokens[0]['token']

        # we should define 'this' here. 
        
        self.compileParameterList()
        
        self.saveNextTokens(1) # ')' 

        self.compileSubroutineBody()

        self.advanceAndPause()
       
        if self.currentToken in ['constructor', 'function', 'method']:
            self.compileSubroutineDec()

    def compileParameterList(self):
        
        self.advanceAndPause()
        
        if self.currentToken == ')':
            return
        
        self.saveNextTokens(2) # type varName

        if self.currentFunctionKind == 'method':
            self.symbolTable.define('this', self.currentFunctionType, 'argument')

        self.symbolTable.define(self.passedTokens[1]['token'],
                                self.passedTokens[0]['token'],
                                'argument')

        self.writeMultiVarWithType()

    
    def compileSubroutineBody(self):
        
        self.saveNextTokens(1) # {
        
        self.compileVarDec()
        
        self.vm.writeFunction(self.currentClass + '.' + self.currentFunction, self.symbolTable.getLocalsCount())
        
        if self.currentFunctionKind == 'constructor':
            fName = self.currentFunctionType + '.' + self.currentFunction
            self.vm.writePush('constant', self.symbolTable.getFieldsCount())
            self.vm.writeCall('Memory.alloc', 1)
            self.vm.writePop('pointer', 0)

        if self.currentFunctionKind == 'method':
            self.vm.writePush('argument', 0)
            self.vm.writePop('pointer', 0)
            self.nArgs += 1

        self.compileStatements()
        
        self.saveNextTokens(1) # }

    
    def compileVarDec(self):
        
        self.advanceAndPause()

        if self.currentToken != 'var':
            return

        self.saveNextTokens(3) # 'var' type varName

        self.symbolTable.define(self.passedTokens[2]['token'],
                                self.passedTokens[1]['token'],
                                'local')

        self.writeMultiVar(self.passedTokens[1]['token'], 'local')
        self.saveNextTokens(1) # ';'

        self.advanceAndPause()

        if self.currentToken == 'var':
            self.compileVarDec()
        
    
    def compileStatements(self):
        self.advanceAndPause()
        self.nArgs = 0
        if self.currentToken in ['let', 'if', 'while', 'do', 'return']:
            exec('self.compile' + self.currentToken.capitalize() + 'Statement()')
            self.advanceAndPause()
            if self.currentToken in ['let', 'if', 'while', 'do', 'return']:
                self.compileStatements()
    
    def compileReturnStatement(self):
        
        self.saveNextTokens(1) # 'return'

        self.advanceAndPause()

        if self.currentToken == 'this':
            self.vm.writePush('pointer', 0)
            self.saveNextTokens(2) # 'this ;'
            self.vm.writeReturn()
            return

        if self.currentToken != ';':
            self.compileExpression()
        
        
        if self.currentFunctionType == 'void':
            self.vm.writePush('constant', 0)
            
        self.saveNextTokens(1) #  ';'
        
        self.vm.writeReturn()
        
    
    def compileDoStatement(self):

        self.saveNextTokens(1) # 'do'  

        self.compileExpression()
            
        self.saveNextTokens(1) #  ';'

        self.vm.writePop('temp', 0)
    
    
    def compileWhileStatement(self):

        whileLabel = 'while_' + str(uuid.uuid4())[:18]

        exitWhile = 'exitWhile_' + str(uuid.uuid4())[:18]

        self.saveNextTokens(2) # 'while' '(' 
        
        self.vm.writeLabel(whileLabel)

        self.compileExpression() # x

        self.vm.writeCommand('not')

        self.vm.writeIf(exitWhile)

        self.saveNextTokens(2) #  ')' '{' 
        
        self.compileStatements()

        self.vm.writeGoto(whileLabel)

        self.saveNextTokens(1) # '}'

        self.vm.writeLabel(exitWhile)

    
    def compileIfStatement(self):
        
        elseLabel = 'else_' + str(uuid.uuid4())[:18]
        
        continueLabel = 'continue_' + str(uuid.uuid4())[:18]
        
        noElseLabel = 'noElseLabel_' + str(uuid.uuid4())[:18]
        
        self.saveNextTokens(2) # 'if' '('

        self.compileExpression() # x

        self.vm.writeCommand('not')

        self.saveNextTokens(2) # ')' '{'

        self.vm.writeIf(elseLabel)
        
        self.compileStatements()

        self.saveNextTokens(1) # '}'

        self.vm.writeGoto(continueLabel)

        self.advanceAndPause()

        if self.currentToken == 'else':
            self.saveNextTokens(2) # 'else' '{'
            
            self.vm.writeLabel(elseLabel)
            
            self.compileStatements()

            self.saveNextTokens(1) # '}' 

            self.vm.writeLabel(continueLabel)
        else:
            self.vm.writeLabel(elseLabel)
            self.vm.writeLabel(continueLabel)
    
    
    def compileLetStatement(self):
        
        self.saveNextTokens(2) # 'let' varName

        varName = self.passedTokens[1]['token']
        
        self.advanceAndPause()

        # Array Handling
        if self.currentToken == '[':
            varKind = self.symbolTable.kindOf(varName)
            varIndex = self.symbolTable.indexOf(varName)

            self.vm.writePush(varKind, varIndex)

            self.saveNextTokens(1) # '['

            self.compileExpression()

            self.vm.writeArithmetic('+')
           
            self.saveNextTokens(2) # ']' '=' 

            self.compileExpression()

            self.vm.writePop('temp', 0)
            self.vm.writePop('pointer', 1)
            self.vm.writePush('temp', 0)
            self.vm.writePop('that', 0)

            self.saveNextTokens(1) # ';'
            
            return
        
        self.saveNextTokens(1) # '=' 
        self.compileExpression() # x

        self.saveNextTokens(1) # ';'

        # pop the stack into the variable
        varIndex = self.symbolTable.indexOf(varName)
        varKind = self.symbolTable.kindOf(varName)
        if varIndex != None:
            if varKind == 'field':
                varKind = 'this'
            self.vm.writePop(varKind, varIndex)
        else:
            sys.exit('Error: Call to undefined variable: ' + varName)
        
    def compileSubroutineCall(self):

        self.saveNextTokens(1) # subroutineName | className | varName
        
        fName = self.passedTokens[0]['token']
       
        self.advanceAndPause()

        if self.currentToken == '(':
           
            self.saveNextTokens(1) # '('
            
            self.compileExpressionList()
            
            self.saveNextTokens(1) # ')'
        
        if self.currentToken == '.':
            className = self.symbolTable.typeOf(fName)
            index = self.symbolTable.indexOf(fName)
            kind = self.symbolTable.kindOf(fName)
            
            self.saveNextTokens(3) # '.' subroutineName '('
            
            if className:
                
                fName = ( className + self.passedTokens[0]['token'] +  
                        self.passedTokens[1]['token'] )
                
                
                # Pushing the object address into the stack
                if kind == 'field':
                    self.vm.writePush('this', index)
                    self.nArgs += 1
                    
                else:
                    self.vm.writePush(kind, index)
                    self.nArgs += 1
            
            else:
                fName += ( self.passedTokens[0]['token'] +  
                        self.passedTokens[1]['token'] )
            
            
            
            self.compileExpressionList()

            if fName.find('.') == -1:
                # This certainly means that we are calling a class method within the same class
                self.vm.writePush('pointer', 0)
                self.nArgs += 1
                fName = self.currentClass + '.' + fName
            
            self.vm.writeCall(fName, self.nArgs)

            self.saveNextTokens(1) # ')'

    
    def compileExpressionList(self):
        self.advanceAndPause()
        
        if self.currentToken != ')':
            self.compileTerm()
            self.nArgs += 1
            self.advanceAndPause()
            
            if self.currentToken == ',':
                self.writeMultExpressions()
        '''
        if fName.find('.') == -1:
            # This certainly means that we are calling a class method within the same class
            self.vm.writePush('pointer', 0)
            self.nArgs += 1
            cFName = self.currentClass + '.' + cFName
        self.vm.writeCall(cFName, self.nArgs)
        '''

        
    def removeParas(self, exp):
        expression = exp
        chars = []
        stack = []
        count = 0
        for index, char in enumerate(exp): 
            if char == '(':
                stack.append(index)
            else:
                chars.append(char)
            if char == ')':
                if index == len(exp) - 1 and len(stack) != 0 and stack[0] == 0:  
                    count += 1
                if len(stack) != 0:
                    stack.pop()
        for _ in range(count):
            expression = expression[1:-1]
        
        return expression


    def writeExpression(self, exp):
        if not exp:
            return
        

        # Remove redundant parantheses
        expression = self.removeParas(exp)

        # case: string
        if self.passedTokens[0]['tokenType'] == "stringConstant":
            # String Construction 
            string = self.passedTokens[0]['token']
            stringLength = len(string)
            self.vm.writePush('constant', stringLength)
            self.vm.writeCall('String.new', 1)
            for char in string:
                self.vm.writePush('constant', ord(char))
                self.vm.writeCall('String.appendChar', 2)
            return
        
        # case: exp = op exp1
        if expression[0] in ['-', '~']:
            self.writeExpression(expression[1:])
            if expression[0] == '-':
                self.vm.writeCommand('neg')
            else:
                self.vm.writeCommand('not')
            return
        
        # case: exp = constant
        if expression.isnumeric():
            self.vm.writePush('constant', expression)
            return

        functionSearch = re.search('^(\w+(\.\w+)?)\((.*)\)$', expression)
        # case: exp = f(exp1, exp2,...)
        if functionSearch:
            parametersList = re.split(',\s*(?![^()]*\))', functionSearch.group(3))
            fName = functionSearch.group(1)
            args = len(parametersList)
           
            if parametersList[0] == '':
                args = 0

            # Functions Conditions
            if fName.find('.') == -1:
                # This certainly means that we are calling a class method within the same class
                self.vm.writePush('pointer', 0)
                args += 1
                fName = self.currentClass + '.' + fName
        
            if fName.find('.') != -1:
                objectName = fName.split('.')[0]
                fNameType = self.symbolTable.typeOf(objectName)
                fNameKind = self.symbolTable.kindOf(objectName)
                fNameIndex = self.symbolTable.indexOf(objectName)
                
                if fNameType:
                    if fNameKind == 'field':
                        self.vm.writePush('this', fNameIndex)
                    else:
                        self.vm.writePush(fNameKind, fNameIndex)
                    args += 1
                    fName = fNameType + '.' + fName.split('.')[1] 
                    
            
            for param in parametersList:
                if param:    
                    kind = self.symbolTable.kindOf(param)
                    if param[0] == '"': # means this is a srting
                        string = param[1:-1]
                        
                        stringLength = len(string)
                        self.vm.writePush('constant', len(string))
                        self.vm.writeCall('String.new', 1)
                        for char in string:
                            self.vm.writePush('constant', ord(char))
                            self.vm.writeCall('String.appendChar', 2)
                    else:
                        self.writeExpression(param)


            self.vm.writeCall(fName, args)
            return

        # case: exp = varibale name or keywordConstant
        if re.search("^[A-Za-z_]\w*$", expression):
            if expression == 'true':
                self.vm.writePush('constant', 1)
                self.vm.writeCommand('neg')
                return
            
            if expression == 'this':
                self.vm.writePush('pointer', 0)
                return
            
            if expression in ['false', 'null']:
                self.vm.writePush('constant', 0)
                return
            
            varIndex = self.symbolTable.indexOf(expression)
            if varIndex != None:
                varKind = self.symbolTable.kindOf(expression)
                if varKind == 'field':
                    varKind = 'this'
                self.vm.writePush(varKind, varIndex)
                return

            else:
                sys.exit('Error: Call to Undefined Variable: ' + expression)
        
        
        # case exp = varName[exp]
        arraySearch = re.search("^([A-Za-z_]\w*)\[(.+)\]$", expression)

        if arraySearch:
            innerExp = arraySearch.group(2)
            stack = []
            for char in innerExp:
                if char == '[':
                    stack.append('[')
                if char == ']':
                    if len(stack):
                        stack.pop()
            
            if len(stack) == 0:
                varName = arraySearch.group(1)

                varKind = self.symbolTable.kindOf(varName)
                varIndex = self.symbolTable.indexOf(varName)

                self.vm.writePush(varKind, varIndex)
                
                self.writeExpression(innerExp)

                self.vm.writeArithmetic('+')
                self.vm.writePop('pointer', 1)
                self.vm.writePush('that', 0)
                return

        # case: exp = exp1 op exp2
        for char in JackTokenizer.operators:
            stackPara = []
            stackSquarePara = []
            for index, char in enumerate(reversed(expression)):
                if char == ']':
                    stackSquarePara.append(index)
                if char == '[':
                    stackSquarePara.pop()
                if char == ')':
                    stackPara.append(index)
                if char == '(':
                    stackPara.pop()
                for op in JackTokenizer.operators:
                    if (char == op and not len(stackPara) and index !=0
                        and not len(stackSquarePara)):
                        exp1 = expression[0:len(expression)-index-1]
                        exp2 = expression[len(expression)-index:]
                        self.writeExpression(exp1)
                        self.writeExpression(exp2)
                        self.vm.writeArithmetic(expression[len(expression)-index-1])
                        return    
    
    def compileExpression(self):
        self.currentExpression = ''
        self.compileTerm()
        self.writeExpression(self.currentExpression)  
        
    def compileTerm(self):
       
        self.advanceAndPause() 
                
        self.saveNextTokens(1) # integerConstant | stringConstant | keywordConstant | identifier

        fName = self.passedTokens[0]['token']
        
        self.currentExpression += self.passedTokens[0]['token']
       
        if self.currentToken == '(':
            
            self.compileTerm()
            self.saveNextTokens(1) # )
            self.currentExpression += self.passedTokens[0]['token']
        
        if self.currentToken in ['-', '~']:
            self.compileTerm()

        self.advanceAndPause()
        
        # Array Handling
        if self.currentToken == '[':
            
            self.saveNextTokens(1) # '[' 

            self.currentExpression += self.passedTokens[0]['token']
            
            self.compileTerm()
            
            self.saveNextTokens(1) # ']'
            self.currentExpression += self.passedTokens[0]['token'] 


        if self.currentToken == '(':

            self.saveNextTokens(1) # '('
            self.currentExpression += self.passedTokens[0]['token']
            self.compileExpressionList()

            self.saveNextTokens(1) # ')'
            self.currentExpression += self.passedTokens[0]['token']

        if self.currentToken == '.':
            self.saveNextTokens(3) # '.' subroutineName '('
            self.currentExpression += self.passedTokens[0]['token']
            self.currentExpression += self.passedTokens[1]['token']
            self.currentExpression += self.passedTokens[2]['token']
            
            fName += self.passedTokens[0]['token'] + self.passedTokens[1]['token']
            
            self.compileExpressionList()

            self.saveNextTokens(1) # '.' subroutineName ')'
            self.currentExpression += self.passedTokens[0]['token']
            
        self.advanceAndPause()
        
        # - Those operations require to have 2 elements on the stack
        # - '/' & '*' are implemented by the operating system function
        if self.currentToken in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.saveNextTokens(1)
            self.currentExpression += self.passedTokens[0]['token']
            self.compileTerm()
        
        
    def writeMultExpressions(self):
        self.saveNextTokens(1) # ','
        self.currentExpression += self.passedTokens[0]['token']
        
        self.compileTerm()

        self.advanceAndPause()
        self.nArgs += 1

        if self.currentToken == ',':
            self.writeMultExpressions()
        

    def writeMultiVar(self, varType = 'char', varKind = 'argument'):
        
        self.advanceAndPause()
        
        if self.currentToken == ',':
            self.saveNextTokens(2) # ',' varName 
            self.symbolTable.define(self.passedTokens[1]['token'], 
                                        varType,
                                        varKind
                                    )
            
            self.writeMultiVar(varType, varKind)
        
    def writeMultiVarWithType(self):
        self.advanceAndPause()

        if self.currentToken == ',':
            self.saveNextTokens(3) # ',' varType varName
            self.symbolTable.define(self.passedTokens[2]['token'], 
                                        self.passedTokens[1]['token'],
                                        'argument'
                                    )
            self.writeMultiVarWithType()
    
    def saveNextTokens(self, i):
        self.passedTokens = []
        j = i
        if self.pauseFlow == True:
            self.saveCurrentToken()
            self.pauseFlow = False
            j = i - 1
        for _ in range(j) :
            self.tokenizer.advance()
            self.currentToken = self.tokenizer.getCurrentToken()
            self.currentTokenType = self.tokenizer.getCurrentTokenType()
            self.saveCurrentToken()
            
    
    def advanceAndPause(self):
        if self.pauseFlow:
            return
        self.tokenizer.advance()
        self.currentToken = self.tokenizer.getCurrentToken()
        self.currentTokenType = self.tokenizer.getCurrentTokenType()
        self.pauseFlow = True
    
    def saveCurrentToken(self):
        if not self.currentToken:
            return
        self.passedTokens.append({'token': self.currentToken, 'tokenType': self.currentTokenType})
    
   