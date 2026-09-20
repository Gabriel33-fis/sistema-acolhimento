import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.sql_crianca_repository import SQLCriancaRepository
from app.infrastructure.database.sql_audit_logger import SQLAuditLogger
from app.infrastructure.security.crypto_service import CryptoService
from app.application.use_cases.admitir_crianca import AdmitirCriancaUseCase, AdmitirCriancaInput
from app.application.use_cases.listar_criancas import ListarCriancasUseCase
from app.application.use_cases.consultar_crianca_detalhe import ConsultarCriancaDetalheUseCase
from app.presentation.api.schemas import CriancaEntradaSchema, CriancaRespostaSchema, CriancaDetalheSchema
from app.presentation.api.dependencies import obter_utilizador_atual

router = APIRouter(prefix="/api/v1/criancas", tags=["Crianças"])

CHAVE_PADRAO = os.getenv("CRYPTO_KEY_HEX", "00" * 32)

def obter_caso_uso_admissao(db: Session = Depends(get_db)) -> AdmitirCriancaUseCase:
    repo = SQLCriancaRepository(db)
    audit = SQLAuditLogger(db)
    crypto = CryptoService(key_hex=CHAVE_PADRAO)
    return AdmitirCriancaUseCase(repo, audit, crypto)

def obter_caso_uso_listagem(db: Session = Depends(get_db)) -> ListarCriancasUseCase:
    repo = SQLCriancaRepository(db)
    audit = SQLAuditLogger(db)
    return ListarCriancasUseCase(repo, audit)

def obter_caso_uso_detalhe(db: Session = Depends(get_db)) -> ConsultarCriancaDetalheUseCase:
    repo = SQLCriancaRepository(db)
    audit = SQLAuditLogger(db)
    crypto = CryptoService(key_hex=CHAVE_PADRAO)
    return ConsultarCriancaDetalheUseCase(repo, audit, crypto)

@router.post("/", status_code=status.HTTP_201_CREATED)
def admitir_crianca(
    payload: CriancaEntradaSchema,
    request: Request,
    operador: dict = Depends(obter_utilizador_atual),
    use_case: AdmitirCriancaUseCase = Depends(obter_caso_uso_admissao)
):
    ip_origem = request.client.host if request.client else "127.0.0.1"

    try:
        dados = AdmitirCriancaInput(
            nome_completo=payload.nome_completo,
            data_nascimento=payload.data_nascimento,
            alergias=payload.alergias,
            operador_id=operador["id"],
            ip_origem=ip_origem
        )
        crianca_id = use_case.execute(dados)
        return {"id": crianca_id, "mensagem": "Acolhido registado com sucesso"}
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

@router.get("/", response_model=List[CriancaRespostaSchema])
def listar_criancas(
    request: Request,
    busca: Optional[str] = Query(None, description="Filtro por nome do acolhido"),
    operador: dict = Depends(obter_utilizador_atual),
    use_case: ListarCriancasUseCase = Depends(obter_caso_uso_listagem)
):
    ip_origem = request.client.host if request.client else "127.0.0.1"
    return use_case.execute(operador_id=operador["id"], ip_origem=ip_origem, termo_busca=busca)

@router.get("/{crianca_id}", response_model=CriancaDetalheSchema)
def obter_detalhes_crianca(
    crianca_id: str,
    request: Request,
    operador: dict = Depends(obter_utilizador_atual),
    use_case: ConsultarCriancaDetalheUseCase = Depends(obter_caso_uso_detalhe)
):
    perfis_autorizados = ["COORDENADOR", "MEDICO"]
    if operador.get("perfil") not in perfis_autorizados:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: seu perfil não tem permissão para acessar o prontuário médico confidencial."
        )

    ip_origem = request.client.host if request.client else "127.0.0.1"
    detalhes = use_case.execute(crianca_id=crianca_id, operador_id=operador["id"], ip_origem=ip_origem)
    if not detalhes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acolhido não encontrado")
    return detalhes
