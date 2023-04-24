import subprocess

from langchain.agents import load_tools
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback

def executeShellCommand(command: str) -> str:
    print("\n> " + command)
    output=""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        output += result.stdout
    else:
        output += result.stdout + "\n" + result.stderr
    return output

execute_tool = Tool(
    name = "Execute",
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

tools = [execute_tool, help_tool]

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)
agent = initialize_agent(tools, llm,agent="zero-shot-react-description", verbose=True, max_iterations=10)

intro = """
This chat session is managed by a program running in a container.
You can interact with the environment using the execute tool.
You can create files by piping an echo into a file.
You can edit files using grep/sed/awk.
If you are stuck, you can ask the human operator for help using the help tool.
"""
question1 = intro + "Read task1.txt and follow the instructions. Once complete, do the same for task2.txt."

with get_openai_callback() as cb:
    response = agent.run(question1)
    print(f"Total Tokens: {cb.total_tokens}")
    print(f"Prompt Tokens: {cb.prompt_tokens}")
    print(f"Completion Tokens: {cb.completion_tokens}")
    print(f"Total Cost (USD): ${cb.total_cost}")