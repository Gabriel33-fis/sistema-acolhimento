from dataclasses import dataclass
from datetime import date
from typing import Optional
from app.application.interfaces.crianca_repository import CriancaRepository
from app.application.interfaces.audit_logger import AuditLogger
from app.infrastructure.security.crypto_service import CryptoService

@dataclass
class AtualizarCriancaInput:
    crianca_id: str
    nome_completo: str
    data_nascimento: date
    alergias: Optional[str]
    operador_id: str
    ip_origem: str

class AtualizarCriancaUseCase:
    def __init__(
        self, 
        repository: CriancaRepository, 
        audit_logger: AuditLogger, 
        crypto_service: CryptoService
    ):
        self.repository = repository
        self.audit_logger = audit_logger
        self.crypto_service = crypto_service

    def execute(self, dados: AtualizarCriancaInput) -> None:
        crianca = self.repository.obter_por_id(dados.crianca_id)
        if not crianca:
            raise ValueError("Acolhido não encontrado.")

        # Cifra os dados médicos se informados
        alergias_cifradas = None
        if dados.alergias and dados.alergias.strip():
            alergias_cifradas = self.crypto_service.cifrar(dados.alergias.strip())

        crianca.atualizar_dados(
            novo_nome=dados.nome_completo,
            nova_data_nascimento=dados.data_nascimento,
            novas_alergias_cifradas=alergias_cifradas
        )

        self.repository.salvar(crianca)

        self.audit_logger.registrar(
            operador_id=dados.operador_id,
            acao="ATUALIZAR_CRIANCA",
            recurso="CRIANCA",
            recurso_id=crianca.id,
            ip_origem=dados.ip_origem,
            detalhes=f"Cadastro de {crianca.nome_completo} atualizado."
        )
