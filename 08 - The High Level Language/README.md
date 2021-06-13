## High Level Language
In a step to facilatate computer programming and make programmers life easier, a layer of abstraction above the virtual machine is necessary, it is the high level language, a formal language that is close the the human thoughts, in this project we present a high level language called **jack** which is a quite similar to the know high level languages like Java and C.
the language specification can be found [here](https://classes.engineering.wustl.edu/cse365/jack.php) 

## Project 
To get familiar with the Jack language and for the aim to build a compiler in the next two modules, we've built an application called **jack paint**, which is a basic tool for drawing that runs on the hack computer that we've built previously. 
The program is composed of 4 modules: 
- **Interface:** Resposible of drawing the interface of the tool. 
- **Tool:** Responsive of the pencil tool and drawing.
- **JackPaint:** Uses the previous two modules to start the program and respond to the user actions.
- **Main:** The program entry point. 

We provided the source code and the compiled files (vm files).

## How to use the paint tool 
- The tool starts with a square in the middle of the screen. 
- You can move the square left, up, right, and down. 
- Press 'space' at any given point to draw it 
- To remove a square just get back to it 
- Press ESC to start with a fresh canvas   
- 
![Screenshot from 2021-06-13 17-17-18](https://user-images.githubusercontent.com/39377174/121814875-3c4a4780-cc6b-11eb-87a1-63a55a6b9364.png)
