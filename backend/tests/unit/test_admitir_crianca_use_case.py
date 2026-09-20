from datetime import date
from typing import List, Optional
from app.domain.entities.crianca import Crianca
from app.application.interfaces.crianca_repository import CriancaRepository
from app.application.interfaces.audit_logger import AuditLogger
from app.application.use_cases.admitir_crianca import AdmitirCriancaUseCase, AdmitirCriancaInput

class InMemoryCriancaRepository(CriancaRepository):
    def __init__(self):
        self.criancas = {}

    def salvar(self, crianca: Crianca) -> None:
        self.criancas[crianca.id] = crianca

    def obter_por_id(self, id: str) -> Optional[Crianca]:
        return self.criancas.get(id)

    def listar_todas(self, termo_busca: Optional[str] = None) -> List[Crianca]:
        return list(self.criancas.values())

class InMemoryAuditLogger(AuditLogger):
    def __init__(self):
        self.logs = []

    def registrar(self, operador_id, acao, recurso, recurso_id=None, ip_origem=None, detalhes=None):
        self.logs.append({
            "operador_id": operador_id,
            "acao": acao,
            "recurso": recurso,
            "recurso_id": recurso_id,
            "ip_origem": ip_origem
        })

    def registar_evento(self, operador_id, acao, recurso_id=None, ip=None, detalhes=None):
        self.registrar(operador_id, acao, "SISTEMA", recurso_id, ip, detalhes)

def test_deve_admitir_crianca_e_registar_auditoria():
    repo = InMemoryCriancaRepository()
    audit = InMemoryAuditLogger()
    use_case = AdmitirCriancaUseCase(repository=repo, audit_logger=audit)

    entrada = AdmitirCriancaInput(
        nome_completo="Lucas Silva",
        data_nascimento=date(2018, 5, 10),
        alergias="Nenhuma",
        operador_id="user-123",
        ip_origem="127.0.0.1"
    )

    crianca_id = use_case.execute(entrada)

    assert crianca_id in repo.criancas
    crianca = repo.obter_por_id(crianca_id)
    assert crianca.nome_completo == "Lucas Silva"
    assert len(audit.logs) == 1
    assert audit.logs[0]["acao"] == "ADMISSAO_CRIANCA"
