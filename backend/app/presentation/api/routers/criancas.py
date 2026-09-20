import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.sql_crianca_repository import SQLCriancaRepository
from app.infrastructure.database.sql_evolucao_repository import SQLEvolucaoRepository
from app.infrastructure.database.sql_audit_logger import SQLAuditLogger
from app.infrastructure.security.crypto_service import CryptoService

from app.application.use_cases.admitir_crianca import AdmitirCriancaUseCase, AdmitirCriancaInput
from app.application.use_cases.listar_criancas import ListarCriancasUseCase
from app.application.use_cases.consultar_crianca_detalhe import ConsultarCriancaDetalheUseCase
from app.application.use_cases.desacolher_crianca import DesacolherCriancaUseCase, DesacolherCriancaInput
from app.application.use_cases.adicionar_evolucao import AdicionarEvolucaoUseCase, AdicionarEvolucaoInput
from app.application.use_cases.listar_evolucoes import ListarEvolucoesUseCase
from app.application.use_cases.atualizar_crianca import AtualizarCriancaUseCase, AtualizarCriancaInput

from app.presentation.api.schemas import (
    CriancaEntradaSchema, 
    CriancaRespostaSchema, 
    CriancaDetalheSchema,
    DesligamentoEntradaSchema,
    EvolucaoEntradaSchema,
    EvolucaoRespostaSchema
)
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

def obter_caso_uso_desligamento(db: Session = Depends(get_db)) -> DesacolherCriancaUseCase:
    repo = SQLCriancaRepository(db)
    audit = SQLAuditLogger(db)
    return DesacolherCriancaUseCase(repo, audit)

def obter_caso_uso_adicionar_evolucao(db: Session = Depends(get_db)) -> AdicionarEvolucaoUseCase:
    evolucao_repo = SQLEvolucaoRepository(db)
    crianca_repo = SQLCriancaRepository(db)
    audit = SQLAuditLogger(db)
    crypto = CryptoService(key_hex=CHAVE_PADRAO)
    return AdicionarEvolucaoUseCase(evolucao_repo, crianca_repo, audit, crypto)

def obter_caso_uso_listar_evolucoes(db: Session = Depends(get_db)) -> ListarEvolucoesUseCase:
    evolucao_repo = SQLEvolucaoRepository(db)
    crypto = CryptoService(key_hex=CHAVE_PADRAO)
    return ListarEvolucoesUseCase(evolucao_repo, crypto)

def obter_caso_uso_atualizar(db: Session = Depends(get_db)) -> AtualizarCriancaUseCase:
    repo = SQLCriancaRepository(db)
    audit = SQLAuditLogger(db)
    crypto = CryptoService(key_hex=CHAVE_PADRAO)
    return AtualizarCriancaUseCase(repo, audit, crypto)

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

@router.put("/{crianca_id}", status_code=status.HTTP_200_OK)
def atualizar_crianca(
    crianca_id: str,
    payload: CriancaEntradaSchema,
    request: Request,
    operador: dict = Depends(obter_utilizador_atual),
    use_case: AtualizarCriancaUseCase = Depends(obter_caso_uso_atualizar)
):
    if operador.get("perfil") != "COORDENADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas coordenadores podem editar dados cadastrais de acolhidos."
        )

    ip_origem = request.client.host if request.client else "127.0.0.1"
    try:
        dados = AtualizarCriancaInput(
            crianca_id=crianca_id,
            nome_completo=payload.nome_completo,
            data_nascimento=payload.data_nascimento,
            alergias=payload.alergias,
            operador_id=operador["id"],
            ip_origem=ip_origem
        )
        use_case.execute(dados)
        return {"mensagem": "Dados cadastrais atualizados com sucesso!"}
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

@router.post("/{crianca_id}/desligamento", status_code=status.HTTP_200_OK)
def desligar_crianca(
    crianca_id: str,
    payload: DesligamentoEntradaSchema,
    request: Request,
    operador: dict = Depends(obter_utilizador_atual),
    use_case: DesacolherCriancaUseCase = Depends(obter_caso_uso_desligamento)
):
    if operador.get("perfil") != "COORDENADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas coordenadores podem registrar o desligamento de acolhidos."
        )

    ip_origem = request.client.host if request.client else "127.0.0.1"
    try:
        dados = DesacolherCriancaInput(
            crianca_id=crianca_id,
            data_desligamento=payload.data_desligamento,
            motivo=payload.motivo,
            destino=payload.destino,
            operador_id=operador["id"],
            ip_origem=ip_origem
        )
        use_case.execute(dados)
        return {"mensagem": "Desligamento registrado com sucesso!"}
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

@router.post("/{crianca_id}/evolucoes", status_code=status.HTTP_201_CREATED)
def adicionar_evolucao(
    crianca_id: str,
    payload: EvolucaoEntradaSchema,
    request: Request,
    operador: dict = Depends(obter_utilizador_atual),
    use_case: AdicionarEvolucaoUseCase = Depends(obter_caso_uso_adicionar_evolucao)
):
    ip_origem = request.client.host if request.client else "127.0.0.1"
    try:
        evolucao_id = use_case.execute(
            AdicionarEvolucaoInput(
                crianca_id=crianca_id,
                autor_id=operador["id"],
                autor_nome=operador.get("nome", "Operador"),
                tipo=payload.tipo,
                texto=payload.texto,
                ip_origem=ip_origem
            )
        )
        return {"id": evolucao_id, "mensagem": "Evolução adicionada com sucesso!"}
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

@router.get("/{crianca_id}/evolucoes", response_model=List[EvolucaoRespostaSchema])
def listar_evolucoes(
    crianca_id: str,
    operador: dict = Depends(obter_utilizador_atual),
    use_case: ListarEvolucoesUseCase = Depends(obter_caso_uso_listar_evolucoes)
):
    return use_case.execute(crianca_id=crianca_id, perfil_operador=operador.get("perfil", "OPERADOR"))
