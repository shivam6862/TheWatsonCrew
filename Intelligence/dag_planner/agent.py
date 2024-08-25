from typing import List, Optional, Sequence, Any
from langchain.callbacks.base import BaseCallbackManager
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.mrkl.prompt import SUFFIX
from langchain.prompts import PromptTemplate
from langchain.tools.base import BaseTool
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.agent import  AgentOutputParser
from Intelligence.dag_planner.templates_prompts import PREFIX, FORMAT_INSTRUCTIONS, SUFFIX, FORMAT_INSTRUCTIONS_DAG
from langchain.chains.llm import LLMChain
from Intelligence.utils.llm_utils import llm
from Intelligence.utils.misc_utils import logger

template = '''
Below are the tools in your toolkit along with their descriptions to help you decide on tool choice.

MEDICAL_AGENT: Useful for queries related to medical diagnosis, diseases, remedies, and fitness and exercise. It has expertise in diabetes and blood pressure domains.
FINANCIAL_AGENT: Useful for queries related to the stock market, cryptocurrency, and financial literacy.

Use the following format:

Question    : The query to be answered.
Thought     : Based on the scratchpad, just tell the logic for the next step to be taken.
Action      : The action to take, should be one of [MEDICAL_AGENT, FINANCIAL_AGENT]
Action Input: The input to the action, pass in the query in natural language, representing the subtask to be performed by the picked tool.
Observation : $$PREV[i], representing the output of the ith action, believe that $$PREV[i] answers the ith action input.
    
...(this Thought/Action/Action Input/Observation can repeat N times)

Final Thought: Review the sequence of actions to ensure they correctly represent the steps needed to answer the question. Do not conclude the answer.
------------------------------------------------------------

Your task is to only plan the very next step based on the Question, Tools, and agent scratchpad. Do not answer the question or generate the full plan in one go. Only provide the next Thought, Action, Action Input, and Observation based on the context provided.

Begin!

Question : {input}

Steps Taken: {agent_scratchpad}

Next Step:


'''
class PersonalAgent(ZeroShotAgent):
    

    @classmethod
    def create_prompt(
        cls,
        
        tools: Sequence[BaseTool] ,
        user_query: str =None ,
        prefix: str = PREFIX,
        suffix: str = SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS_DAG,
        input_variables: Optional[List[str]] = None,
    ) -> PromptTemplate:

        tool_strings = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
        tool_names = ", ".join([tool.name for tool in tools])
        format_instructions = format_instructions.format(tool_names=tool_names, user_query=user_query)
        #________________________________________________________________________________

        template = "\n\n".join([prefix, tool_strings, format_instructions,  suffix])    # mistakes

        if input_variables is None:
            input_variables = ["input", "agent_scratchpad"]
        
        prompt =  PromptTemplate(template=template, input_variables=input_variables)
           
        return prompt
    #________________________________________________________________________________________________________________________________
    @classmethod
    def from_llm_and_tools(
        cls,
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool],
        user_query: str = None,
        callback_manager: Optional[BaseCallbackManager] = None,
        output_parser: Optional[AgentOutputParser] = None,
        prefix: str = PREFIX,
        suffix: str = SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> 'PersonalAgent':
        """Construct an agent from an LLM and tools."""
        cls._validate_tools(tools)

        prompt = cls.create_prompt(
            tools=tools,
            prefix=prefix,
            user_query=user_query,
            suffix=suffix,
            format_instructions=format_instructions,
            input_variables=input_variables,
        )
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            callback_manager=callback_manager,
        )
        tool_names = [tool.name for tool in tools]
        _output_parser = output_parser or cls._get_default_output_parser()

        return cls(
            llm_chain=llm_chain,
            allowed_tools=tool_names,
            output_parser=_output_parser,
            **kwargs,
        )   