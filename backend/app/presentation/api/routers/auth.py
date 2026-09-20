import uuid
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import UtilizadorModel
from app.infrastructure.security.auth_service import AuthService
from app.presentation.api.dependencies import obter_utilizador_atual

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    nome: str
    perfil: str

class CriarUtilizadorSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: Literal["COORDENADOR", "OPERADOR"]

@router.post("/login", response_model=TokenSchema)
@router.post("/login/", response_model=TokenSchema, include_in_schema=False)
def login(dados: LoginSchema, db: Session = Depends(get_db)):
    utilizador = db.query(UtilizadorModel).filter(UtilizadorModel.email == dados.email).first()
    
    if not utilizador or not AuthService.verificar_senha(dados.senha, utilizador.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas."
        )

    token = AuthService.criar_token_acesso({
        "sub": utilizador.id,
        "email": utilizador.email,
        "perfil": utilizador.perfil
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "nome": utilizador.nome,
        "perfil": utilizador.perfil
    }

@router.post("/registar", status_code=status.HTTP_201_CREATED)
def registar_utilizador(
    dados: CriarUtilizadorSchema,
    operador: dict = Depends(obter_utilizador_atual),
    db: Session = Depends(get_db)
):
    # Regra RBAC: Apenas Coordenador pode criar novas contas
    if operador.get("perfil") != "COORDENADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores/coordenadores podem registar novos utilizadores."
        )

    if len(dados.senha) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A palavra-passe deve conter no mínimo 6 caracteres."
        )

    existente = db.query(UtilizadorModel).filter(UtilizadorModel.email == dados.email).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já se encontra registado no sistema."
        )

    novo_utilizador = UtilizadorModel(
        id=str(uuid.uuid4()),
        nome=dados.nome,
        email=dados.email,
        senha_hash=AuthService.gerar_hash_senha(dados.senha),
        perfil=dados.perfil
    )

    db.add(novo_utilizador)
    db.commit()

    return {
        "mensagem": f"Utilizador {dados.nome} ({dados.perfil}) registado com sucesso!",
        "id": novo_utilizador.id
    }
