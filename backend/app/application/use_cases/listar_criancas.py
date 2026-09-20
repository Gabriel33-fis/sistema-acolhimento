from typing import List, Optional
from app.application.interfaces.crianca_repository import CriancaRepository
from app.application.interfaces.audit_logger import AuditLogger

class ListarCriancasUseCase:
    def __init__(self, repository: CriancaRepository, audit_logger: AuditLogger):
        self.repository = repository
        self.audit_logger = audit_logger

    def execute(self, operador_id: str, ip_origem: str, termo_busca: Optional[str] = None) -> List[dict]:
        criancas = self.repository.listar_todas(termo_busca)

        self.audit_logger.registrar(
            operador_id=operador_id,
            acao="LISTAGEM_CRIANCAS",
            recurso="CRIANCA",
            ip_origem=ip_origem,
            detalhes=f"Consulta de listagem executada. Filtro: '{termo_busca or 'Nenhum'}'. Total retornado: {len(criancas)}."
        )

        return [
            {
                "id": c.id,
                "nome_completo": c.nome_completo,
                "data_nascimento": c.data_nascimento,
                "data_admissao": c.data_admissao,
                "status_acolhimento": c.status_acolhimento,
            }
            for c in criancas
        ]
