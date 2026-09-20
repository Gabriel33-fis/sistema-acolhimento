from dataclasses import dataclass
from datetime import date
import uuid
from typing import Optional
from app.domain.entities.crianca import Crianca
from app.application.interfaces.crianca_repository import ICriancaRepository
from app.application.interfaces.audit_logger import IAuditLogger
from app.infrastructure.security.crypto_service import CryptoService

@dataclass(frozen=True)
class AdmitirCriancaInput:
    nome_completo: str
    data_nascimento: date
    alergias: Optional[str]
    operador_id: str
    ip_origem: str

class AdmitirCriancaUseCase:
    def __init__(
        self,
        crianca_repository: ICriancaRepository,
        audit_logger: IAuditLogger,
        crypto_service: CryptoService
    ):
        self._repo = crianca_repository
        self._audit = audit_logger
        self._crypto = crypto_service

    def execute(self, entrada: AdmitirCriancaInput) -> str:
        novo_id = str(uuid.uuid4())
        
        crianca = Crianca(
            id=novo_id,
            nome_completo=entrada.nome_completo,
            data_nascimento=entrada.data_nascimento,
            data_admissao=date.today(),
            alergias=entrada.alergias
        )
        
        alergias_cifradas = None
        if crianca.alergias:
            alergias_cifradas = self._crypto.encrypt(crianca.alergias)
            
        self._repo.salvar(crianca=crianca, alergias_cifradas=alergias_cifradas)
        
        self._audit.registar_evento(
            operador_id=entrada.operador_id,
            acao="ADMISSAO_CRIANCA",
            recurso_id=crianca.id,
            ip=entrada.ip_origem
        )
        
        return crianca.id
