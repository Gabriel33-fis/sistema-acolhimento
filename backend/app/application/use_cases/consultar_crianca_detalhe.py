from typing import Optional
from dataclasses import dataclass
from datetime import date
from app.application.interfaces.crianca_repository import ICriancaRepository
from app.application.interfaces.audit_logger import IAuditLogger
from app.infrastructure.security.crypto_service import CryptoService

@dataclass
class CriancaDetalheOutput:
    id: str
    nome_completo: str
    data_nascimento: date
    data_admissao: date
    status_acolhimento: str
    alergias_decifradas: Optional[str]

class ConsultarCriancaDetalheUseCase:
    def __init__(
        self,
        crianca_repository: ICriancaRepository,
        audit_logger: IAuditLogger,
        crypto_service: CryptoService
    ):
        self._repo = crianca_repository
        self._audit = audit_logger
        self._crypto = crypto_service

    def execute(self, crianca_id: str, operador_id: str, ip_origem: str) -> Optional[CriancaDetalheOutput]:
        # Busca direta no banco
        crianca = self._repo.buscar_por_id(crianca_id)
        if not crianca:
            return None

        # Busca modelo ORM direto para pegar o campo cifrado
        from app.infrastructure.database.models import CriancaModel
        session = getattr(self._repo, "_session", None)
        alergias_texto = None

        if session:
            model = session.query(CriancaModel).filter(CriancaModel.id == crianca_id).first()
            if model and model.alergias_cifradas:
                try:
                    alergias_texto = self._crypto.decrypt(model.alergias_cifradas)
                except Exception:
                    alergias_texto = "Erro ao decifrar registro médico."

        # Auditoria de acesso aos dados sensíveis
        self._audit.registar_evento(
            operador_id=operador_id,
            acao="CONSULTA_DETALHE_SAUDE",
            recurso_id=crianca_id,
            ip=ip_origem
        )

        return CriancaDetalheOutput(
            id=crianca.id,
            nome_completo=crianca.nome_completo,
            data_nascimento=crianca.data_nascimento,
            data_admissao=crianca.data_admissao,
            status_acolhimento=crianca.status_acolhimento,
            alergias_decifradas=alergias_texto
        )
