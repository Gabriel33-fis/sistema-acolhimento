import uuid
from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.domain.entities.crianca import Crianca
from app.application.interfaces.crianca_repository import CriancaRepository
from app.application.interfaces.audit_logger import AuditLogger
from app.infrastructure.security.crypto_service import CryptoService

@dataclass
class AdmitirCriancaInput:
    nome_completo: str
    data_nascimento: date
    alergias: Optional[str]
    operador_id: str
    ip_origem: str

class AdmitirCriancaUseCase:
    def __init__(
        self,
        repository: CriancaRepository,
        audit_logger: AuditLogger,
        crypto_service: Optional[CryptoService] = None
    ):
        self.repository = repository
        self.audit_logger = audit_logger
        self.crypto_service = crypto_service

    def execute(self, entrada: AdmitirCriancaInput) -> str:
        novo_id = str(uuid.uuid4())

        alergias_cifradas = None
        if entrada.alergias:
            if self.crypto_service:
                alergias_cifradas = self.crypto_service.cifrar(entrada.alergias)
            else:
                alergias_cifradas = entrada.alergias

        crianca = Crianca(
            id=novo_id,
            nome_completo=entrada.nome_completo,
            data_nascimento=entrada.data_nascimento,
            data_admissao=date.today(),
            status_acolhimento="ACOLHIDO",
            alergias_cifradas=alergias_cifradas
        )

        self.repository.salvar(crianca)

        # Registro de Auditoria
        if hasattr(self.audit_logger, "registrar"):
            self.audit_logger.registrar(
                operador_id=entrada.operador_id,
                acao="ADMISSAO_CRIANCA",
                recurso="CRIANCA",
                recurso_id=crianca.id,
                ip_origem=entrada.ip_origem,
                detalhes=f"Admissão do acolhido {crianca.nome_completo}"
            )
        elif hasattr(self.audit_logger, "registar_evento"):
            self.audit_logger.registar_evento(
                operador_id=entrada.operador_id,
                acao="ADMISSAO_CRIANCA",
                recurso_id=crianca.id,
                ip=entrada.ip_origem
            )

        return crianca.id
