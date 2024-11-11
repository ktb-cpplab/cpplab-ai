# uvicorn main:app --reload
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.user_info import UserInfo
from models.project_info import RegenInfo
from services.chain_generator import create_gen_chain, create_regen_chain

# from dotenv import load_dotenv
# load_dotenv()

app = FastAPI()

origins = [
    "http://www.cpplab.store",
    "http://cpplab.store",
    "cpplab.store"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gen_chain = create_gen_chain()
regen_chain = create_regen_chain()

@app.get("/ai/health")
def health_check():
    return {"status": "healthy"}

@app.post('/ai/genproject')
def genProject(userinfo: UserInfo):
    proj = gen_chain.invoke(
        input={
            "hopeJob": userinfo.hopeJob,
            "mainStack": userinfo.mainStack,
            "educations": userinfo.educations,
            "projects": userinfo.projects,
            "prizes": userinfo.prizes,
            "activities": userinfo.activities,
            "certificates": userinfo.certificates,
            "language": "TEPS 404",
            "hopeCompany": userinfo.hopeCompany
        }
    )
    return proj

@app.post('/ai/regenproject')
def regenProject(regeninfo: RegenInfo):
    proj = regen_chain.invoke(
        input={
            'prev_project': regeninfo.prev_project,
            'level': regeninfo.level,
            'theme': regeninfo.theme,
            'domain': regeninfo.domain,
            'stacks': regeninfo.stacks
        }
    )
    return proj