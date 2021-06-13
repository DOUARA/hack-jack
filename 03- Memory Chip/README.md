## Sequential Logic 
All the chips that we have built before are COMBINATIONAL chips, means that they all depend on the combination of its inputs, those kinds of chips doesn't depend on time, they produce their output almost instantly when they get feeded with the inputs.
BUT, our computer architecture requires having some kind of chips that can store their inputs for a specifed amount of time ( theoretically could be unlimited )  those are called SEQUENTIAL chips. 

We start our journey by introducing the computer clock, which is a physical system that delivers an alternative signal to all the sequential chips in the computer, one cycle of this alternative signal represents one unit time. 

The **flip-flop** is the basic sequential chip ( Which can be built with Nand ), accepts a 'bit' input and time input and outputs the input bit of the previous time unit: 
```
out(t)= in(t-1)
```

Using **Mux** gate with the flip-flop we can build the **register** chip which can store one bit information for multiple time units.
building up from the 1 bit register we build the 16K RAM which is a RAM of 16k registers each one holds 16 bit of information
also we've built the counter chip which is an important component of the CPU as we will see in a while 
