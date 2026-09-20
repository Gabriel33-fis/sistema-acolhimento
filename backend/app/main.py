from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.presentation.api.routers import auth, criancas

app = FastAPI(
    title="Sistema de Acolhimento Institucional",
    description="API com Arquitetura Limpa, Segurança e Criptografia AES-GCM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "mensagem": "Sistema operacional"}

app.include_router(auth.router)
app.include_router(criancas.router)
