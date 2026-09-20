from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.database.connection import engine, Base
import app.infrastructure.database.models  # Garante o registro de todos os modelos no SQLAlchemy
import app.infrastructure.database.seed_users as seed_users

from app.presentation.api.routers import auth, criancas


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Cria todas as tabelas no SQLite se não existirem
    Base.metadata.create_all(bind=engine)
    
    # 2. Executa a rotina de seed de usuários iniciais
    try:
        if hasattr(seed_users, "seed"):
            seed_users.seed()
        elif hasattr(seed_users, "main"):
            seed_users.main()
        elif hasattr(seed_users, "seed_users"):
            seed_users.seed_users()
        print("[DATABASE] Inicialização de tabelas e seed concluída com sucesso.")
    except Exception as exc:
        print(f"[DATABASE] Aviso durante a execução do seed: {exc}")
        
    yield  # API em execução atendendo requisições


app = FastAPI(
    title="Sistema de Acolhimento Institucional",
    description="API com Arquitetura Limpa, Segurança e Criptografia AES-GCM",
    version="1.0.0",
    lifespan=lifespan
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