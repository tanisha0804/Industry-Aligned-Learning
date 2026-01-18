from fastapi import FastAPI
from app.api import resume, skills

app = FastAPI()

app.include_router(resume.router, prefix="/data")
app.include_router(skills.router, prefix="/skills")

@app.get("/")
def root():
    return {"message": "Backend is running"}


