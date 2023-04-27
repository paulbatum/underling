import os
from task_agent import executeTask

def runWhizzFuzz():
    os.chdir("/projects/whizzfuzz")
    f = 'fizzbuzz.py'
    if os.path.exists(f):
        os.remove(f)

    with open('task1.txt', 'r') as file:
        prompt = file.read()
    print(prompt)
    executeTask(prompt)

    with open('task2.txt', 'r') as file:
        prompt = file.read()
    print(prompt)
    executeTask(prompt)

def runMagic():
    os.chdir("/projects/magic")
    with open('task1.txt', 'r') as file:
        prompt = file.read()
    print(prompt)
    executeTask(prompt)

def runUserInputLoop():
    while True:
        task = input("What would you like me to do?\n")
        executeTask(task)

answer = input("""Enter a number to run a predefined scenario or just hit enter to give me your own task:
1. generate fizzbuzz and then modify into whizzfuzz
2. extract data from a large json file
""")

match answer:
    case "1":
        runWhizzFuzz()
    case "2":
        runMagic()
    case _:
        runUserInputLoop()

