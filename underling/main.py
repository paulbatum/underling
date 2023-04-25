import subprocess
import re
import os

from typing import List, Union
from langchain import LLMChain
from langchain.agents import load_tools, Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.prompts import StringPromptTemplate
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish

def executeShellCommand(command: str) -> str:
    command = command.strip().strip('`').strip().replace("\\n", "\n").replace("\\t", "\t")
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

tools = [execute_tool, change_working_directory_tool]#, help_tool]

template = """Perform the specified task. You have access to the following tools:

{tools}

Use the following format, paying special attention to the casing and punctuation used as part of the prefix for each line. For example, "Task Complete: done" is valid, while "task complete, done" is not.

Task: the input task that you must complete
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times until the task is done)
Thought: I think I have completed the task, I need to double check my work
Action: Action to take to double check the work
Action Input: the input to the action
Task Complete: I have completed the task and double checked my work

Pay attention to these important tips:
This chat session is managed by a program running in a container, as a user with limited permissions. You cannot sudo / run as root.
You can create files by piping an echo into a file. You can edit files using grep/sed/awk. Do not try to use interactive programs like nano or vi.
You have write access to the /projects directory.

Begin!
Task: {input}
{agent_scratchpad}"""

class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[BaseTool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)

prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=["input", "intermediate_steps"]
)

class CustomOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Task Complete" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Done:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

output_parser = CustomOutputParser()

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)
llm_chain = LLMChain(llm=llm, prompt=prompt)
agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=[tool.name for tool in tools]
)

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, max_iterations=10)


def runWithTokenOutput(task:str):
    with get_openai_callback() as cb:
        response = agent_executor.run(task)
        print(f"Total Tokens: {cb.total_tokens}")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion Tokens: {cb.completion_tokens}")
        print(f"Total Cost (USD): ${cb.total_cost}")

def runWhizzFuzz():
    os.chdir("/projects/whizzfuzz")
    f = 'fizzbuzz.py'
    if os.path.exists(f):
        os.remove(f)

    with open('task1.txt', 'r') as file:
        prompt = file.read()
    print(prompt)
    runWithTokenOutput(prompt)

    with open('task2.txt', 'r') as file:
        prompt = file.read()
    print(prompt)
    runWithTokenOutput(prompt)

def runUserInputLoop():
    while True:
        task = input("What would you like me to do?\n")
        with get_openai_callback() as cb:
            response = agent_executor.run(task)
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")

answer = input("Run through the whizzfuzz demo scenario? (y/n)")
if answer.lower() == 'y':
    runWhizzFuzz()
else:
    runUserInputLoop()



