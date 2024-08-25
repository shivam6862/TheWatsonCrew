'''
These are non-leaf tools which has several leaf or non-leaf tools under them.
'''
from Intelligence.agents.agent_runner import MyAgentRunner
from Intelligence.tools.tool_instance_mappings import tool_instance_mapping as TIM
from Intelligence.utils.misc_utils import logger
from Intelligence.utils.llm_utils import llm_lc

MEDICAL_AGENT_1 = MyAgentRunner.from_tools(
                        llm = llm_lc,
                        tools = [TIM['diabetes_doctor_tool'.upper()], TIM['blood_pressure_doctor_tool'.upper()]],
                        description='''Useful for queries related to medical diagnosis, diseases, remedies and fitness and exercise. It has a staff of expertise in diabetes and blood pressure domains.''',
                        name = 'MEDICAL_AGENT', 
                        )

FINANCIAL_AGENT_1 = MyAgentRunner.from_tools(
                            llm = llm_lc,
                            tools = [TIM['finance_advisor_tool'.upper()]],
                            description="Useful for queries related to stock market, cryptocurrency, and financial literacy.",
                            name = 'FINANCIAL_AGENT', 
                        )

DATABASE_AGENT_1 = MyAgentRunner.from_tools(
                        llm = llm_lc,
                        tools = [TIM['get_similar_work_items_tool'.upper()], TIM['summarize_objects_tool'.upper()], 
                                 TIM['prioritize_objects_tool'.upper()], TIM['search_object_by_name_tool'.upper()], 
                                 TIM['create_actionable_tasks_from_text_tool'.upper()]],
                        description="For doing database operations like searching, summarizing, prioritizing, and creating actionable tasks.",
                        name = 'database_agent'.upper(), 
                        )

ROOT = MyAgentRunner.from_tools(
    llm=llm_lc , 
    tools = [MEDICAL_AGENT_1, FINANCIAL_AGENT_1],
    description="All purpose agent with a staff of expertise in medical and financial domains.",
    name = 'ROOT',
)

if __name__=='__main__':
    ROOT.input = 'What is diabetes? '
    instance_list = ROOT.dag_response()
    logger.critical(instance_list)