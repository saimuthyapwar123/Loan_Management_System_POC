from fastapi import FastAPI
from app.routers.rag_router import router as rag_router

app = FastAPI(title= "Loan Management System")

app.include_router(rag_router)