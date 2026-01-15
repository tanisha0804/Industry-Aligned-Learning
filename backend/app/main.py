# backend/app/main.py

from fastapi import FastAPI

app = FastAPI(title="Industry-Aligned Learning System")

@app.get("/")
def root():
    return {"message": "Backend is running"}
