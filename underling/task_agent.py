import re
from typing import List, Union

from langchain import LLMChain
from langchain.agents import load_tools, Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import StringPromptTemplate
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish

from agent_tools import exec_python_tool, execute_shell_tool, change_working_directory_tool

tools = [exec_python_tool, execute_shell_tool, change_working_directory_tool]#, help_tool]

template = """Perform the specified task. You have access to the following tools:

{tools}

Use the following format:

Task: the input task that you must complete
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times until the task is done)

Once the task appears to be done, its time to perform a verification step, following a similar format to above:

Thought: think about how you will verify the task is complete
Action: Action to take to perform the verification, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

If the observation indicates the task is not complete, resume work on the task. If the task is complete, follow this format for the final output:

Task Complete: summary of the outcome

Pay special attention to the prefixes used in various lines above. For example, "Task Complete: printed hello world" is valid, while "task complete, printed hello world" is not.

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
                return_values={"output": llm_output.split("Task Complete")[-1].strip()},
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