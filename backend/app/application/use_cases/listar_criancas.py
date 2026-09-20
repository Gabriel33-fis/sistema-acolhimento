from typing import List, Optional
from app.domain.entities.crianca import Crianca
from app.application.interfaces.crianca_repository import ICriancaRepository
from app.application.interfaces.audit_logger import IAuditLogger

class ListarCriancasUseCase:
    def __init__(self, crianca_repository: ICriancaRepository, audit_logger: IAuditLogger):
        self._repo = crianca_repository
        self._audit = audit_logger

    def execute(self, operador_id: str, ip_origem: str, termo_busca: Optional[str] = None) -> List[Crianca]:
        resultado = self._repo.listar(termo_busca=termo_busca)
        
        self._audit.registar_evento(
            operador_id=operador_id,
            acao="LISTAGEM_CRIANCAS",
            recurso_id="ALL",
            ip=ip_origem
        )
        return resultado
