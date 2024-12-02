from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain import hub

from models.project_info import Project

# 공통 json parser
parser = JsonOutputParser(pydantic_object=Project)

# 프로젝트 생성 chain
def create_gen_chain():
    gen_prompt = hub.pull("gen_prompt")
    gen_llm = ChatOpenAI(model="gpt-4o-mini")
    gen_prompt = gen_prompt.partial(format_instructions=parser.get_format_instructions())
    return gen_prompt | gen_llm | parser

# 프로젝트 재생성 chain
def create_regen_chain():
    regen_prompt = hub.pull("regen_prompt")
    regen_llm = ChatOpenAI(model="gpt-4o-mini")
    regen_prompt = regen_prompt.partial(format_instructions=parser.get_format_instructions())
    return regen_prompt | regen_llm | parser