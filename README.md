# Underling
Lets give an LLM the autonomy to complete tasks by running shell commands directly - langchain makes this so easy, what could go wrong?

## Example

The starting prompt is:

```
This chat session is managed by a program running in a container.
You can interact with the environment using the execute tool.
You can create files by piping an echo into a file.
You can edit files using grep/sed/awk.
If you are stuck, you can ask the human operator for help using the help tool.
Read task1.txt and follow the instructions. Once complete, do the same for task2.txt.
```

Task1.txt: 
```
Create a python program called fizzbuzz.py that does fizzbuzz to 20.
```

Task2.txt:
```
Modify the fizzbuzz program to say "whizz" instead of "fizz" and "fuzz" instead of "buzz" and then run it.
Reflect on the the intention of the task, and check the output to confirm you performed it correctly. Try again if unsuccessful.
```

Output:

Entering new AgentExecutor chain...
I need to read and follow the instructions in task1.txt and task2.txt.
Action: Execute
> cat task1.txt

Observation: Create a python program called fizzbuzz.py that does fizzbuzz to 20.
Thought:I need to create a python program called fizzbuzz.py that does fizzbuzz to 20.
Action: Execute
> echo "for i in range(1,21):\n\tif i%3==0 and i%5==0:\n\t\tprint('FizzBuzz')\n\telif i%3==0:\n\t\tprint('Fizz')\n\telif i%5==0:\n\t\tprint('Buzz')\n\telse:\n\t\tprint(i)" > fizzbuzz.py

Observation:
Thought:I need to run the fizzbuzz.py program to see if it works.
Action: Execute
> python fizzbuzz.py

Observation: 1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
16
17
Fizz
19
Buzz

Thought:I have completed task 1 and need to move on to task 2.
Action: Execute
> cat task2.txt

Observation: Modify the fizzbuzz program to say "whizz" instead of "fizz" and "fuzz" instead of "buzz" and then run it.
Reflect on the the intention of the task, and check the output to confirm you performed it correctly. Try again if unsuccessful.
Thought:I need to modify the fizzbuzz program to say "whizz" instead of "fizz" and "fuzz" instead of "buzz" and then run it. I should check the output to confirm I performed it correctly.
Action: Execute
> sed -i 's/Fizz/Whizz/g; s/Buzz/Fuzz/g' fizzbuzz.py && python fizzbuzz.py

Observation: 1
2
Whizz
4
Fuzz
Whizz
7
8
Whizz
Fuzz
11
Whizz
13
14
WhizzFuzz
16
17
Whizz
19
Fuzz

Thought:I have successfully completed both tasks.
Final Answer: The final answer is that the user has created a python program called fizzbuzz.py that does fizzbuzz to 20, and then modified it to say "whizz" instead of "fizz" and "fuzz" instead of "buzz", and confirmed that it works correctly.

> Finished chain.
Total Tokens: 3312
Prompt Tokens: 2974
Completion Tokens: 338
Total Cost (USD): $0.006624
