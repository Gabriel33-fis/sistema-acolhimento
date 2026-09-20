from typing import Optional
from dataclasses import dataclass
from datetime import date
from app.application.interfaces.crianca_repository import CriancaRepository
from app.application.interfaces.audit_logger import AuditLogger
from app.infrastructure.security.crypto_service import CryptoService

@dataclass
class CriancaDetalheOutput:
    id: str
    nome_completo: str
    data_nascimento: date
    data_admissao: date
    status_acolhimento: str
    alergias_decifradas: Optional[str] = None
    data_desligamento: Optional[date] = None
    motivo_desligamento: Optional[str] = None
    destino_desligamento: Optional[str] = None

class ConsultarCriancaDetalheUseCase:
    def __init__(self, repository: CriancaRepository, audit_logger: AuditLogger, crypto_service: CryptoService):
        self.repository = repository
        self.audit_logger = audit_logger
        self.crypto_service = crypto_service

    def execute(self, crianca_id: str, operador_id: str, ip_origem: str) -> Optional[CriancaDetalheOutput]:
        crianca = self.repository.obter_por_id(crianca_id)
        if not crianca:
            return None

        alergias = None
        if crianca.alergias_cifradas:
            alergias = self.crypto_service.decifrar(crianca.alergias_cifradas)

        self.audit_logger.registrar(
            operador_id=operador_id,
            acao="CONSULTA_DETALHE_PRONTUARIO",
            recurso="CRIANCA",
            recurso_id=crianca.id,
            ip_origem=ip_origem,
            detalhes="Consulta ao prontuário médico sensível (dados decifrados)."
        )

        return CriancaDetalheOutput(
            id=crianca.id,
            nome_completo=crianca.nome_completo,
            data_nascimento=crianca.data_nascimento,
            data_admissao=crianca.data_admissao,
            status_acolhimento=crianca.status_acolhimento,
            alergias_decifradas=alergias,
            data_desligamento=crianca.data_desligamento,
            motivo_desligamento=crianca.motivo_desligamento,
            destino_desligamento=crianca.destino_desligamento
        )
