from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.database.connection import engine, Base
from app.presentation.api.routers import criancas, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Acolhimento Institucional",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(criancas.router)
