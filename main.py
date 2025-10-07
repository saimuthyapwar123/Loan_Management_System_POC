from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.routers.loan_router import router as loan_router

app = FastAPI(title= "Loan Management System")

app.include_router(auth_router)
app.include_router(loan_router)