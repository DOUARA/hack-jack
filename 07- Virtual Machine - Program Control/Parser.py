import sys


class Parser():
    def __init__(self, inputFile):
        self.acceptedWords = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not',
                              'pop', 'push', 'label', 'if-goto', 'goto', 'function', 'call', 'return']
        self.file = open(inputFile, "r")
        self.lines = self.file.readlines()
        self.commands = []
        self.currentCommand = None
        self.nextLine = 0
        self.Main()

    def getCommands(self):
        return self.commands

    def Main(self):
        if self.nextLine >= len(self.lines):
            return
        if self.isValidCommand():
            self.currentCommand = self.lines[self.nextLine]
            commandObject = {}
            commandObject['commandLine'] = self.currentCommand.strip()
            commandObject['command'] = self.currentCommand.split()[0]
            commandObject['type'] = self.commandType()
            commandObject['arg1'] = self.arg1()
            commandObject['arg2'] = self.arg2()
            self.commands.append(commandObject)
        self.nextLine += 1
        self.Main()

    def isValidCommand(self):
        if len(self.lines[self.nextLine].split()) > 0:
            first_word = self.lines[self.nextLine].split()[0]
            if first_word in self.acceptedWords:
                return True
        return False

    def commandType(self):
        parsed = self.currentCommand.split()
        if parsed[0] == 'pop':
            return 'C_POP'
        if parsed[0] == 'push':
            return 'C_PUSH'
        if parsed[0] in ['label', 'goto', 'if-goto']:
            return 'C_BRANCH'
        if parsed[0] == 'function': 
            return 'C_FUNCTION'
        if parsed[0] == 'call':
            return 'C_CALL'
        if parsed[0] == 'return':
            return 'C_RETURN'
        return 'C_ARITHMETIC'

    def arg1(self):
        parsed = self.currentCommand.split()
        if len(parsed) > 1:
            return parsed[1]
        return None

    def arg2(self):
        parsed = self.currentCommand.split()
        if len(parsed) > 2:
            if parsed[2][0] != '/':
                return parsed[2]
        return None
