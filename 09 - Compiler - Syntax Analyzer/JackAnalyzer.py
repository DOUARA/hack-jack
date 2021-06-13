from CompilationEngine import CompilationEngine
import sys
import os

class JackAnalyzer:
    def __init__(self):
        self.path = sys.argv[1]
        self.Main()

    def Main(self):
        if os.path.isdir(self.path):
            for inputFile in os.listdir(self.path):
                if inputFile.endswith(".jack"):    
                    outputPath = os.path.join(self.path, inputFile.split('.')[0] + '.xml')
                    inputPath = os.path.join(self.path, inputFile)
                    CompilationEngine(inputPath, outputPath)
            return

        outputPath = self.path.split('.')[0] + '.xml'
        CompilationEngine(self.path, outputPath)
            

JackAnalyzer()

