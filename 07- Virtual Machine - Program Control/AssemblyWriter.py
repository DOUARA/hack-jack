import sys
import ntpath

class AssemblyWriter():
  def __init__(self, outputFile, inputFile = ''):
    self.inputFile = inputFile
    self.fileName = ntpath.basename(outputFile).split('.')[0]
    self.file = open(outputFile, "a")
    self.outputFile = outputFile
    self.iterator = 0
    self.asmCode = ''

  def close(self):
    if self.asmCode:
      endCode = '(END)\n'
      endCode += '@END\n' 
      endCode += '0;JMP'
      return self.file.write(endCode)  
    self.file.close()

  '''
  Writes the assembly bootstrap code in the output file 
    Parameters:
      None
     
    Returns:
      asmCode (str): Assembly code for bootstrapped code
  '''
  def writeInit(self):
    asmCode  = ''
    lineBreak = '\n'
    
    asmCode  += '@256' + lineBreak
    asmCode  += 'D=A' + lineBreak
    asmCode  += '@SP' + lineBreak
    asmCode  += 'M=D' + lineBreak

    asmCode  += self.writeCall('Sys.init', '0', False)
    
    self.asmCode += asmCode
    self.file.write(asmCode)
    return asmCode
  
  '''
  Writes the assembly code in the output file for return command
    Parameters:
      None
     
    Returns:
      asmCode (str): Assembly code for the command
  '''
  def writeReturn(self):
    asmCode  = ''
    lineBreak = '\n'

    # EndFrame Address
    asmCode  += '@LCL' + lineBreak
    asmCode  += 'D=M' + lineBreak
    asmCode  += '@R13' + lineBreak
    asmCode  += 'M=D' + lineBreak # endFrame = RAM[R13]
    asmCode  += '@5' + lineBreak
    asmCode  += 'D=D-A' + lineBreak
    asmCode  += 'A=D' + lineBreak
    asmCode  += 'D=M' + lineBreak # D=retAddr
    asmCode  += '@R14' + lineBreak
    asmCode  += 'M=D' + lineBreak # retAdd = RAM[R14]

    # Reposition the return value
    asmCode += self.writePushPop('C_POP', 'argument', '0', False)

    # Reposition SP 
    asmCode += '@ARG' + lineBreak
    asmCode += 'D=M' + lineBreak
    asmCode += '@SP' + lineBreak
    asmCode += 'M=D+1' + lineBreak
    
    # Restore caller state
    segmentsMapping = {
      'THAT': '1',
      'THIS': '2',
      'ARG': '3',
      'LCL': '4'
    }
    for SEG in segmentsMapping.keys():
      asmCode += '@R13' + lineBreak
      asmCode += 'D=M' + lineBreak
      asmCode += '@' + segmentsMapping[SEG] + lineBreak
      asmCode += 'D=D-A' + lineBreak
      asmCode += 'A=D' + lineBreak
      asmCode += 'D=M' + lineBreak
      asmCode += '@' + SEG + lineBreak
      asmCode += 'M=D' + lineBreak
    
    # Return to the caller
    if self.currentFunctionCall: 
      asmCode += '@R14' + lineBreak
      asmCode += 'A=M' + lineBreak
      asmCode += '0;JMP' + lineBreak

    self.iterator +=1
    self.asmCode += asmCode
    self.file.write(asmCode)
    return asmCode
  
  
  '''
  Writes the assembly code in the output file for function command
    Parameters:
      fName (str): function Name
      nLocal (str): number of local variables 
     
    Returns:
      asmCode (str): Assembly code for the command
  '''
  def writeFunction(self, fName, nLocal):
    asmCode  = ''
    lineBreak = '\n'

    # Function label 
    asmCode += self.writeBranches('label', fName, False)
    
    # Local variable initializaion
    for i in range(int(nLocal)):
      asmCode += self.writePushPop('C_PUSH', 'constant', '0', False)
    
    self.currentFunctionCall = fName
    
    self.iterator +=1
    self.asmCode += asmCode
    self.file.write(asmCode)
    return asmCode


  '''
  Writes the assembly code in the output file for call function command
    Parameters:
      fName (str): function Name
      nArg (str): number of arguments 
     
    Returns:
      asmCode (str): Assembly code for the command
  '''
  def writeCall(self, fName, nArg, writeInFile = True):
    asmCode  = ''
    lineBreak = '\n'
    
    # Generate and push return address
    
    uniqueLabel = str(sum([ord(i) for i in self.fileName])) +  str(self.iterator)
    returnLabel = 'RETURN_'  + uniqueLabel
    
    asmCode += '@' + returnLabel + lineBreak
    asmCode += 'D=A' + lineBreak
    asmCode += '@SP' + lineBreak
    asmCode += 'A=M'  + lineBreak
    asmCode += 'M=D'  + lineBreak
    asmCode += '@SP' + lineBreak
    asmCode += 'M=M+1' + lineBreak

    # push current LCL, ARG, THIS, THAT
    for SEG in ['LCL', 'ARG', 'THIS', 'THAT']:
      asmCode += '@' + SEG + lineBreak
      asmCode += 'D=M' + lineBreak
      asmCode += '@SP' + lineBreak
      asmCode += 'A=M'  + lineBreak
      asmCode += 'M=D'  + lineBreak
      asmCode += '@SP' + lineBreak
      asmCode += 'M=M+1' + lineBreak

    # Reposition ARG
    asmCode += '@5' + lineBreak
    asmCode += 'D=A' + lineBreak
    asmCode += '@' + nArg + lineBreak
    asmCode += 'D=D+A' + lineBreak
    asmCode += '@SP' + lineBreak
    asmCode += 'D=M-D' + lineBreak
    asmCode += '@ARG' + lineBreak
    asmCode += 'M=D' + lineBreak

    # Put LCL = SP
    asmCode += '@SP' + lineBreak
    asmCode += 'D=M' + lineBreak
    asmCode += '@LCL' + lineBreak
    asmCode += 'M=D' + lineBreak

    # goto functionName 
    asmCode += self.writeBranches('goto', fName, False)

    # return label
    asmCode += self.writeBranches('label', returnLabel, False)
    
    self.iterator += 1
    
    if writeInFile:
      self.asmCode += asmCode
      self.file.write(asmCode)

    return asmCode
  
  
  '''
  Writes the assembly code in the output file for branching commands
    Parameters:
      command (str): the branching command 
      arg (str): the argument of the command 
     
    Returns:
      asmCode (str): Assembly code for the command
  '''
  def writeBranches(self, command, arg, writeInFile = True):
    asmCode  = ''
    lineBreak = '\n'
    if command == 'label':
      asmCode += '(' + arg + ')' + lineBreak

    if command == 'goto':
      asmCode += '@' + arg + lineBreak
      asmCode += '0;JMP' + lineBreak

    if command == 'if-goto':
      asmCode += '@SP' + lineBreak 
      asmCode += 'M=M-1' + lineBreak
      asmCode += 'A=M' + lineBreak
      asmCode += 'D=M' + lineBreak 
      asmCode += '@' + arg + lineBreak
      asmCode += 'D;JNE' + lineBreak
    
    self.iterator +=1
    if writeInFile:
      self.asmCode += asmCode
      self.file.write(asmCode)
    return asmCode
    

  '''
  Writes the assembly code in the output file for an arithmetic command
    Parameters:
      command (str): the arithmetic command 
     
    Returns:
      asmCode (str): Assembly code for the command
  '''
  def writeArithmetic(self, command):
    asmCode  = ''
    lineBreak = '\n'
    uniqueLabel = str(sum([ord(i) for i in self.fileName])) +  str(self.iterator)
    
    # add and sub mapping
    addSubMapping = {
      'add': '+',
      'sub': '-', 
      'and': '&',
      'or': '|'
    }

    if command in addSubMapping.keys():
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M-1' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'D=M' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M-1' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'M=M' + addSubMapping[command] + 'D' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M+1' + lineBreak

    # Negation & not mapping
    negNotMapping = {
      'neg': '-',
      'not': '!'
    }
    if command in negNotMapping.keys():
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M-1' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'D=M' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'M=' + negNotMapping[command] + 'D' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M+1' + lineBreak

    # gt, lt, eq opeartions 
    compareMapping = {
      'gt': {
        'truthy': 'JGT',
        'falsy': 'JLE',
      },
      'lt': {
        'truthy': 'JLT',
        'falsy': 'JGE',
      },
      'eq': {
        'truthy': 'JEQ',
        'falsy': 'JNE',
      }
    }

    if command in compareMapping.keys():
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M-1' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'D=M' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M-1' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'D=M-D' + lineBreak
      asmCode  += '@TRUE_'+ uniqueLabel + lineBreak
      asmCode  += 'D;' + compareMapping[command]['truthy'] + lineBreak
      asmCode  += '@FALSE_'+ uniqueLabel + lineBreak
      asmCode  += 'D;' + compareMapping[command]['falsy'] + lineBreak
      
      asmCode  += '(TRUE_'+ uniqueLabel +')' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'M=-1' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M+1' + lineBreak
      asmCode  += '@CONINUE_' + uniqueLabel + lineBreak
      asmCode  += '0;JMP' + lineBreak

      asmCode  += '(FALSE_'+ uniqueLabel +')' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'M=0' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M+1' + lineBreak
      asmCode  += '(CONINUE_' + uniqueLabel + ')' + lineBreak
    
    self.iterator +=1
    self.asmCode += asmCode
    self.file.write(asmCode)
    return asmCode

      
  '''
  Writes the  assembly code in the output file for for push or pop commands
    Parameters:
      commandType (str): the type of the command: C_POP or C_PUSH
      segmentName (str): the name of the segmant: temp, static. argument, ...
      index (str): the index in the command

    Returns:
      asmCode (str): Assembly code for the command
  '''
  def writePushPop(self, commandType, segment, index, writeInFile = True ):
      asmCode  = ''
      lineBreak = '\n'
      uniqueLabel = str(sum([ord(i) for i in self.fileName])) +  str(self.iterator)

      # Segments Assembly Variables Mapping. 
      segmentsMapping = {
          'local': 'LCL',
          'argument': 'ARG',
          'this': 'THIS',
          'that': 'THAT',
          'temp': '5'
      }

      # PUSH command Code Generation
      if commandType == 'C_PUSH':
         
        # Segments: local, argument, this, that, temp
        if segment in segmentsMapping.keys():
          asmCode += '@' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@' + segmentsMapping[segment] + lineBreak
          if segment == 'temp':
            asmCode += 'A=D+A' + lineBreak
          else:
            asmCode += 'A=D+M' + lineBreak
          asmCode += 'D=M' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'M=D' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'M=M+1' + lineBreak
         
        # Segment: constant
        if segment == 'constant':
          asmCode += '@' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'M=M+1' + lineBreak

        # Segment: static
        if segment == 'static':
          asmCode += '@' + self.inputFile + '.' + index + lineBreak
          asmCode += 'D=M'  + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'M=M+1' + lineBreak
        
        # Segment: pointer
        if segment == 'pointer' and (index == '0' or index == '1') :
          asmCode += '@' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@THIS_B' + uniqueLabel + lineBreak
          asmCode += 'D;JEQ'  + lineBreak
          asmCode += '@THAT_B'  + uniqueLabel + lineBreak
          asmCode += 'D;JGT'  + lineBreak
          
          # THIS Branch
          asmCode += '(THIS_B' + uniqueLabel + ')'  + lineBreak
          asmCode += '@THIS' + lineBreak
          asmCode += 'D=M'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'M=M+1' + lineBreak
          asmCode  += '@CONINUE_' + uniqueLabel + lineBreak
          asmCode  += '0;JMP' + lineBreak
         
          # THAT Branch
          asmCode += '(THAT_B' + uniqueLabel + ')'  + lineBreak
          asmCode += '@THAT' + lineBreak
          asmCode += 'D=M'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'M=M+1'  + lineBreak
          asmCode  += '(CONINUE_' + uniqueLabel + ')' + lineBreak

      # POP command Code Generation
      if commandType == 'C_POP':
        
        # Segments: local, argument, this, that, temp
        if segment in segmentsMapping.keys():
          asmCode += '@' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@' + segmentsMapping[segment] + lineBreak
          if segment == 'temp':
            asmCode += 'D=D+A' + lineBreak
          else:
            asmCode += 'D=D+M' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'M=D' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'M=M-1' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'D=M' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M+1' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'M=D' + lineBreak

        # No pop command for constant segmant 

        # Segment: static
        if segment == 'static':
          asmCode += '@' + self.inputFile + '.' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'M=D' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'M=M-1' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'D=M' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M+1' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'M=D' + lineBreak

        # Segment: pointer
        if segment == 'pointer' and (index == '0' or index == '1') :
          asmCode += '@' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@THIS_B' + uniqueLabel + lineBreak
          asmCode += 'D;JEQ' + lineBreak
          asmCode += '@THAT_B' + uniqueLabel + lineBreak
          asmCode += 'D;JGT' + lineBreak
          
          # THIS Branch
          asmCode += '(THIS_B' + uniqueLabel + ')' + lineBreak
          asmCode += '@THIS'  + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'M=M-1'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'D=M'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M+1'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode  += '@CONINUE_' + uniqueLabel + lineBreak
          asmCode  += '0;JMP' + lineBreak

          # THAT Branch
          asmCode += '(THAT_B' + uniqueLabel + ')' + lineBreak
          asmCode += '@THAT'  + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'M=M-1'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'D=M'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M+1'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D' + lineBreak
          asmCode  += '(CONINUE_' + uniqueLabel + ')' + lineBreak
      
      self.iterator +=1
      if writeInFile:
        self.asmCode += asmCode
        self.file.write(asmCode)
      return asmCode

