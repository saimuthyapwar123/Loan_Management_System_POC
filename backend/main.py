from fastapi import FastAPI
from console_code.app.routers.auth_router import router as auth_router
from console_code.app.routers.loan_router import router as loan_router
from console_code.app.routers.loan_data_list import router as loan_data_list

from ai_chatbot.app.routers.lc_router import router as lc_router
from ai_chatbot.app.routers.rag_router import router as rag_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title= "Loan Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in prodz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(auth_router)
app.include_router(loan_router)
app.include_router(loan_data_list)
app.include_router(lc_router)
app.include_router(rag_router)