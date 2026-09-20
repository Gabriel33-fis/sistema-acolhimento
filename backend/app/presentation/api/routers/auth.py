import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import UtilizadorModel
from app.infrastructure.security.auth_service import AuthService
from app.presentation.api.dependencies import obter_utilizador_atual

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])

class LoginInput(BaseModel):
    email: EmailStr
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    nome: str
    perfil: str

class RegistarUtilizadorInput(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: str = "OPERADOR"

class UtilizadorResponse(BaseModel):
    id: str
    nome: str
    email: str
    perfil: str

class AlterarPerfilInput(BaseModel):
    perfil: str

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginInput, db: Session = Depends(get_db)):
    usuario = db.query(UtilizadorModel).filter(UtilizadorModel.email == payload.email).first()
    if not usuario or not AuthService.verificar_senha(payload.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas."
        )

    # Gera o token JWT
    gerador = getattr(AuthService, "criar_token_acesso", getattr(AuthService, "gerar_token_acesso", None))
    token = gerador(
        payload={
            "sub": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": usuario.perfil
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "nome": usuario.nome,
        "perfil": usuario.perfil
    }

@router.post("/registar", status_code=status.HTTP_201_CREATED)
def registar(
    payload: RegistarUtilizadorInput,
    db: Session = Depends(get_db),
    operador: dict = Depends(obter_utilizador_atual)
):
    if operador.get("perfil") != "COORDENADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas coordenadores podem registar novos utilizadores."
        )

    existente = db.query(UtilizadorModel).filter(UtilizadorModel.email == payload.email).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um utilizador registado com este e-mail."
        )

    novo_usuario = UtilizadorModel(
        id=str(uuid.uuid4()),
        nome=payload.nome,
        email=payload.email,
        senha_hash=AuthService.gerar_hash_senha(payload.senha),
        perfil=payload.perfil.upper()
    )
    db.add(novo_usuario)
    db.commit()

    return {"mensagem": "Utilizador registado com sucesso!", "id": novo_usuario.id}

@router.get("/utilizadores", response_model=List[UtilizadorResponse])
def listar_utilizadores(
    db: Session = Depends(get_db),
    operador: dict = Depends(obter_utilizador_atual)
):
    if operador.get("perfil") != "COORDENADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas coordenadores podem listar a equipe."
        )
    return db.query(UtilizadorModel).order_by(UtilizadorModel.nome.asc()).all()

@router.patch("/utilizadores/{utilizador_id}/perfil", status_code=status.HTTP_200_OK)
def alterar_perfil_utilizador(
    utilizador_id: str,
    payload: AlterarPerfilInput,
    db: Session = Depends(get_db),
    operador: dict = Depends(obter_utilizador_atual)
):
    if operador.get("perfil") != "COORDENADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas coordenadores podem alterar perfis."
        )

    alvo = db.query(UtilizadorModel).filter(UtilizadorModel.id == utilizador_id).first()
    if not alvo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não encontrado.")

    novo_perfil = payload.perfil.upper().strip()
    if novo_perfil not in ("COORDENADOR", "OPERADOR"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Perfil inválido.")

    alvo.perfil = novo_perfil
    db.commit()
    return {"mensagem": f"Perfil de {alvo.nome} atualizado para {novo_perfil} com sucesso!"}
