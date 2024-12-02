from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain import hub
from models.project_info import Project, Jobposting

# 채용공고 요약 chain
def jobposting_summary_chain():
    gen_summary = hub.pull("gen_summary")
    gen_llm = ChatOpenAI(model="gpt-4o-mini")
    parser = JsonOutputParser(pydantic_object=Jobposting)
    gen_summary = gen_summary.partial(format_instructions=parser.get_format_instructions())
    return gen_summary | gen_llm | parser

# 프로젝트 생성 chain
def create_gen_chain():
    gen_prompt = hub.pull("gen_prompt")
    gen_llm = ChatOpenAI(model="gpt-4o-mini")
    parser = JsonOutputParser(pydantic_object=Project)
    gen_prompt = gen_prompt.partial(format_instructions=parser.get_format_instructions())
    return gen_prompt | gen_llm | parser

# 프로젝트 재생성 chain
def create_regen_chain():
    regen_prompt = hub.pull("regen_prompt")
    regen_llm = ChatOpenAI(model="gpt-4o-mini")
    parser = JsonOutputParser(pydantic_object=Project)
    regen_prompt = regen_prompt.partial(format_instructions=parser.get_format_instructions())
    return regen_prompt | regen_llm | parser