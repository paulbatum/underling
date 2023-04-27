import os
import subprocess
import traceback
from io import StringIO
from contextlib import redirect_stdout
from langchain.agents import load_tools, Tool

def execPythonCommand(command: str) -> str:
    command = command.strip().strip('`').strip().replace("\\n", "\n")
    outString = StringIO()
    with redirect_stdout(outString):
        try:
            exec(command)
            result = outString.getvalue()
        except Exception:
            print(traceback.format_exc())
    output = outString.getvalue()
    output = "Error, output exceeded maximum allowable length." if len(output) > 1000 else output
    return output

exec_python_tool = Tool(
    name = "Execute Python Code",
    func = execPythonCommand,
    description = "Does an exec of the specified python code and returns the output. Input must be valid python."
)

def executeShellCommand(command: str) -> str:
    command = command.strip().strip('`').strip().replace("\\n", "\n").replace("\\t", "\t")
    print("\n> " + command)
    output=""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        output += result.stdout
    else:
        output += result.stdout + "\n" + result.stderr

    output = "Error, output exceeded maximum allowable length." if len(output) > 1000 else output
    return output

execute_shell_tool = Tool(
    name = "Execute Shell Command",
    func = executeShellCommand,
    description = """
        Executes the specified bash command and outputs stdout/stderr.
        Use this to interact with the environment, e.g. `cat readme.txt` to inspect a file.
        Input string must be a syntactically valid command.
        """
)

def helpCommand(command:str) -> str:
    answer = input("\n" + command)
    return answer

help_tool = Tool(
    name = "Help",
    func = helpCommand,
    description= "Asks the human operator for advice or suggestions. The input should be a question or a description of a problem."
)

def changeWorkingDirectory(dirname:str):
    dirname=dirname.lstrip('cd').strip()
    if os.path.exists(dirname):
        os.chdir(dirname)
    else:
        return "Error - could not find the specified path. Consider trying again using an absolute path."

change_working_directory_tool = Tool(
    name = "Change Working Directory",
    func = changeWorkingDirectory,
    description = "Changes the current working directory. Input should be an absolute path."
)