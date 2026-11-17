from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.database.connection import engine, Base
import app.infrastructure.database.models  # Garante o registro de todos os modelos no SQLAlchemy
import app.infrastructure.database.seed_users as seed_users

from app.presentation.api.routers import auth, criancas
from app.version import APP_VERSION, info_versao


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Cria todas as tabelas no SQLite se não existirem
    Base.metadata.create_all(bind=engine)
    
    # 2. Executa a rotina de seed de utilizadores
    try:
        if hasattr(seed_users, "criar_utilizadores"):
            seed_users.criar_utilizadores()
        elif hasattr(seed_users, "seed"):
            seed_users.seed()
        print("[DATABASE] Inicialização de tabelas e seed concluída com sucesso.")
    except Exception as exc:
        print(f"[DATABASE] Aviso durante a execução do seed: {exc}")
        
    yield


app = FastAPI(
    title="Sistema de Acolhimento Institucional",
    description="API com Arquitetura Limpa, Segurança e Criptografia AES-GCM",
    version=APP_VERSION,
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
    return {"status": "ok", "mensagem": "Sistema operacional", **info_versao()}


@app.get("/api/v1/versao", tags=["Health"])
def versao():
    """Versão em execução (mesma informação exibida na tela de login)."""
    return info_versao()

app.include_router(auth.router)
app.include_router(criancas.router)