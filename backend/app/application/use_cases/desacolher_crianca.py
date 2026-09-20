from dataclasses import dataclass
from datetime import date
from app.application.interfaces.crianca_repository import CriancaRepository
from app.application.interfaces.audit_logger import AuditLogger

@dataclass
class DesacolherCriancaInput:
    crianca_id: str
    data_desligamento: date
    motivo: str
    destino: str
    operador_id: str
    ip_origem: str

class DesacolherCriancaUseCase:
    def __init__(self, repository: CriancaRepository, audit_logger: AuditLogger):
        self.repository = repository
        self.audit_logger = audit_logger

    def execute(self, dados: DesacolherCriancaInput) -> None:
        crianca = self.repository.obter_por_id(dados.crianca_id)
        if not crianca:
            raise ValueError("Acolhido não encontrado.")

        crianca.desacolher(
            data_saida=dados.data_desligamento,
            motivo=dados.motivo,
            destino=dados.destino
        )

        self.repository.salvar(crianca)

        self.audit_logger.registrar(
            operador_id=dados.operador_id,
            acao="DESACOLHIMENTO",
            recurso="CRIANCA",
            recurso_id=crianca.id,
            ip_origem=dados.ip_origem,
            detalhes=f"Desligamento realizado. Motivo: {dados.motivo}. Destino: {dados.destino}."
        )
