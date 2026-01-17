from fastapi import FastAPI
from app.api import resume

app = FastAPI(
    title="Industry-Aligned Learning Recommendation System",
    version="0.1.0"
)

app.include_router(resume.router, prefix="/data")

@app.get("/")
def root():
    return {"message": "Backend is running"}
