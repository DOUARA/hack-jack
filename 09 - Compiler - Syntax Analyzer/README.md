## The Compiler ( Syntax Analyzer )
This is the first part of developing a compiler for the high level language (Jack) presented on the previous project, 
The compiler is composed of two main components: 
- The syntax analyzer 
- The code generator 
[pic]
In this project we build the syntax analyzer, the syntax analyzer takes a jack code as an input and outputs an xml code specifying the the tokens found in the code along with their type in a tree form. 

## Project
The syntax analyzer is composed of 3 modules:
- **JackTokenizer:** Parses the jack code and provides functionality to walk through the tokens step by step 
- **CompliationEngine:** Uses the Jacktokenizer to read the jack code and generate xml code 
- **JackAnalyzer:** Uses the previous modules to produce xml files 


